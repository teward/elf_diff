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
python_version = tuple(map(int, platform.python_version_tuple()))

from elf_diff.error_handling import unrecoverable_error


def escape_string(string):
    return string.replace("<", "&lt;").replace(">", "&gt;")


def generate_symbol_table_entry(symbol_name):
    return "<a name=\"table_%s\"><a href=\"#details_%s\">%s</a></a>" % \
           (symbol_name, symbol_name, symbol_name)


def generate_symbol_table_entry_light(symbol_name):
    return "<a href=\"#details_%s\">%s</a>" % \
           (symbol_name, symbol_name)


def generate_symbol_details_title(symbol_name):
    return "<a name=\"details_%s\"><a href=\"#table_%s\">%s</a></a>" % \
           (symbol_name, symbol_name, tag_symbol_name(symbol_name))


def generate_similar_symbol_table_entry(similar_pair_id):
    return "<a name=\"similar_table_%s\"><a href=\"#similar_details_%s\">%s</a></a>" % \
           (similar_pair_id, similar_pair_id, similar_pair_id)


def generate_similar_symbol_details_title(similar_pair_id):
    return "<a name=\"similar_details_%s\"><a href=\"#similar_table_%s\">%s</a></a>" % \
           (similar_pair_id, similar_pair_id, similar_pair_id)


def tag_symbol_name(symbol_name):
    return "<span class=\"symbol_name\">%s</span>" % symbol_name


def format_number(number):
    return "<span class=\"number\">%s</span>" % number


def highlight_number(number):
    if number > 0:
        css_class = "deterioration"
    elif number < 0:
        css_class = "improvement"
    else:
        css_class = "unchanged"

    return "<span  class=\"%s number\">%+d</span>" % (css_class, number)


def pre_highlight_source_code(src):
    return "__ED_SOURCE_START__%s__ED_SOURCE_END__" % src


def post_highlight_source_code(src):
    return src.replace("__ED_SOURCE_START__", "<span class=\"source\">") \
        .replace("__ED_SOURCE_END__", "</span>")


def post_highlight_source_code_remove_tags(src):
    return src.replace("__ED_SOURCE_START__", "") \
        .replace("__ED_SOURCE_END__", "")


def format_number_delta(old_size, new_size):
    return highlight_number(new_size - old_size)


# noinspection PyUnboundLocalVariable
def configure_template(settings, template_filename, keywords):
    import jinja2
    from jinja2 import Environment, FileSystemLoader, StrictUndefined

    template_path = settings.repo_path + "/html"

    env = Environment(loader=FileSystemLoader(template_path),
                      undefined=StrictUndefined)

    # addGlobalJinjaFunction(GetComponentLink)

    try:
        creator = env.get_template(template_filename)
    except jinja2.exceptions.TemplateError as e:
        unrecoverable_error("Failed creating jinja creator\n" + str(e))

    try:
        replaced_content = creator.render(keywords)
    except jinja2.exceptions.TemplateError as e:
        unrecoverable_error("Failed rendering jinja template \'" +
                            template_filename + "\'\n" + str(e))

    return replaced_content  # .encode('utf8')


def configure_template_write(settings, template_filename, out_file, keywords):
    html_code = configure_template(settings, template_filename, keywords)

    out_file.write(html_code)
