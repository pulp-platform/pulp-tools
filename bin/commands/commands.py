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


MODULE_COMMANDS = dict()
PKG_COMMANDS = dict()
PROJECT_COMMANDS = dict()


def register_module_cmd(func):
    MODULE_COMMANDS[func.__name__] = func
    return func

def get_module_cmd(name):
    return MODULE_COMMANDS.get(name)

def register_pkg_cmd(func):
    PKG_COMMANDS[func.__name__] = func
    return func

def get_pkg_cmd(name):
    return PKG_COMMANDS.get(name)

def register_project_cmd(func):
    PROJECT_COMMANDS[func.__name__] = func
    return func

def get_project_cmd(name):
    return PROJECT_COMMANDS.get(name)

