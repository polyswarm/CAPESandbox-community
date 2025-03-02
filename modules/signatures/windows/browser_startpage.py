# Copyright (C) 2015 Kevin Ross
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from lib.cuckoo.common.abstracts import Signature


class browser_startpage(Signature):
    name = "browser_startpage"
    description = "Attempts to modify Internet Explorer's start page"
    severity = 2
    categories = ["browser"]
    authors = ["Kevin Ross"]
    minimum = "1.2"
    ttps = ["T1112"]  # MITRE v6,7,8
    mbcs = ["OB0006", "E1112"]
    mbcs += ["OC0008", "C0036", "C0036.001"]  # micro-behaviour

    def run(self):
        if self.check_write_key(
            pattern=r".*\\SOFTWARE\\(Wow6432Node\\)?Microsoft\\Internet\\ Explorer\\Main\\Start\\ Page$", regex=True
        ):
            return True

        return False
