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

import elf_diff.html as html


# noinspection PyProtectedMember,PyUnresolvedReferences
class Report(object):

    def generate(self):

        import codecs

        if self.settings.html_file:
            html_file = self.settings.html_file
        else:
            html_file = "elf_diff_" + self.getReportBasename() + ".html"

        print("Writing html file " + html_file)
        with codecs.open(html_file, "w", "utf-8") as f:
            self.write_html(f)

        if self.settings.pdf_file:
            import tempfile

            tmp_html_file = tempfile._get_default_tempdir() + "/" + \
                next(tempfile._get_candidate_names()) + ".html"

            with codecs.open(tmp_html_file, "w", "utf-8") as f:
                self.write_html(f, skip_details=True)

            import pdfkit
            pdfkit.from_url(tmp_html_file, self.settings.pdf_file)

            import os
            os.remove(tmp_html_file)

    def write_html(self, out_file, skip_details=False):

        keywords = self.configureJinjaKeywords(skip_details)

        html.configure_template_write(self.settings,
                                      self.getHTMLTemplate(),
                                      out_file,
                                      keywords)
