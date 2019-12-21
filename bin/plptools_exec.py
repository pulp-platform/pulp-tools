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

from twisted.internet import reactor



class Cmd_group(object):

    def __init__(self, callback=None, *kargs, **kwargs):
        self.finished = False
        self.callback = callback
        self.enqueued = 0
        self.kargs = kargs
        self.kwargs = kwargs
        self.status = True

    def set_callback(self, callback=None, *kargs, **kwargs):
        self.callback = callback
        self.kargs = kargs
        self.kwargs = kwargs

    def inc_enqueued(self):
        self.enqueued += 1

    def dec_enqueued(self, command=None):
        self.enqueued -= 1

        if command is not None:
            self.status = self.status and command.status
        if not self.status or self.callback is not None and self.enqueued == 0 and self.finished:
            self.callback(*self.kargs, **self.kwargs)

    def set_finished(self):
        self.finished = True
        if self.enqueued == 0:
          reactor.callLater(0, self.callback, *self.kargs, **self.kwargs)
