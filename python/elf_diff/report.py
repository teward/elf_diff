# -*- coding: utf-8 -*-

# -*- mode: python -*-
#
# elf_diff
#
# Copyright (C) 2019  Noseglasses (shinynoseglasses@gmail.com)
#
# This program is free software: you can redistribute it and/or modify it under it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with along with
# this program. If not, see <http://www.gnu.org/licenses/>.
#


import platform
import tempfile
import pdfkit

import elf_diff.html as html


# noinspection PyProtectedMember
class Report(object):

    def __init__(self, settings):
        self.settings = settings

    def configure_jinja_keywords(self, skip_details):
        raise NotImplementedError

    @staticmethod
    def get_report_basename():
        raise NotImplementedError

    @staticmethod
    def get_html_template():
        raise NotImplementedError

    def write_html(self, out_file, skip_details=False):

        keywords = self.configure_jinja_keywords(skip_details)

        html.configure_template_write(self.settings,
                                      self.get_html_template(),
                                      out_file,
                                      keywords)

    def generate(self):

        if self.settings.html_file:
            html_file = self.settings.html_file
        else:
            html_file = "elf_diff_" + self.get_report_basename() + ".html"

        print("Writing html file " + html_file)

        # Python 2 and Python 3 use different mechanisms for open();
        # this explains why codecs.open was used.
        with open(html_file, mode="w", encoding="utf-8") as f:
            self.write_html(f)

        if self.settings.pdf_file:
            tmp_html_file = tempfile.NamedTemporaryFile(suffix='.html')

            self.write_html(tmp_html_file, skip_details=True)

            pdfkit.from_url(tmp_html_file, self.settings.pdf_file)

            tmp_html_file.close()
