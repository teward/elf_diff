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

from elf_diff.html import post_highlight_source_code_remove_tags
from elf_diff.html import post_highlight_source_code


class Symbol(object):
    type_function = 1
    type_data = 2

    def __init__(self, name):
        self.name = name
        self.instruction_lines = []
        self.size = 0
        self.type = "?"
        self.namespace = None
        self.parameters = None
        self.actual_name = self.name
        self.symbol_parse_success = False
        self.symbol_type = None

    def add_instructions(self, instruction_line):
        self.instruction_lines.append(instruction_line)

    def __eq__(self, other):
        if not self.name == other.name:
            # print("Symbol name differs")
            return False

        if not self.size == other.size:
            return False

        if not len(self.instruction_lines) == len(other.instruction_lines):
            # print("Instructions differ")
            return False

        symbol_diff = [i for i, j in zip(self.instruction_lines, other.instruction_lines) if i != j]
        if len(symbol_diff) > 0:
            # print("Symbols differ")
            return False

        # print("Symbols equal")
        return True

    def get_differences_as_string(self, other, indent):

        import difflib
        # from difflib_data import *

        diff = difflib.ndiff(self.instruction_lines, other.instruction_lines)
        # print list(diff)
        return post_highlight_source_code_remove_tags(indent + ("\n" + indent).join(list(diff)))

    def get_differences_as_html(self, other, indent):

        import difflib
        diff_class = difflib.HtmlDiff(tabsize=3, wrapcolumn=200)

        diff_table = diff_class.make_table(self.instruction_lines,
                                           other.instruction_lines,
                                           fromdesc='Old',
                                           todesc='New',
                                           context=True,
                                           numlines=1000)

        return post_highlight_source_code(diff_table)

    def get_instructions_block(self, indent):
        return indent + ("\n" + indent).join(self.instruction_lines)

    def lives_in_program_memory(self):
        return (self.type != 'B') and (self.type != 'b') and \
               (self.type != 'S') and (self.type != 's')

    def parse_signature(self):

        import re

        symbol_regex = r"((([\S]*)?::)?)?(\w+)(\((.*)\))?"
        match = re.match(symbol_regex, self.name)
        if match:
            self.namespace = match.group(3)
            self.actual_name = match.group(4)
            self.parameters = match.group(6)
            self.symbol_parse_success = True
        else:
            return

        if self.parameters:
            self.symbol_type = Symbol.type_function
        else:
            self.symbol_type = Symbol.type_data

    def init(self):
        self.parse_signature()

    def was_function_renamed(self, other):
        return self.namespace == other.namespace \
               and self.parameters == other.parameters

    def has_function_signature_changed(self, other):
        return self.namespace == other.namespace \
               and self.actual_name == other.actual_name

    def was_function_moved(self, other):
        return self.actual_name == other.actual_name \
               and self.parameters == other.parameters

    def was_data_moved(self, other):
        return self.actual_name == other.actual_name \
               and self.size == other.size

    def was_data_resized(self, other):
        return self.actual_name == other.actual_name \
               and self.namespace == other.namespace

    def was_data_renamed(self, other):
        return self.namespace == other.namespace \
               and self.size == other.size

    def is_similar(self, other):

        if not (self.symbol_parse_success and other.symbol_parse_success):
            return False

        if self.symbol_type == Symbol.type_function:
            if other.symbol_type == Symbol.type_function:
                return self.was_function_renamed(other) \
                       or self.has_function_signature_changed(other) \
                       or self.was_function_moved(other)

        elif self.symbol_type == Symbol.type_data:
            if other.symbol_type == Symbol.type_data:
                return self.was_data_moved(other) \
                       or self.was_data_resized(other) \
                       or self.was_data_renamed(other)

        return False
