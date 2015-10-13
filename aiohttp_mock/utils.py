# Copyright 2015 by Benjamen R. Meyer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class cidict(dict):
    """Simple case-insensitive dict

    All keys are stored as lower-case.
    All values can be accessed in any-case.
    """

    def __setitem__(self, key, value):
        key = key.lower()
        super(cidict, self).__setitem__(key, value)

    def __getitem__(self, key):
        key = key.lower()
        return super(cidict, self).__getitem__(key)

    def __delitem__(self, key):
        key = key.lower()
        return super(cidict, self).__delitem__(key)

    def __contains__(self, key):
        key = key.lower()
        return super(cidict, self).__contains__(key)
