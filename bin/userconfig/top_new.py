
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


import json
from collections import OrderedDict

try:
    import json_tools as js
except:
    pass


class Arg(object):

    def __init__(self, str):
        self.params = []
        self.name = str
        self.params_dict = {}
        if str.find('(') != -1:
            self.name = str.split('(', 1)[0]
            for arg_str in str.split('(', 1)[1][:-1].split(','):
                arg = Arg(arg_str)
                self.params.append(arg)
                self.params_dict[arg.name] = arg


    def get_params(self):
        return self.params

    def get_param(self, name):
        return self.params_dict.get(name)

    def get_name(self):
        return self.name

    def get_value(self):
        return self.name

    def dump(self, indent=0):
        print ('  '*indent + self.name)
        for arg in self.params:
            arg.dump(indent + 2)



def get_core_from_name(name):
  if name == 'riscyv2-fpu':
    return 'ri5ky_v2_fpu'
  elif name == 'riscyv2':
    return 'ri5ky_v2'
  elif name in ['zeroriscy', 'microriscy']:
    return name
  else:
    raise Exception('Unknown core: ' + name)


class Periph(object):

    def process(self, config):
        return []


class Spim_verif(Periph):

    def bind(self, result, config):
        return [["pulp_chip->%s" % config.get('spi'), "spim_verif->spi"]]

    def handle_arg(self, config, arg):
        config.set('periphs/spim_verif/spi', arg.get_params()[0].get_value())


class Jtag_proxy(Periph):

    def bind(self, result, config):
        return [
            ["pulp_chip->%s" % config.get('jtag'), "jtag_proxy->jtag"],
            ["pulp_chip->%s" % config.get('ctrl'), "jtag_proxy->ctrl"]
        ]

    def handle_arg(self, config, arg):
        config.set('periphs/jtag_proxy/jtag', arg.get_params()[0].get_value())
        config.set('periphs/jtag_proxy/ctrl', arg.get_params()[1].get_value())


class Debug_bridge(object):

    def handle_arg(self, config, arg):
        pass

    def process(self, config):
        if config.get('boot') is not None and config.get('boot').get() == 'jtag':
            return [
                ['system_tree/debug-bridge/cable/type', 'jtag-proxy'],
                ['system_tree/debug-bridge/boot-mode', 'jtag']
            ]
        return []



class Boot(object):

    def handle_arg(self, config, arg):
        config.set('boot', arg.get_params()[0].get_value())

    def process(self, config):
        return []



peripherals = {
    'spim_verif': Spim_verif,
    'jtag_proxy': Jtag_proxy
}

tools = {
    'debug-bridge': Debug_bridge,
    'boot':         Boot
}


class Generic_template(object):

    def __init__(self, name=None, config={}):
        if name is not None:
            self.name = name
        self.config = config
        self.comps = {}
        self.props = {}

        for key, value in config.items():
            if key in 'template':
                continue

            if type(value) == OrderedDict or type(value) == dict:
                self.comps[key] = get_comp_from_config(key, value)
            else:
                self.props[key] = value

    def handle_periphs(self, result):
        periphs = self.config.get('periphs')
        if periphs is not None:
            if result.get('system_tree') is None:
                result['system_tree'] = OrderedDict()

            if result.get('system_tree').get('board') is None:
                result['system_tree']['board'] = OrderedDict()

            tb_comps = []
            bindings = []

            for name in periphs.keys():
                periph_config = periphs.get(name)

                instance_name = name
                index = 0
                while True:
                    if result['system_tree']['board'].get(instance_name) is None:
                        result['system_tree']['board'][instance_name] = OrderedDict([("includes", ['configs/periph/%s.json' % name])])
                        tb_comps.append(instance_name)
                        break
                    instance_name = name + '_' + index
                    index += 1

                periph = peripherals.get(name)()

                bindings += periph.bind(result, periph_config)

            result['system_tree']['board']['tb_comps'] = tb_comps
            result['system_tree']['board']['tb_bindings'] = bindings

    def gen(self, args=[]):
        for comp in self.comps.values():
            comp.gen(args)


class Pulpissimo(Generic_template):

    name = 'pulpissimo'

    def gen(self, args=[]):

        fc = self.config.get('fc')
        if fc is not None:
            core = fc.get('core')
            if core is not None:
                args.append(['**/fc/core', get_core_from_name(core)])

        result = OrderedDict()
        result['system'] = "pulpissimo"
        result["includes"] = ["configs/pulpissimo_system.json"]


        install_name = self.config.get('install_name')
        if install_name is not None:
            result['install_name'] = install_name

        return result



class Quentin(Generic_template):

    name = 'quentin'

    def gen(self, args=[]):

        result = OrderedDict()
        result['system'] = "quentin"
        result["includes"] = ["configs/quentin_system.json"]


        install_name = self.config.get('install_name')
        if install_name is not None:
            result['install_name'] = install_name

        return result


class Gap(Generic_template):

    name = 'gap'

    def gen(self, args=[]):

        result = OrderedDict()
        result['system'] = "gap"
        result["includes"] = ["configs/gap_system.json"]


        install_name = self.config.get('install_name')
        if install_name is not None:
            result['install_name'] = install_name

        return result


class Wolfe(Generic_template):

    name = 'wolfe'

    def gen(self, args=[]):

        result = OrderedDict()
        result['system'] = "wolfe"
        result["includes"] = ["configs/wolfe_system.json"]


        install_name = self.config.get('install_name')
        if install_name is not None:
            result['install_name'] = install_name

        return result



class Pulp(Generic_template):

    name = 'pulp'

    def gen(self, args=[]):

        result = OrderedDict()
        result['system'] = "pulp"
        result["includes"] = ["configs/pulp_system.json"]


        install_name = self.config.get('install_name')
        if install_name is not None:
            result['install_name'] = install_name

        return result


class Top_template(Generic_template):

    name = 'top'

    def gen(self, args=[]):


        result = OrderedDict([
            ("includes", ["configs/defaults.json"])
        ])

        system = OrderedDict()

        result["system_tree"] = self.comps.get('chip').gen(args)

        self.handle_periphs(result)

        return result

templates = [ Pulpissimo, Quentin, Pulp, Gap, Wolfe ]


def get_comp_from_config(name, config):

    template_name = config.get('template')

    if template_name is None:
        return Generic_template(name, config)

    for template in templates:
        if template_name == template.name:
            return template(name, config)

    raise Exception('Unknown template: ' + template_name)



class Top(object):

    def __init__(self, name=None, config_path=None, config_string=None, config=None, props=None, args=None):
        self.name = name
        self.config_args = []

        if config_path is not None:
            with open(config_path, 'r') as fd:
                config = json.load(fd, object_pairs_hook=OrderedDict)

        if config_string is not None:
            config = json.loads(config_string, object_pairs_hook=OrderedDict)

        js_config = js.import_config(config)

        args_objects = None
        if args is not None:
            for name in args.split(':'):
                arg = Arg(name)
                args_objects = self.handle_arg(js_config, arg)

        try:
            if props is not None:
                for arg in props.split(':'):
                    key, value = arg.split('=')
                    js_config.set(key, value)
        except:
            pass

        if args_objects is not None:
            for arg_object in args_objects:
                self.config_args += arg_object.process(js_config)

        self.top = Top_template(config=js_config.get_dict())

    def handle_arg(self, config, arg):

        result = []

        periph = peripherals.get(arg.get_name())
        if periph is not None:
            obj = periph()
            result.append(obj)
            obj.handle_arg(config=config, arg=arg)

        tool = tools.get(arg.get_name())
        if tool is not None:
            obj = tool()
            result.append(obj)
            obj.handle_arg(config=config, arg=arg)

        return result


    def gen_config(self):
        return self.top.gen(self.config_args), self.config_args

    def gen(self, path):

        config = self.top.gen(self.config_args)

        with open(path, 'w') as file:
            json.dump(config, file, indent='  ')
