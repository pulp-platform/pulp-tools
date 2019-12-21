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

import commands.commands as cmd
from plptools_exec import Cmd_group
import os
import subprocess




@cmd.register_module_cmd
def checkout(self, pkg, builder, cmd_group):

    ret = 0

    if self.scm == 'gitmodule':
        cwd = os.getcwd()
        os.chdir(self.root_dir)
        ret += self.exec_cmd(pkg, "git submodule update --init --recursive %s" % self.path, 'checkout', chdir=False)
        os.chdir(cwd)

    elif self.scm == 'git':
        ret = 0
        if self.url is not None:
            self.dump_msg(self, 'checkout')
            if not os.path.exists(self.abs_path):
                cmd = "git clone %s %s" % (self.url, self.abs_path)
                if os.system(cmd) != 0:
                    return -1
            cwd = os.getcwd()

            os.chdir(self.abs_path)

            # We may get an exception if the version is not specified, just
            # ignore it
            if self.version is not None:
                ret += os.system("git fetch")
                ret += os.system("git checkout %s" % (self.version))

                cmd = 'git log -n 1 --format=format:%H'.split()
                output = subprocess.check_output(cmd)
                if output.decode('utf-8') != self.version:
                    ret += os.system("git pull")

            os.chdir(cwd)

        step = self.steps.get('checkout')
        if step is not None:
            name = '%s:%s:checkout' % (pkg, self.name)
            cmd_group.inc_enqueued()
            cmd = plptools_builder.Builder_command(
                name=name, cmd=step.command, path=self.abs_path,
                env=self.get_env_for_command(pkg))
            cmd.set_callback(callback=cmd_group.dec_enqueued, command=cmd)
            builder.enqueue(cmd=cmd)

    else:
        self.dump_error(pkg, 'Unknown SCM: %s' % self.scm)
        return -1

    return ret



