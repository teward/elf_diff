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

from elf_diff.report import Report, unrecoverable_error
from elf_diff.binary_pair import BinaryPair

import elf_diff.html as html


class MassReport(Report):
    html_template_file = "mass_report_template.html"

    def __init__(self, settings):

        self.settings = settings

        if len(self.settings.mass_report_members) == 0:
            unrecoverable_error("No mass report binary_pairs members defined in driver file")

        self.generate_pair_reports()

    @staticmethod
    def get_report_basename():
        return "mass_report"

    def generate_pair_reports(self):

        self.binary_pairs = []

        for pair_report_setting in self.settings.mass_report_members:
            binary_pair = BinaryPair(self.settings,
                                     pair_report_setting.old_binary_filename,
                                     pair_report_setting.new_binary_filename)

            binary_pair.short_name = pair_report_setting.short_name

            self.binary_pairs.append(binary_pair)

    def generate_resource_consumption_table_html(self):

        table_lines_html = []

        for binary_pair in self.binary_pairs:
            table_lines_html.append(
                "<tr><td>{short_name}</td><td>{code_size_old_overall}</td><td>"
                "{code_size_new_overall}</td><td>{code_size_delta_overall}</td>"
                "<td>{static_ram_old_overall}</td><td>{static_ram_new_overall}</td>"
                "<td>{static_ram_change_overall}</td></tr>\n".format(
                    short_name=binary_pair.short_name,
                    code_size_old_overall=binary_pair.old_binary.progmem_size,
                    code_size_new_overall=binary_pair.new_binary.progmem_size,
                    code_size_delta_overall=html.format_number_delta(
                        binary_pair.old_binary.progmem_size,
                        binary_pair.new_binary.progmem_size),
                    static_ram_old_overall=binary_pair.old_binary.static_ram_size,
                    static_ram_new_overall=binary_pair.new_binary.static_ram_size,
                    static_ram_change_overall=html.format_number_delta(
                        binary_pair.old_binary.static_ram_size,
                        binary_pair.new_binary.static_ram_size)
                ))

        return "\n".join(table_lines_html)

    def generate_symbols_table_html(self):

        table_lines_html = []

        for binary_pair in self.binary_pairs:
            num_persisting_symbols = str(len(binary_pair.persisting_symbol_names))
            num_disappeared_symbols = str(binary_pair.num_symbols_disappeared)
            num_new_symbols = str(binary_pair.num_symbols_new)

            table_lines_html.append(
                "<tr><td>{short_name}</td><td>{num_persisting_symbols}</td>"
                "<td>{num_disappeared_symbols}</td><td>{num_new_symbols}</td></tr>\n".format(
                    short_name=binary_pair.short_name,
                    num_persisting_symbols=str(len(binary_pair.persisting_symbol_names)),
                    num_disappeared_symbols=str(binary_pair.num_symbols_disappeared),
                    num_new_symbols=str(binary_pair.num_symbols_new)
                ))

        return "\n".join(table_lines_html)

    def configure_jinja_keywords(self, skip_details):

        import datetime

        resource_consumtption_table = self.generate_resource_consumption_table_html()
        symbols_table = self.generate_symbols_table_html()

        if self.settings.project_title:
            doc_title = html.escape_string(self.settings.project_title)
        else:
            doc_title = "ELF Binary Comparison - Mass Report"

        return {
            "elf_diff_repo_base": self.settings.repo_path,
            "doc_title": doc_title,
            "page_title": u"ELF Binary Comparison - (c) 2019 by noseglasses",
            "resource_consumption_table": resource_consumtption_table,
            "symbols_table": symbols_table,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def get_html_template():
        return MassReport.html_template_file


def generate_mass_report(settings):
    MassReport(settings).generate()
