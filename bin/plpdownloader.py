
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

import os
import plplink
from padframe.padframe import Padframe

downloader_pattern = """#!/usr/bin/env python3

# This file has been auto-generated and can be used for downloading the SDK it has
# been generated for.

import os
import tarfile
import os.path
import argparse


src="59b44701b6ac8390a97936cbd049256fc2917212"

artefacts=[
  {artefacts}
]

envFileStrCsh=[
  "setenv PULP_PKG_PATH @PULP_PKG_HOME@/pkg",
  "setenv PULP_OR1K_GCC_VERSION 1.2.7",
  "setenv OR1K_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/or1k_gcc/1.2.7",
  "setenv PULP_OR10NV2_GCC_VERSION 2.0.15",
  "setenv OR10NV2_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/or10nv2_gcc/2.0.15",
  "setenv PULP_RISCVV0_GCC_VERSION 2.3.11",
  "setenv RISCVV0_GCC_VERSION 2.3.11",
  "setenv RISCVV0_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/riscvv0_gcc/2.3.11",
  "setenv PULP_RISCV_GCC_VERSION 2.3.2", "setenv RISCV_GCC_VERSION 2.3.2",
  "setenv RISCV_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/riscv_gcc/2.3.2",
  "setenv PULP_RISCVV2_GCC_VERSION 2.3.11",
  "setenv RISCVV2_GCC_VERSION 2.3.11",
  "setenv RISCVV2_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/riscvv2_gcc/2.3.11",
  "setenv PULP_RISCVV2_HARDFLOAT_GCC_VERSION 2.3.13",
  "setenv RISCVV2_HARDFLOAT_GCC_VERSION 2.3.13",
  "setenv RISCVV2_HARDFLOAT_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/riscvv2_hardfloat_gcc/2.3.13",
  "setenv PULP_RISCVSLIM_GCC_VERSION 2.3.12", "setenv RISCVSLIM_GCC_VERSION 2.3.12", "setenv RISCVSLIM_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/riscvslim_gcc/2.3.12",
  "setenv PULP_RISCVSLIM16_GCC_VERSION 2.3.11", "setenv RISCVSLIM16_GCC_VERSION 2.3.11", "setenv RISCVSLIM16_GCC_TOOLCHAIN @PULP_PKG_HOME@/pkg/riscvslim16_gcc/2.3.11",
  "setenv PULP_SDK_VERSION 2018.01.2", "setenv PULP_SDK_HOME @PULP_PKG_HOME@/pkg/sdk/2018.01.2",
  "if ( -e @PULP_PKG_HOME@/pkg/sdk/2018.01.2/setup.csh ) source @PULP_PKG_HOME@/pkg/sdk/2018.01.2/setup.csh", ""]

envFileStr=["export PULP_PKG_PATH=@PULP_PKG_HOME@/pkg", "export PULP_OR1K_GCC_VERSION=1.2.7", "export OR1K_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/or1k_gcc/1.2.7", "export PULP_OR10NV2_GCC_VERSION=2.0.15", "export OR10NV2_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/or10nv2_gcc/2.0.15", "export PULP_RISCVV0_GCC_VERSION=2.3.11", "export RISCVV0_GCC_VERSION=2.3.11", "export RISCVV0_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/riscvv0_gcc/2.3.11", "export PULP_RISCV_GCC_VERSION=2.3.2", "export RISCV_GCC_VERSION=2.3.2", "export RISCV_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/riscv_gcc/2.3.2", "export PULP_RISCVV2_GCC_VERSION=2.3.11", "export RISCVV2_GCC_VERSION=2.3.11", "export RISCVV2_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/riscvv2_gcc/2.3.11", "export PULP_RISCVV2_HARDFLOAT_GCC_VERSION=2.3.13", "export RISCVV2_HARDFLOAT_GCC_VERSION=2.3.13", "export RISCVV2_HARDFLOAT_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/riscvv2_hardfloat_gcc/2.3.13", "export PULP_RISCVSLIM_GCC_VERSION=2.3.12", "export RISCVSLIM_GCC_VERSION=2.3.12", "export RISCVSLIM_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/riscvslim_gcc/2.3.12", "export PULP_RISCVSLIM16_GCC_VERSION=2.3.11", "export RISCVSLIM16_GCC_VERSION=2.3.11", "export RISCVSLIM16_GCC_TOOLCHAIN=@PULP_PKG_HOME@/pkg/riscvslim16_gcc/2.3.11", "export PULP_SDK_VERSION=2018.01.2", "export PULP_SDK_HOME=@PULP_PKG_HOME@/pkg/sdk/2018.01.2", "if [ -e @PULP_PKG_HOME@/pkg/sdk/2018.01.2/setup.sh ]; then . @PULP_PKG_HOME@/pkg/sdk/2018.01.2/setup.sh; fi", ""]

pkg=["sdk", "2018.01.2"]

parser = argparse.ArgumentParser(description='PULP downloader')

parser.add_argument('command', metavar='CMD', type=str, nargs='*',
                   help='a command to be execute')

parser.add_argument("--path", dest="path", default=None, help="Specify path where to install packages and sources")

args = parser.parse_args()

if len(args.command ) == 0:
    args.command = ['get']

if args.path != None:
    path = os.path.expanduser(args.path)
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)

for command in args.command:

    if command == 'get' or command == 'download':

        dir = os.getcwd()

        if command == 'get':
            if not os.path.exists('pkg'): os.makedirs('pkg')

            os.chdir('pkg')

        for artefactDesc in artefacts:
            artefact = artefactDesc[0]
            path = os.path.join(dir, artefactDesc[1])
            urlList = artefact.split('/')
            fileName = urlList[len(urlList)-1]

            if command == 'download' or not os.path.exists(path):

                if os.path.exists(fileName):
                    os.remove(fileName)

                if os.system('wget --no-check-certificate %s' % (artefact)) != 0:
                    exit(-1)

                if command == 'get':
                    os.makedirs(path)
                    t = tarfile.open(os.path.basename(artefact), 'r')
                    t.extractall(path)
                    os.remove(os.path.basename(artefact))

        os.chdir(dir)

    if False: #command == 'get' or command == 'download' or command == 'env':

        if not os.path.exists('env'):
            os.makedirs('env')

        filePath = 'env/env-%s-%s.sh' % (pkg[0], pkg[1])
        with open(filePath, 'w') as envFile:
            envFile.write('export PULP_ENV_FILE_PATH=%s\\n' % os.path.join(os.getcwd(), filePath))
            envFile.write('export PULP_SDK_SRC_PATH=%s\\n' % os.environ.get("PULP_SDK_SRC_PATH"))
            for env in envFileStr:
                envFile.write('%s\\n' % (env.replace('@PULP_PKG_HOME@', os.getcwd())))
            envFile.write('if [ -e "$PULP_SDK_SRC_PATH/init.sh" ]; then source $PULP_SDK_SRC_PATH/init.sh; fi')

        filePath = 'env/env-%s-%s.csh' % (pkg[0], pkg[1])
        with open(filePath, 'w') as envFile:
            envFile.write('setenv PULP_ENV_FILE_PATH %s\\n' % os.path.join(os.getcwd(), filePath))
            envFile.write('setenv PULP_SDK_SRC_PATH %s\\n' % os.environ.get("PULP_SDK_SRC_PATH"))
            for env in envFileStrCsh:
                envFile.write('%s\\n' % (env.replace('@PULP_PKG_HOME@', os.getcwd())))
            envFile.write('if ( -e "$PULP_SDK_SRC_PATH/init.sh" ) then source $PULP_SDK_SRC_PATH/init.sh; endif')

    if command == 'src':

        if os.path.exists('.git'):
            os.system('git checkout %s' % (src))
        else:
            os.system('git init .')
            os.system('git remote add -t \* -f origin git@kesch.ee.ethz.ch:pulp-sw/pulp_pipeline.git')
            os.system('git checkout %s' % (src))

"""

class Downloader(object):

    def __init__(self, pkg, configs, distrib):
        self.pkg = pkg
        self.configs = configs
        self.distrib = distrib

    def gen(self, file):

        artifacts = []


        packages = [self.pkg] + self.pkg.get_exec_deps_for_configs(self.configs)

        for dep in packages:

            artifact_path = self.pkg.project.artifactory.get_artifact_path(
                dep.get_artifact_path(self.distrib))

            for path in self.pkg.project.artifactory.get_artifact_path(
                dep.get_artifact_path(self.distrib)):

                artifact_info = '["%s", "%s"]' % (path, dep.get_path())
                artifacts.append(artifact_info)

        file.write(downloader_pattern.format(
            artefacts=',\n  '.join(artifacts)))
