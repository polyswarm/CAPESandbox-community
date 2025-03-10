# Copyright (C) 2014 Optiv, Inc. (brad.spengler@optiv.com)
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

from lib.cuckoo.common.abstracts import Signature


class EmailStealer(Signature):
    name = "infostealer_mail"
    description = "Harvests information related to installed mail clients"
    severity = 3
    categories = ["infostealer"]
    authors = ["Optiv"]
    minimum = "1.2"
    ttps = ["T1081"]  # MITRE v6
    ttps += ["T1003", "T1005", "T1114"]  # MITRE v6,7,8
    ttps += ["T1552", "T1552.001", "T1114.01"]  # MITRE v7,8
    mbcs = ["OC0003", "OC0005"]

    def run(self):
        office_pkgs = ["ppt", "doc", "xls", "eml"]
        if any(e in self.results["info"]["package"] for e in office_pkgs):
            return False

        file_indicators = (
            ".*\.pst$",
            r".*\\Microsoft\\Windows\\ Live\\ Mail.*",
            r".*\\Microsoft\\Address\\ Book\\.*\.wab$",
            r".*\\Microsoft\\Outlook\\ Express\\.*\.dbx$",
            r".*\\Foxmail\\mail\\.*\\Account\.stg$",
            r".*\\Foxmail.*\\Accounts\.tdat$",
            r".*\\Thunderbird\\Profiles\\.*\.default$",
            r".*\\AppData\\Roaming\\Thunderbird\\profiles.ini$",
        )
        registry_indicators = [
            r".*\\Microsoft\\Windows\\ Messaging\\ Subsystem\\MSMapiApps.*",
            r".*\\Microsoft\\Windows\\ Messaging\\ Subsystem\\Profiles.*",
            r".*\\Microsoft\\Windows\\ NT\\CurrentVersion\\Windows\\ Messaging\\ Subsystem\\Profiles.*",
            r".*\\Microsoft\\Office\\.*\\Outlook\\Profiles\\Outlook.*",
            r".*\\Microsoft\\Office\\Outlook\\OMI\\ Account\\ Manager\\Accounts.*",
            r".*\\Microsoft\\Internet\\ Account\\ Manager\\Accounts.*",
            r".*\\Software\\(Wow6432Node\\)?IncrediMail.*" r".*\\Software\\(Wow6432Node\\)?Microsoft\\Windows\\ Live\\ Mail.*",
        ]
        if self.results.get("target", {}).get("category", "") == "file":
            registry_indicators.append(r".*\\Software\\(Wow6432Node\\)?Clients\\Mail.*")

        found_stealer = False
        for indicator in file_indicators:
            file_match = self.check_file(pattern=indicator, regex=True, all=True)
            if file_match:
                for match in file_match:
                    self.data.append({"file": match})
                found_stealer = True
        for indicator in registry_indicators:
            key_match = self.check_key(pattern=indicator, regex=True, all=True)
            if key_match:
                for match in key_match:
                    self.data.append({"regkey": match})
                found_stealer = True
        return found_stealer
