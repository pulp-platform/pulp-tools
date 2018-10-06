
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

header_pattern="""
OUTPUT_ARCH({pulp_core_family})
ENTRY( _start )
"""



class Variable(object):

    def __init__(self, script, value):
        self.value = value
        script.add_variable(self)

    def gen(self, file):
        file.write('%s\n' % self.value)





class Link_script(object):

  def __init__(self, config):
    self.variables = []

    Variable(self, '__ZERO  = 0;')
    Variable(self, '__USE_UART = 0;')
    Variable(self, '__RT_DEBUG_CONFIG   = (0 << 8) | 0;')
    Variable(self, '__FC   = 1;')
    Variable(self, '__L2   = 0x80000;')
    Variable(self, '__L1Cl = 0x10000;')
    Variable(self, '__FETCH_ALL = 0x0;')
    Variable(self, '__ACTIVE_FC = 0x1;')
    Variable(self, '__rt_stack_size = 0x%x;' % (config.get_int('stack_size')))
    if config.get('cluster/nb_pe') != None:
      Variable(self, '__NB_ACTIVE_PE = %d;' % (config.get_int('cluster/nb_pe')))

    platform = 0
    if config.get('platform') == 'fpga':
      platform = 1
    elif config.get('platform') == 'rtl':
      platform = 2
    elif config.get('platform') == 'gvsoc':
      platform = 3
    elif config.get('platform') == 'board':
      platform = 4
    Variable(self, '__rt_platform = %d;' % platform)

    iodev = config.get('rt/iodev')

    iodevs_conf = config.get_config('rt/iodevs')

    Variable(self, '__rt_iodev = %s;' % (iodevs_conf.get_config(iodev).value()))

    for iodev_name in iodevs_conf.keys():
        iodev_conf = iodevs_conf.get_config(iodev_name)
        for item_name in iodev_conf.keys():
            Variable(self, '%s = %s;' % ('__rt_iodev_%s_%s' % (iodev_name, item_name), iodev_conf.get(item_name)))



    if config.get('nb_cluster') != None and config.get('nb_cluster') != 0:
      Variable(self, '__rt_nb_cluster = %s;' % (config.get('nb_cluster')))
      Variable(self, '__rt_nb_pe = %s;' % (config.get('cluster/nb_pe')))
    if config.get('rt/cl_master_stack_size') is not None:
        Variable(self, '__rt_cl_master_stack_size = 0x%x;' % config.get('rt/cl_master_stack_size'))
    if config.get('rt/cl_slave_stack_size') is not None:
        Variable(self, '__rt_cl_slave_stack_size = 0x%x;' % config.get('rt/cl_slave_stack_size'))

    config_trace_value = 0
    warning = 0
    werror = 0
    if config.get('rt/trace'):
      traces = config.get('rt/traces')
      if traces == None or traces == 'all': config_trace_value = 0xffffffff
      else:
        for trace in traces.split(','):
          if trace == 'init': config_trace_value |= (1<<0)
          elif trace == 'alloc': config_trace_value |= (1<<1)

    if config.get('rt/warnings') is not None: warning = config.get_bool('rt/warnings')
    if config.get('rt/werror') is not None: werror = config.get_bool('rt/werror')

    config_value = (warning << 0) | (werror << 1)

    rt_config_value = 0

    if config.get('soc/cluster') is not None and config.get('rt/start-all'):

        if config.get('rt/fc-start') == False or config.get('rt/cluster-start'):
            rt_config_value |= 1<<0
        if config.get('rt/fc-start'):
            rt_config_value |= 1<<1

    Variable(self, '__rt_config = 0x%x;' % rt_config_value)
    Variable(self, '__rt_debug_init_config = 0x%x;' % config_value)
    Variable(self, '__rt_debug_init_config_trace = 0x%x;' % config_trace_value)

    if config.get_bool('rt/libc'):
      Variable(self, 'GROUP( -lc -lgloss -lgcc )')
    else:
      Variable(self, 'GROUP( -lgloss -lgcc )')

  def add_variable(self, section):
    self.variables.append(section)

  def gen(self, file, prop_file):
    if prop_file is not None:
      for var in self.variables:
        var.gen(prop_file)
      prop_file.write('\n')



def gen_link_script(file, prop_file, config):
  link = Link_script(config)
  link.gen(file, prop_file)
