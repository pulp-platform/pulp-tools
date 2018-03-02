
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
    pass


class Spim_verif(Periph):

    def bind(self, result, config):
        return [["pulp_chip->%s" % config.get('spi'), "spim_verif->spi"]]



class Jtag_proxy(Periph):

    def bind(self, result, config):
        return [
            ["pulp_chip->%s" % config.get('jtag'), "jtag_proxy->jtag"],
            ["pulp_chip->%s" % config.get('ctrl'), "jtag_proxy->ctrl"]
        ]



peripherals = {
    'spim_verif': Spim_verif,
    'jtag_proxy': Jtag_proxy
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

    def __init__(self, name=None, config_path=None, config_string=None, config=None, args=None):
        self.name = name

        if config_path is not None:
            with open(config_path, 'r') as fd:
                config = json.load(fd, object_pairs_hook=OrderedDict)

        if config_string is not None:
            config = json.loads(config_string, object_pairs_hook=OrderedDict)

        try:
            if args is not None:
                for arg in args.split(':'):
                    key, value = arg.split('=')
                    config2 = js.import_config(config)
                    config2.set(key, value)
                    config = config2.get_dict()
        except:
            pass


        self.top = Top_template(config=config)

    def gen_config(self):
        args = []
        return self.top.gen(args), args

    def gen(self, path):

        config = self.top.gen()

        with open(path, 'w') as file:
            json.dump(config, file, indent='  ')
