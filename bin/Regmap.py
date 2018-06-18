#
# Copyright (C) 2018 ETH Zurich and University of Bologna
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


import collections
from prettytable import PrettyTable


class Register_field(object):

    def __init__(self, name, config):
        self.bit = config.get('bit')
        self.width = config.get('width')
        self.access = config.get('access')
        self.reset = config.get('reset')
        self.desc = config.get('desc')

    def dump_doc(self, table, dump_regs=False):
        if self.width == 1:
            bit = '%d' % self.bit
        else:
            bit = '%d:%d' % (self.bit + self.width - 1, self.bit)

        row = []
        if dump_regs:
            row += ['', '', '', '']

        table.add_row(row + [bit, self.access, self.desc])

class Register(object):

    def __init__(self, name, regmap, config):

        self.fields = collections.OrderedDict([])
        self.config = config
        self.name = name
        self.regmap = regmap

        self.desc = config.get('desc')
        self.offset = int(config.get('offset'), 0)
        self.width = config.get('width')

        content = config.get('content')
        for name, field in content.items():
            self.fields[name] = Register_field(name, field)

    def get_group_path(self):
        return self.regmap.get_group_path()

    def get_offset(self):
        parent_offset = self.regmap.get_offset()

        if parent_offset is not None:
            return parent_offset + self.offset
        else:
            return self.offset


    def clone(self, regmap):
        new_reg = Register(self.name, regmap, self.config)
        regmap.registers[self.name] = new_reg

    def dump_doc(self, table, dump_regs_fields):

        row = [self.get_group_path(), '0x%x' % self.get_offset(), self.width, self.desc]
        if dump_regs_fields:
            row += ['', '', '']

        table.add_row(row)

        if dump_regs_fields:
            for name, field in self.fields.items():
                field.dump_doc(table, dump_regs=True)

    def dump_doc_fields(self):

        x = PrettyTable(['Bit #', 'R/W', 'Description'])
        x.align = 'l'

        for name, field in self.fields.items():
            field.dump_doc(x)

        print (self.desc)
        print (x)
        print ('\n')


class Regmap(object):

    def __init__(self, config, name=None, parent=None):
        self.templates = collections.OrderedDict()
        self.registers = collections.OrderedDict()
        self.groups = collections.OrderedDict()
        self.parent = parent
        self.name = name
        self.offset = None
        self.config = config

        if name is None:
            self.__parse_elems(config)
        else:
            self.__parse_elem(name, config)

    def get_offset(self):
        offset = 0
        parent_offset = None
        if self.parent is not None:
            parent_offset = self.parent.get_offset()
        if parent_offset is not None:
            offset += parent_offset
        if self.offset is not None:
            offset += self.offset
        return offset

    def get_group_path(self):
        parent_path = None
        if self.parent is not None:
            parent_path = self.parent.get_group_path()

        if parent_path is not None:
            return parent_path + ':' + self.name
        else:
            return self.name

        return self.name

    def __parse_elems(self, config):

        for name, obj in config.items():
            self.__parse_elem_from_type(name, obj)

    def __get_template(self, name):
        if self.templates.get(name) is not None:
            return self.templates.get(name)

        if self.parent is not None:
            return self.parent.__get_template(name)

        return None



    def __parse_elem_from_type(self, name, config):
        if type(config) not in [dict, collections.OrderedDict]:
            return

        obj_type = config.get('type')

        if obj_type is not None:

            if obj_type == 'template':
                self.templates[name] = Template(config, parent=self)
                return

            elif obj_type == 'register':
                self.registers[name] = Register(name, self, config)
                return

            elif obj_type == 'group':
                self.groups[name] = Regmap(config, name=name, parent=self)
                return

        self.__parse_elem(name, config)


    def __parse_elem(self, name, config):

        self.offset = config.get('offset')
        if self.offset is not None:
            self.offset = int(self.offset, 0)
        template = config.get('template')
        if template is not None:
            self.__get_template(template).clone(self)
            return

        self.__parse_elems(config)

    def dump_doc_regs_rec(self, table, dump_regs_fields):

        for name, group in self.groups.items():
            group.dump_doc_regs_rec(table, dump_regs_fields=dump_regs_fields)

        for name, register in self.registers.items():
            register.dump_doc(table, dump_regs_fields=dump_regs_fields)

    def dump_doc_regs(self, dump_regs_fields=False):

        rows = ['Group', 'Offset', 'Width', 'Description']
        if dump_regs_fields:
            rows += ['Field bit #', 'Field R/W', 'Field description']

        table = PrettyTable(rows)
        table.align = 'l'

        self.dump_doc_regs_rec(table, dump_regs_fields=dump_regs_fields)

        print (table)

    def dump_doc_regs_fields(self):
        for name, group in self.groups.items():
            print (name)
            group.dump_doc_regs_fields()
            print ('\n')

        for name, register in self.registers.items():
            register.dump_doc_fields()




    def dump_memmap(self, dump_regs=False, dump_regs_fields=False):

        if dump_regs_fields and not dump_regs:
            self.dump_doc_regs_fields()
        else:
            self.dump_doc_regs(dump_regs_fields=dump_regs_fields)

    def clone(self, regmap):
        regmap.groups[self.name] = Regmap(self.config, name=self.name, parent=regmap)


class Template(Regmap):

    def clone(self, regmap):

        for name, group in self.groups.items():
            group.clone(regmap)

        for name, register in self.registers.items():
            register.clone(regmap)
