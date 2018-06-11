#!/usr/bin/env python3


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



class Condor_pool(object):

    def __init__(self):
        machines = [
            'larain.ee.ethz.ch', 'larain3.ee.ethz.ch', 'larain4.ee.ethz.ch', 'larain5.ee.ethz.ch', 'larain6.ee.ethz.ch', 
            #'fenga1.ee.ethz.ch',
            #'pisoc1.ee.ethz.ch', 'pisoc3.ee.ethz.ch', 'pisoc4.ee.ethz.ch', 'pisoc5.ee.ethz.ch', 'pisoc6.ee.ethz.ch'
        ]

        requirements = []

        machines_string = []
        for machine in machines:
            requirements.append('( TARGET.Machine == \"%s\" )' % (machine))

        requirements.append('( TARGET.OpSysAndVer == \"CentOS7\" )')

        print (' || '.join(requirements))

        self.env = {}
        self.env['CONDOR_REQUIREMENTS'] = ' || '.join(requirements)


    def get_cmd(self, cmd):
        return 'condor_run -a "periodic_remove = (RemoteWallClockTime - CumulativeSuspensionTime) > 1" %s' % cmd

    def get_env(self):
        return self.env

