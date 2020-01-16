#
# Copyright (C) 2018 ETH Zurich, University of Bologna
# and GreenWaves Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Authors: Germain Haugou, ETH (germain.haugou@iis.ee.ethz.ch)

import pytablewriter

class Rst_file(object):
    def __init__(self, name, path):
        self.file = open(path, "w")
        self.name = name

    def close(self):
        self.file.close()

    def get_file(self):
        return self.file

    def dump_title(self, title, depth, link=None):

        if depth == 1:
            title_char = '#'
        elif depth == 2:
            title_char = '*'
        elif depth == 3:
            title_char = '='
        elif depth == 4:
            title_char = '-'
        elif depth == 5:
            title_char = '^'
        else:
            title_char = '"'

        self.file.write('\n')
        if link is not None:
            self.file.write('.. _%s:\n' % link)
            self.file.write('\n')
        self.file.write(title + '\n')
        self.file.write(title_char * len(title) + '\n')
        self.file.write('\n')


class Regfield(object):

    def get_row(self):
        if self.width == 1:
            bit = '%d' % self.bit
        else:
            bit = '%d:%d' % (self.bit + self.width - 1, self.bit)

        return [bit, self.access, self.name, self.desc]

    def dump_to_rst(self, rst):
        rst.append(self.get_row())



class Register(object):

    def dump_to_rst(self, rst):
        writer = pytablewriter.RstGridTableWriter()
        writer.header_list = ['Bit #', 'R/W', 'Name', 'Description']

        table = []
        for name, field in self.fields.items():
            field.dump_to_rst(table)

        writer.value_matrix = table

        writer.stream = rst.get_file()
        writer.write_table()

    def dump_to_reglist_rst(self, table):
        table.append([':ref:`%s<%s>`' % (self.name, self.name), self.offset, self.width, self.desc])


class Regmap(object):

    def dump_to_rst(self, rst):

        if self.input_file is not None:
            rst.file.write('Input file: %s\n' % self.input_file)

        rst.dump_title('Register map', 5)

        rst.dump_title('Overview', 6)

        writer = pytablewriter.RstGridTableWriter()
        writer.header_list = ['Name', 'Offset', 'Width', 'Description']

        table = []
        for name, register in self.registers.items():
            register.dump_to_reglist_rst(table)

        writer.value_matrix = table

        writer.stream = rst.get_file()
        writer.write_table()


        rst.dump_title('Generated headers', 6)

        self.dump_regs_to_rst(rst=rst)

        rst.file.write('|\n')


        for name, register in self.registers.items():
            rst.dump_title(register.name, 6, link=register.name)
            register.dump_to_rst(rst)



def dump_to_rst(regmap, name, rst_path):
    rst_file = Rst_file(name, rst_path)
    regmap.dump_to_rst(rst_file)
    rst_file.close()
