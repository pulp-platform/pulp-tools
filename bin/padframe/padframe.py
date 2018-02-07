
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


from collections import OrderedDict
from math import log

class Profile_pad(object):

    def __init__(self, pad, alternate):
        self.pad = pad
        self.alternate = alternate


class Profile(object):

    def __init__(self, padframe, name, config):
        self.padframe = padframe
        self.name = name
        self.alternates_id = config.get('alternates')
        self.alternates = []
        self.groups = OrderedDict()

        for pad_id in range(0, len(self.alternates_id)):
            alternate_choice = self.alternates_id[pad_id]
            pad = padframe.get_pad_from_id(pad_id)
            alternate = pad.get_alternate(alternate_choice)
            self.alternates.append(alternate)
            for group in alternate.get_groups():
                if self.groups.get(group) is None:
                    self.groups[group] = []
                self.groups[group].append(Profile_pad(pad, alternate))

    def get_groups(self):
        return self.groups

class Alternate(object):

    def __init__(self, config):
        self.name = config.get('name')
        self.groups = config.get('groups')

    def get_groups(self):
        return self.groups


class Pad(object):

    def __init__(self, name, config):
        self.name = name
        self.id = config.get_int('id')
        self.alternates = []
        alternates = config.get('alternates')
        if alternates is not None:
            for alternate in alternates:
                self.alternates.append(Alternate(alternate))

    def get_alternate(self, id):
        return self.alternates[id]


class Padframe(object):

    def __init__(self, config):
        self.config = config
        self.profiles_dict = OrderedDict()
        self.profiles = []
        self.pads_dict = OrderedDict()
        self.pads = []
        self.groups = OrderedDict()
        self.nb_alternate = config.get_int('nb_alternate')

        pads = config.get_config('pads')
        if pads is not None:
            for pad_name, pad_conf in pads.items():
                pad = Pad(pad_name, pad_conf)
                self.pads_dict[pad_name] = pad
                self.pads.append(pad)

        profiles = config.get_config('profiles')
        if profiles is not None:
            for profile_name, profile_conf in profiles.items():
                profile = Profile(self, profile_name, profile_conf)
                self.profiles_dict[profile_name] = profile
                self.profiles.append(profile)

    def get_profile(self, name):
        return self.profiles_dict.get(name)

    def get_profiles(self):
        return self.profiles

    def get_pad_from_id(self, pad_id):
        return self.pads[pad_id]

    def get_pads(self):
        return self.pads


    def gen_rt_conf(self, filepath):
      nb_bit_per_pad = int(log(self.nb_alternate, 2))
      nb_pad = len(self.get_pads())
      nb_pad_per_word = int(32 / nb_bit_per_pad)
      nb_words = int(nb_pad * nb_bit_per_pad / 32)

      with open(filepath, 'w') as file:

          file.write('#include "rt/rt_data.h"\n')
          file.write('\n')

          default_profile = self.get_profile(self.config.get("default_profile"))

          profile_list = [ default_profile ]
          for profile in self.get_profiles():
              if profile != default_profile:
                  profile_list.append(profile)

          for profile in profile_list:
              file.write('static unsigned int __rt_padframe_%s[] = {' % profile.name)
              alternates = profile.alternates_id
              alternates = alternates[8:]
              for word in range(0, nb_words):
                  value = 0
                  for alternate in range (0, nb_pad_per_word):
                      if len(alternates) == 0: break
                      alternate_value = alternates.pop(0)
                      value = value | ( alternate_value << (alternate * nb_bit_per_pad))
                  file.write(' 0x%8.8x,' % value)
              file.write('};\n')
              file.write('\n')

          file.write('rt_padframe_profile_t __rt_padframe_profiles[] = {\n')
          for profile in profile_list:
            file.write('  { .name="%s", .config=__rt_padframe_%s },\n' % (profile.name, profile.name))
          file.write('};\n')
          file.write('\n')
