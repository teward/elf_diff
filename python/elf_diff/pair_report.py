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
from elf_diff.report import Report
from elf_diff.binary_pair import BinaryPair
import elf_diff.html as html
from elf_diff.error_handling import unrecoverable_error
from elf_diff.auxiliary import format_mem_change


class PairReport(Report):
    html_template_file = "pair_report_template.html"

    def __init__(self, settings):

        self.settings = settings

        self.validate_settings()

        self.binary_pair = BinaryPair(settings, settings.old_binary_filename,
                                      settings.new_binary_filename)

    @staticmethod
    def get_report_basename():
        return "pair_report"

    def validate_settings(self):
        if not self.settings.old_binary_filename:
            unrecoverable_error("No old binary filename defined")

        if not self.settings.new_binary_filename:
            unrecoverable_error("No new binary filename defined")

    def generate_persisting_symbols_table_html(self):

        old_binary = self.binary_pair.old_binary
        new_binary = self.binary_pair.new_binary

        table_html = ""

        import operator

        diff_by_symbol = {}
        for symbol_name in self.binary_pair.persisting_symbol_names:
            old_symbol = old_binary.symbols[symbol_name]
            new_symbol = new_binary.symbols[symbol_name]

            difference = new_symbol.size - old_symbol.size

            diff_by_symbol[symbol_name] = difference

        sorted_by_diff = sorted(diff_by_symbol.items(), key=operator.itemgetter(1), reverse=True)

        size_delta = 0

        for symbol_tuple in sorted_by_diff:

            symbol_name = symbol_tuple[0]

            old_symbol = old_binary.symbols[symbol_name]
            new_symbol = new_binary.symbols[symbol_name]

            if new_symbol.lives_in_program_memory():
                size_delta += new_symbol.size - old_symbol.size

            if old_symbol.size != new_symbol.size:
                symbol_name_html = html.escape_string(symbol_name)
                table_html += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" \
                              "<td>%s</td></tr>\n" % (
                                  html.generate_symbol_table_entry(symbol_name_html),
                                  new_symbol.type,
                                  html.format_number(old_symbol.size),
                                  html.format_number(new_symbol.size),
                                  html.format_number_delta(old_symbol.size, new_symbol.size)
                              )

        if size_delta == 0:
            table_visible = False
        else:
            table_visible = True

        return [table_html, table_visible, html.highlight_number(size_delta)]

    # noinspection DuplicatedCode
    def generate_disappeared_symbols_table_html(self):

        old_binary = self.binary_pair.old_binary

        table_html = ""
        overal_symbol_size = 0

        for symbol_name in sorted(self.binary_pair.disappeared_symbol_names,
                                  key=lambda symb_name: old_binary.symbols[symb_name].size,
                                  reverse=True):
            symbol_name_html = html.escape_string(symbol_name)
            symbol = old_binary.symbols[symbol_name]
            table_html += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (
                html.generate_symbol_table_entry(symbol_name_html),
                symbol.type,
                html.format_number(symbol.size))

            if symbol.lives_in_program_memory():
                overal_symbol_size += symbol.size

        if len(self.binary_pair.disappeared_symbol_names) == 0:
            table_visible = "invisible"
        else:
            table_visible = True

        return [table_html, table_visible, html.highlight_number(-overal_symbol_size)]

    # noinspection DuplicatedCode
    def generate_new_symbols_table_html(self):

        new_binary = self.binary_pair.new_binary

        table_html = ""
        overal_symbol_size = 0

        for symbol_name in sorted(self.binary_pair.new_symbol_names,
                                  key=lambda symb_name: new_binary.symbols[symb_name].size,
                                  reverse=True):
            symbol_name_html = html.escape_string(symbol_name)
            symbol = new_binary.symbols[symbol_name]
            table_html += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (
                html.generate_symbol_table_entry(symbol_name_html),
                symbol.type,
                html.format_number(symbol.size))

            if symbol.lives_in_program_memory():
                overal_symbol_size += symbol.size

        if len(self.binary_pair.new_symbol_names) == 0:
            table_visible = "invisible"
        else:
            table_visible = True

        return [table_html, table_visible, html.highlight_number(overal_symbol_size)]

    def generate_similar_symbols_table_html(self):

        table_html = ""

        index = 0
        for symbol_pair in self.binary_pair.similar_symbols:
            index = index + 1

            old_symbol = symbol_pair[0]
            new_symbol = symbol_pair[1]

            old_symbol_name_html = html.escape_string(old_symbol.name)
            new_symbol_name_html = html.escape_string(new_symbol.name)

            table_html += "<tr><td>%s</td><td><p>%s</p><p>%s</p></td><td><p>%s</p>" \
                          "<p>%s</p></td><td><p>%s</p><p>%s</p></td><td>%s</td></tr>\n" % (
                              html.generate_similar_symbol_table_entry(str(index)),
                              html.generate_symbol_table_entry_light(old_symbol_name_html),
                              html.generate_symbol_table_entry_light(new_symbol_name_html),
                              old_symbol.type,
                              new_symbol.type,
                              html.format_number(old_symbol.size),
                              html.format_number(new_symbol.size),
                              html.format_number_delta(old_symbol.size, new_symbol.size))

        if len(self.binary_pair.similar_symbols) == 0:
            table_visible = "invisible"
        else:
            table_visible = True

        return [table_html, table_visible, len(self.binary_pair.similar_symbols)]

    def generate_persistent_symbol_details_html(self):

        old_binary = self.binary_pair.old_binary
        new_binary = self.binary_pair.new_binary

        html_lines = []

        for symbol_name in self.binary_pair.persisting_symbol_names:

            old_symbol = old_binary.symbols[symbol_name]
            new_symbol = new_binary.symbols[symbol_name]

            symbol_name_html = html.escape_string(symbol_name)

            if not old_symbol.__eq__(new_symbol):

                symbol_differences = old_symbol.get_differences_as_html(new_symbol, "   ")

                if old_symbol.size == new_symbol.size:
                    size_info = "size unchanged"
                else:
                    size_info = format_mem_change("", old_symbol.size, new_symbol.size)

                html_lines.append("<{header}>{title} ({size_info})</{header}>\n".format(
                    header=self.settings.symbols_html_header,
                    title=html.generate_symbol_details_title(symbol_name_html),
                    size_info=size_info))
                html_lines.append("%s\n" % symbol_differences)

        return "\n".join(html_lines)

    # noinspection DuplicatedCode
    def generate_disappeared_symbol_details_html(self):

        html_lines = []

        if len(self.binary_pair.disappeared_symbol_names) > 0:
            html_lines.append("<pre>")
            for symbol_name in self.binary_pair.disappeared_symbol_names:
                symbol = self.binary_pair.old_binary.symbols[symbol_name]
                symbol_name_html = html.escape_string(symbol_name)
                html_lines.append("<%s>%s: %d bytes</%s>\n" % (
                    self.settings.symbols_html_header,
                    html.generate_symbol_details_title(symbol_name_html),
                    symbol.size,
                    self.settings.symbols_html_header))
                html_lines.append(html.escape_string(symbol.get_instructions_block("   ") + "\n"))
            html_lines.append("</pre>")

        return "\n".join(html_lines)

    # noinspection DuplicatedCode
    def generate_new_symbol_details_html(self):

        html_lines = []

        if len(self.binary_pair.new_symbol_names) > 0:
            html_lines.append("<pre>")
            for symbol_name in self.binary_pair.new_symbol_names:
                symbol = self.binary_pair.new_binary.symbols[symbol_name]
                symbol_name_html = html.escape_string(symbol_name)
                html_lines.append("<%s>%s: %d bytes</%s>\n" % (
                    self.settings.symbols_html_header,
                    html.generate_symbol_details_title(symbol_name_html),
                    symbol.size,
                    self.settings.symbols_html_header))
                html_lines.append(html.escape_string(symbol.get_instructions_block("   ") + "\n"))
            html_lines.append("</pre>")

        return "\n".join(html_lines)

    def generate_similar_symbol_details_html(self):

        html_lines = []

        index = 0
        for symbol_pair in self.binary_pair.similar_symbols:

            index = index + 1

            old_symbol = symbol_pair[0]
            new_symbol = symbol_pair[1]

            old_symbol_name_html = html.escape_string(old_symbol.name)
            new_symbol_name_html = html.escape_string(new_symbol.name)

            symbol_differences = old_symbol.get_differences_as_html(new_symbol, "   ")

            if old_symbol.size == new_symbol.size:
                size_info = "size unchanged"
            else:
                size_info = format_mem_change("", old_symbol.size, new_symbol.size)

            html_lines.append("<%s>Similar pair %s (%s)</%s>\n" % (
                self.settings.symbols_html_header,
                html.generate_similar_symbol_details_title(str(index)),
                size_info,
                self.settings.symbols_html_header))
            html_lines.append(
                "<p>Old: %s</p>\n" % (html.generate_symbol_details_title(old_symbol_name_html)))
            html_lines.append(
                "<p>New: %s</p>\n" % (html.generate_symbol_details_title(new_symbol_name_html)))
            html_lines.append("%s\n" % symbol_differences)

        return "\n".join(html_lines)

    def configure_jinja_keywords(self, skip_details):

        import datetime

        old_binary = self.binary_pair.old_binary
        new_binary = self.binary_pair.new_binary

        # If we generate a pdf files, we skip the details
        #
        if skip_details:
            details_visibility = False
            persisting_symbol_details_html = ""
            disappeared_symbol_details_html = ""
            new_symbol_details_html = ""
            similar_symbol_details_html = ""
        else:
            details_visibility = True
            persisting_symbol_details_html = self.generate_persistent_symbol_details_html()
            disappeared_symbol_details_html = self.generate_disappeared_symbol_details_html()
            new_symbol_details_html = self.generate_new_symbol_details_html()
            similar_symbol_details_html = self.generate_similar_symbol_details_html()

        if self.settings.project_title:
            doc_title = html.escape_string(self.settings.project_title)
        else:
            doc_title = "ELF Binary Comparison"

        [persisting_symbols_table, persisting_symbols_table_visible,
         persisting_symbols_delta] = self.generate_persisting_symbols_table_html()
        [disappeared_symbols_table, disappeared_symbols_table_visible,
         disappeared_symbols_size] = self.generate_disappeared_symbols_table_html()
        [new_symbols_table, new_symbols_table_visible,
         new_symbols_size] = self.generate_new_symbols_table_html()
        [similar_symbols_table, similar_symbols_table_visible,
         num_similar_symbols] = self.generate_similar_symbols_table_html()

        if self.settings.build_info == "":
            build_info_visible = False
        else:
            build_info_visible = True

        binary_details_visible = False
        if self.settings.old_binary_info == "":
            old_binary_info_visible = False
        else:
            old_binary_info_visible = True
            binary_details_visible = True

        if self.settings.new_binary_info == "":
            new_binary_info_visible = False
        else:
            new_binary_info_visible = True
            binary_details_visible = True

        return {
            "page_title": u"ELF Binary Comparison - (c) 2019 by noseglasses"
            , "doc_title": doc_title
            , "elf_diff_repo_base": self.settings.repo_path
            , "old_binary_file": html.escape_string(self.settings.old_alias)
            , "new_binary_file": html.escape_string(self.settings.new_alias)

            , "code_size_old_overall": str(old_binary.progmem_size)
            , "code_size_new_overall": str(new_binary.progmem_size)
            , "code_size_change_overall": html.format_number_delta(old_binary.progmem_size,
                                                                   new_binary.progmem_size)
            , "static_ram_old_overall": str(old_binary.static_ram_size)
            , "static_ram_new_overall": str(new_binary.static_ram_size)
            , "static_ram_change_overall": html.format_number_delta(old_binary.static_ram_size,
                                                                    new_binary.static_ram_size)
            , "text_size_old_overall": str(old_binary.text_size)
            , "text_size_new_overall": str(new_binary.text_size)
            , "text_size_change_overall": html.format_number_delta(old_binary.text_size,
                                                                   new_binary.text_size)
            , "data_size_old_overall": str(old_binary.data_size)
            , "data_size_new_overall": str(new_binary.data_size)
            , "data_size_change_overall": html.format_number_delta(old_binary.data_size,
                                                                   new_binary.data_size)
            , "bss_size_old_overall": str(old_binary.bss_size)
            , "bss_size_new_overall": str(new_binary.bss_size)
            , "bss_size_change_overall": html.format_number_delta(old_binary.bss_size,
                                                                  new_binary.bss_size)

            , "total_symbols_old": str(len(old_binary.symbols.keys()))
            , "total_symbols_new": str(len(new_binary.symbols.keys()))

            , "num_persisting_symbols": str(len(self.binary_pair.persisting_symbol_names))
            , "num_disappeared_symbols": str(self.binary_pair.num_symbols_disappeared)
            , "num_new_symbols": str(self.binary_pair.num_symbols_new)
            , "num_similar_symbols": str(num_similar_symbols)

            , "persisting_symbols_table_visible": persisting_symbols_table_visible
            , "disappeared_symbols_table_visible": disappeared_symbols_table_visible
            , "new_symbols_table_visible": new_symbols_table_visible
            , "similar_symbols_table_visible": similar_symbols_table_visible

            , "persisting_symbols_table": persisting_symbols_table
            , "disappeared_symbols_table": disappeared_symbols_table
            , "new_symbols_table": new_symbols_table
            , "similar_symbols_table": similar_symbols_table

            , "persisting_symbols_delta": persisting_symbols_delta
            , "disappeared_symbols_size": disappeared_symbols_size
            , "new_symbols_size": new_symbols_size

            , "details_visibility": details_visibility

            , "persisting_symbol_details_html": persisting_symbol_details_html
            , "disappeared_symbol_details_html": disappeared_symbol_details_html
            , "new_symbol_details_html": new_symbol_details_html
            , "similar_symbol_details_html": similar_symbol_details_html

            , "binary_details_visible": binary_details_visible

            , "old_binary_info_visible": old_binary_info_visible
            , "new_binary_info_visible": new_binary_info_visible

            , "old_binary_info": html.escape_string(self.settings.old_binary_info)
            , "new_binary_info": html.escape_string(self.settings.new_binary_info)

            , "build_info_visible": build_info_visible
            , "build_info": html.escape_string(self.settings.build_info)

            , "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def get_html_template():
        return PairReport.html_template_file


def generate_pair_report(settings):
    PairReport(settings).generate()
