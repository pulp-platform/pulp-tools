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

import json
import plptree
import os
from collections import OrderedDict


class Interface(object):

    def __init__(self, comp, name):
        self.__dict__['name'] = name
        self.__dict__['comp'] = comp



class Component(object):

    def __init__(self, **kwargs):
        self.__dict__['is_tb_comp'] = False

        self.__dict__['_Component__comps'] = OrderedDict()
        self.__dict__['_Component__master_itfs'] = OrderedDict()
        self.__dict__['_Component__slave_itfs'] = OrderedDict()

        if len(kwargs) != 0:
            self.__dict__['_Component__properties'] = kwargs.copy()

    def get_master_itfs(self):
        return self.__dict__['_Component__master_itfs']

    def get_slave_itfs(self):
        return self.__dict__['_Component__slave_itfs']

    def set_name(self, name):
        self.__dict__['_Component__name'] = name

    def get_name(self):
        return self.__dict__.get('_Component__name')

    def get_json_config(self, expand=False):
        if not expand:
            return json.dumps(self.gen(), indent='  ')


        config = plptree.get_config_tree_from_dict(self.gen(), path=os.getcwd())
        return config.get_string()


    def __setattr__(self, name, value):
        if type(value) == Interface:
            self.__dict__['_Component__master_itfs'][name] = value
        else:
            self.__dict__['_Component__comps'][name] = value
            self.__dict__[name] = value
            value.set_name(name)

    def __getattr__(self, name):
        if self.__dict__.get(name) is None:
            itf = Interface(self, name)
            self.__dict__['_Component__slave_itfs'][name] = itf
            return itf
        else:
            return self.__dict__[name]

    def get_property(self, name):
        return self.__dict__.get('_Component__properties').get(name)

    def get_comp(self, name):
        comp = self.__dict__.get('_Component__vp_comps').get(name)
        if comp is None:
            comp = self.__dict__.get('_Component__tb_comps').get(name)
        return comp

    def gen(self):
        result = OrderedDict()

        properties = self.__dict__.get('_Component__properties')
        if properties is not None:
            for key, value in properties.items():
                result[key] = value

        comps = list(self.__dict__['_Component__comps'])
        if len(comps) != 0:
            vp_comps = []
            tb_comps = []
            for comp_name in comps:
                comp = self.__dict__['_Component__comps'].get(comp_name)
                if comp.__dict__.get('is_tb_comp'):
                    tb_comps.append(comp_name)
                else:
                    vp_comps.append(comp_name)

            if len(vp_comps) != 0:
                result['vp_comps'] = vp_comps
            if len(tb_comps) != 0:
                result['tb_comps'] = tb_comps

        vp_bindings = []
        tb_bindings = []

        ports = list(self.get_master_itfs().keys()) + list(self.get_slave_itfs().keys())
        if len(ports) != 0:
            result['vp_ports'] = ports            


        for itf_name, slave_itf in self.get_master_itfs().items():
            slave_name = slave_itf.comp.get_name()
            if self.__dict__.get('_Component__comps').get(slave_name) != slave_itf.comp:
                continue
            binding = [
                "self->%s" % (itf_name),
                "%s->%s" % (slave_name, slave_itf.name)
            ]
            if slave_itf.comp.__dict__.get('is_tb_comp') or self.__dict__.get('is_tb_comp'):
                tb_bindings.append(binding)
            else:
                vp_bindings.append(binding)

        for comp_name, comp in self.__dict__['_Component__comps'].items():
            for itf_name, slave_itf in comp.get_master_itfs().items():

                if slave_itf.comp == self:
                    slave_name = 'self'
                else:
                    slave_name = slave_itf.comp.get_name()

                    if self.__dict__.get('_Component__comps').get(slave_name) != slave_itf.comp:
                        continue

                binding = [
                    "%s->%s" % (comp_name, itf_name),
                    "%s->%s" % (slave_name, slave_itf.name)
                ]

                if slave_itf.comp.__dict__.get('is_tb_comp') or self.__dict__.get('is_tb_comp'):
                    tb_bindings.append(binding)
                else:
                    vp_bindings.append(binding)


        if len(vp_bindings) != 0:
            result['vp_bindings'] = vp_bindings

        if len(tb_bindings) != 0:
            result['tb_bindings'] = tb_bindings

        for name, comp in self.__dict__['_Component__comps'].items():
            result[name] = comp.gen()

        return result



class Tb_Component(Component):
    def __init__(self, **kwargs):
        super(Tb_Component, self).__init__(**kwargs)

        self.__dict__['is_tb_comp'] = True
