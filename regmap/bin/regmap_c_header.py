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



c_head_pattern = """
/* THIS FILE HAS BEEN GENERATED, DO NOT MODIFY IT.
 */

/*
 * Copyright (C) 2018 ETH Zurich, University of Bologna
 * and GreenWaves Technologies
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

"""


class Header(object):

    def __init__(self, name, path):
        self.file = open(path, 'w')
        self.name = name
        self.file.write(c_head_pattern)
        def_name = path.replace('/', '_').replace('.', '_').upper()
        self.file.write('#ifndef __%s__\n' % def_name)
        self.file.write('#define __%s__\n' % def_name)
        self.file.write('\n')
        self.file.write('#ifndef LANGUAGE_ASSEMBLY\n')
        self.file.write('\n')
        self.file.write('#include <stdint.h>\n')
        self.file.write('#include "archi/utils.h"\n')
        self.file.write('\n')
        self.file.write('#endif\n')
        self.file.write('\n')

    def close(self):
        self.file.write('\n')
        self.file.write('#endif\n')



class Constant(object):

    def dump_to_header(self, header):
        header.file.write('#define %s_%s %s\n' % (header.name.upper(), self.name.upper(), self.value))



class Regfield(object):

    def dump_to_header(self, header, reg_name):
        field_name = '%s_%s' % (reg_name, self.name.upper())
        access_str = ''
        if self.access is not None:
          access_str = ' (access: %s)' % self.access
        if self.desc != '' or access_str != '':
          header.file.write('// %s%s\n' % (self.desc.replace('\n', ' '), access_str))
        header.file.write('#define %-60s %d\n' % (field_name + '_BIT', self.bit))
        header.file.write('#define %-60s %d\n' % (field_name + '_WIDTH', self.width))
        header.file.write('#define %-60s 0x%x\n' % (field_name + '_MASK', ((1<<self.width)-1)<<self.bit))
        reset = self.reset

        if reset is None and self.reg_reset is not None:
          reset = (self.reg_reset >> self.bit) & ((1<<self.width) - 1)

        if reset is not None:
            header.file.write('#define %-60s 0x%x\n' % (field_name + '_RESET', reset))

    def dump_macros(self, header, reg_name=None):
        header.file.write('\n')
        field_name = '%s_%s' % (reg_name, self.name.upper())
        header.file.write('#define %-50s (ARCHI_BEXTRACTU((value),%d,%d))\n' % (field_name + '_GET(value)', self.width, self.bit))
        header.file.write('#define %-50s (ARCHI_BEXTRACT((value),%d,%d))\n' % (field_name + '_GETS(value)', self.width, self.bit))
        header.file.write('#define %-50s (ARCHI_BINSERT((value),(field),%d,%d))\n' % (field_name + '_SET(value,field)', self.width, self.bit))
        header.file.write('#define %-50s ((val) << %d)\n' % (field_name + '(val)', self.bit))



class Register(object):

    def dump_to_header(self, header):

        header.file.write('\n')
        if self.desc != '':
            header.file.write('// %s\n' % self.desc.replace('\n', ' '))
        header.file.write('#define %-40s 0x%x\n' % ('%s_%s_OFFSET' % (header.name.upper(), self.name.upper()), self.offset))

    def dump_fields_to_header(self, header):

        for name, field in self.fields.items():
            header.file.write('\n')
            reg_name = '%s_%s' % (header.name.upper(), self.name.upper())
            field.dump_to_header(reg_name=reg_name, header=header)

    def dump_struct(self, header):
        header.file.write('\n')
        header.file.write('typedef union {\n')
        header.file.write('  struct {\n')

        current_index = 0
        current_pad = 0
        for name, field in self.fields.items():
            if current_index < field.bit:
                header.file.write('    unsigned int padding%d:%-2d;\n' % (current_pad, field.bit - current_index))
                current_pad += 1

            current_index = field.bit + field.width

            header.file.write('    unsigned int %-16s:%-2d; // %s\n' % (field.name.lower(), field.width, field.desc.replace('\n', ' ')))

        header.file.write('  };\n')
        header.file.write('  unsigned int raw;\n')
        header.file.write('} __attribute__((packed)) %s_%s_t;\n' % (header.name.lower(), self.name.lower()))

    def dump_vp_class(self, header):
        if self.width in [1, 8, 16, 32, 64]:
            header.file.write('\n')
            header.file.write('class vp_%s_%s : public vp::reg_%d\n' % (header.name.lower(), self.name.lower(), self.width))
            header.file.write('{\n')
            header.file.write('public:\n')

            reg_name = '%s_%s' % (header.name.upper(), self.name.upper())
            for name, field in self.fields.items():
                field_name = '%s_%s' % (reg_name, field.name.upper())
                header.file.write('  inline void %s_set(uint%d_t value) { this->set_field(value, %s_BIT, %s_WIDTH); }\n' % (field.name.lower(), self.width, field_name, field_name))
                header.file.write('  inline uint%d_t %s_get() { return this->get_field(%s_BIT, %s_WIDTH); }\n' % (self.width, field.name.lower(), field_name, field_name))

            header.file.write('};\n')

    def dump_macros(self, header=None):
        reg_name = '%s_%s' % (header.name.upper(), self.name.upper())
        for name, field in self.fields.items():
            field.dump_macros(header, reg_name)

    def dump_access_functions(self, header=None):
        reg_name = '%s_%s' % (header.name, self.name)

        header.file.write("\n")
        header.file.write("static inline uint32_t %s_get(uint32_t base) { return ARCHI_READ(base, %s_OFFSET); }\n" % (reg_name.lower(), reg_name.upper()));
        header.file.write("static inline void %s_set(uint32_t base, uint32_t value) { ARCHI_WRITE(base, %s_OFFSET, value); }\n" % (reg_name.lower(), reg_name.upper()));



class Regmap(object):

    def dump_regs_to_header(self, header):

        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS\n')
        header.file.write('//\n')

        for name, register in self.registers.items():
            register.dump_to_header(header)

    def dump_regfields_to_header(self, header):
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS FIELDS\n')
        header.file.write('//\n')

        for name, register in self.registers.items():
            register.dump_fields_to_header(header=header)

        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS STRUCTS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

        for name, register in self.registers.items():
            register.dump_struct(header=header)

        header.file.write('\n')
        header.file.write('#endif\n')

        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS STRUCTS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#ifdef __GVSOC__\n')

        for name, register in self.registers.items():
            register.dump_vp_class(header=header)

        header.file.write('\n')
        header.file.write('#endif\n')


        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS GLOBAL STRUCT\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

        header.file.write('\n')
        header.file.write('typedef struct {\n')

        for name, register in self.registers.items():
            desc = ''
            if register.desc != '':
                desc = ' // %s' % register.desc
            header.file.write('  unsigned int %-16s;%s\n' % (register.name.lower(), desc))

        header.file.write('} __attribute__((packed)) %s_%s_t;\n' % (header.name, self.name))

        header.file.write('\n')
        header.file.write('#endif\n')


        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS ACCESS FUNCTIONS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

        for name, register in self.registers.items():
            register.dump_access_functions(header=header)


        header.file.write('\n')
        header.file.write('#endif\n')



        header.file.write('\n')
        header.file.write('\n')
        header.file.write('\n')
        header.file.write('//\n')
        header.file.write('// REGISTERS FIELDS MACROS\n')
        header.file.write('//\n')
        header.file.write('\n')
        header.file.write('#ifndef LANGUAGE_ASSEMBLY\n')

        for name, register in self.registers.items():
            register.dump_macros(header=header)


        header.file.write('\n')
        header.file.write('#endif\n')

    def dump_groups_to_header(self, header):

        for name, group in self.regmaps.items():

            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')

            header.file.write('//\n')
            header.file.write('// GROUP %s\n' % name)
            header.file.write('//\n')

            if group.offset is not None:
                header.file.write('\n')
                header.file.write('#define %-40s 0x%x\n' % ('%s_%s_OFFSET' % (header.name.upper(), name.upper()), group.offset))

            group.dump_to_header(header)


    def dump_constants_to_header(self, header):

        if len(self.constants) != 0:
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('\n')
            header.file.write('//\n')
            header.file.write('// CUSTOM FIELDS\n')
            header.file.write('//\n')

        for name, constant in self.constants.items():
            constant.dump_to_header(header=header)

    def dump_to_header(self, header):
        self.dump_regs_to_header(header)
        self.dump_regfields_to_header(header)
        self.dump_groups_to_header(header)
        self.dump_constants_to_header(header)



def dump_to_header(regmap, name, header_path):
    header_file = Header(name, header_path)
    regmap.dump_to_header(header_file)
    header_file.close()
