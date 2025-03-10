# Copyright (C) 2016 Brad Spengler, 2019 Kevin Ross
# This file is part of Cuckoo Sandbox - http://www.cuckoosandbox.org
# See the file 'docs/LICENSE' for copying permission.

import re

from lib.cuckoo.common.abstracts import Signature


class DisablesWindowsDefender(Signature):
    name = "disables_windows_defender"
    description = "Attempts to disable Windows Defender"
    severity = 3
    categories = ["anti-av"]
    authors = ["Brad Spengler", "Kevin Ross", "ditekshen"]
    minimum = "1.2"
    ttps = ["T1089"]  # MITRE v6
    ttps += ["T1562", "T1562.001"]  # MITRE v7,8
    mbcs = ["OB0006", "F0004"]

    def run(self):
        ret = False

        keys = (
            r".*\\SOFTWARE\\(Wow6432Node\\)?Windows\\ Defender\\.*",
            r".*\\SOFTWARE\\(Wow6432Node\\)?Policies\\Microsoft\\Windows\\ Defender\\.*",
            r".*\\SYSTEM\\(CurrentControlSet|ControlSet001)\\services\\WinDefend\\.*",
        )

        cmds = [
            "disableantispyware",
            "disableantivirus",
            "disablearchivescanning",
            "disablebehaviormonitoring",
            "disableblockatfirstseen",
            "disablecatchupfullscan",
            "disablecatchupquickscan",
            "disablecputhrottleonidlescans",
            "disableemailscanning",
            "disableenhancednotification",
            "disableintrusionpreventionsystem",
            "disableioavprotection",
            "disableonaccessprotection",
            "disableprivacymode",
            "disablerealtimemonitoring",
            "disablerestorepoint",
            "disableroutinelytakingaction",
            "disablescanningmappednetworkdrivesforfullscan",
            "disablescanningnetworkfiles",
            "disablescanonrealtimeenable",
            "disablescriptscanning",
            "lowthreatdefaultaction",
            "moderatethreatdefaultaction",
            "mpenablepus",
            "severethreatdefaultaction",
            "tamperprotection",
        ]

        for check in keys:
            match = self.check_write_key(pattern=check, regex=True)
            if match:
                self.data.append({"regkey": match})
                ret = True
                self.ttps += ["T1112"]  # MITRE v6,7,8
                self.mbcs += ["OB0006", "E1112"]
                self.mbcs += ["OC0008", "C0036"]  # micro-behaviour

        cmdlines = self.results["behavior"]["summary"]["executed_commands"]
        for cmdline in cmdlines:
            lower = cmdline.lower()
            for cmd in cmds:
                if cmd in lower or (
                    "sc" in lower and ("stop" in lower or "delete" in lower or "disabled" in lower) and "windefend" in lower
                ):
                    self.data.append({"command": cmdline})
                    ret = True
                    self.ttps += ["T1059"]  # MITRE v6,7,8
                    self.mbcs += ["OB0009", "E1059"]
                    break

        return ret


class WindowsDefenderPowerShell(Signature):
    name = "windows_defender_powershell"
    description = "Attempts to modify Windows Defender using PowerShell"
    severity = 3
    categories = ["anti-av"]
    authors = ["Kevin Ross"]
    minimum = "1.2"
    ttps = ["T1089"]  # MITRE v6
    ttps += ["T1059"]  # MITRE v6,7,8
    ttps += ["T1059.001", "T1562", "T1562.001"]  # MITRE v7,8
    mbcs = ["OB0006", "F0004", "OB0009", "E1059"]

    def run(self):
        ret = False
        cmdlines = self.results["behavior"]["summary"]["executed_commands"]
        for cmdline in cmdlines:
            lower = cmdline.lower()
            if "set-mppreference" in lower:
                self.data.append({"command": cmdline})
                ret = True
            if "add-mppreference" in lower and "exclusionpath" in lower:
                self.data.append({"command": cmdline})
                ret = True

        return ret


class RemovesWindowsDefenderContextMenu(Signature):
    name = "removes_windows_defender_contextmenu"
    description = "Attempts to remove Windows Defender from context menu"
    severity = 3
    categories = ["anti-av"]
    authors = ["ditekshen"]
    minimum = "1.3"
    ttps = ["T1089"]  # MITRE v6
    ttps += ["T1112"]  # MITRE v6,7,8
    ttps += ["T1562", "T1562.001"]  # MITRE v7,8
    mbcs = ["OB0006", "E1112", "F0004"]
    mbcs += ["OC0008", "C0036"]  # micro-behaviour

    def run(self):
        indicators = (
            r"HKEY_CLASSES_ROOT\\\*\\shellex\\ContextMenuHandlers\\EPP$",
            r"HKEY_CLASSES_ROOT\\Directory\\shellex\\ContextMenuHandlers\\EPP$",
            r"HKEY_CLASSES_ROOT\\Drive\\shellex\\ContextMenuHandlers\\EPP$",
        )
        pat = re.compile(r".*\\shellex\\contextmenuhandlers\\epp")

        for indicator in indicators:
            match = self.check_write_key(pattern=indicator, regex=True)
            if match:
                return True

        cmdlines = self.results["behavior"]["summary"]["executed_commands"]
        for cmdline in cmdlines:
            lower = cmdline.lower()
            if re.search(pat, lower):
                self.data.append({"command": cmdline})
                return True

        return False


class DisablesWindowsDefenderLogging(Signature):
    name = "disables_windows_defender_logging"
    description = "Attempts to disable Windows Defender logging"
    severity = 3
    categories = ["anti-av"]
    authors = ["ditekshen"]
    minimum = "1.3"
    ttps = ["T1089"]  # MITRE v6
    ttps += ["T1112"]  # MITRE v6,7,8
    ttps += ["T1562", "T1562.001"]  # MITRE v7,8
    mbcs = ["OB0006", "E1112", "F0004"]
    mbcs += ["OC0008", "C0036"]  # micro-behaviour

    def run(self):
        indicators = (r".*\\System\\CurrentControlSet\\Control\\WMI\\Autologger\\Defender(Api|Audit)Logger",)
        pat = re.compile(r".*\\system\\currentcontrolset\\control\\wmi\\autologger\\defender(api|audit)logger")

        for indicator in indicators:
            match = self.check_write_key(pattern=indicator, regex=True)
            if match:
                return True

        cmdlines = self.results["behavior"]["summary"]["executed_commands"]
        for cmdline in cmdlines:
            lower = cmdline.lower()
            if re.search(pat, lower):
                self.data.append({"command": cmdline})
                return True

        return False


class DisablesWindowsDefenderDISM(Signature):
    name = "disables_windows_defender_dism"
    description = "Disable Windows Defender via DISM"
    severity = 2
    categories = ["anti-av"]
    authors = ["ditekshen"]
    minimum = "1.3"
    evented = True
    ttps = ["T1089"]  # MITRE v6
    ttps += ["T1112"]  # MITRE v6,7,8
    ttps += ["T1562", "T1562.001"]  # MITRE v7,8
    mbcs = ["OB0006", "E1112", "F0004"]
    mbcs += ["OC0008", "C0036"]  # micro-behaviour

    def on_complete(self):
        indicators = [
            ".*\/Disable-Feature.*\/FeatureName:Windows-Defender.*",
        ]

        for indicator in indicators:
            match = self.check_executed_command(pattern=indicator, regex=True)
            if match:
                self.data.append({"command": match})
                return True

        return False


class AddWindowsDefenderExclusions(Signature):
    name = "add_windows_defender_exclusions"
    description = "Attempts to add Windows Defender Exclusions for specific file types by extension"
    severity = 3
    categories = ["bypass", "stealth", "anti-av"]
    authors = ["@para0x0dise"]
    minimum = "1.2"
    ttps = ["T1562.001"]
    references = [
        "https://github.com/elastic/protections-artifacts/blob/main/behavior/rules/windows/defense_evasion_windows_defender_exclusions_by_extension.toml",
    ]
    evented = True

    filter_apinames = set(["RegSetValueExA", "RegSetValueExW", "NtSetValueKey"])

    def __init__(self, *args, **kwargs):
        Signature.__init__(self, *args, **kwargs)
        self.detected = False

    def on_call(self, call, process):
        if not "\\windows\\microsoft.net" in process["module_path"].lower():
            regKeyPath = self.get_argument(call, "FullName").lower()
            valueName = self.get_argument(call, "ValueName")
            buf = self.get_argument(call, "Buffer")
            if buf == "0" and (
                "software\\policies\\microsoft\\windows defender\\exclusions\\extensions\\" in regKeyPath
                and any(
                    extension in valueName
                    for extension in (
                        "exe",
                        "pif",
                        "scr",
                        "js",
                        "vbs",
                        "wsh",
                        "hta",
                        "cpl",
                        "jse",
                        "vbe",
                        "bat",
                        "cmd",
                        "dll",
                        "ps1",
                    )
                )
            ):
                self.data.append({"regkey": regKeyPath})
                self.detected = True

    def on_complete(self):
        if self.detected:
            return True
        return False
