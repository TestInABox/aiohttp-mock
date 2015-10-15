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

from aiohttp_mock.exceptions import *
import aiohttp


def send_interceptor(*args):
    """Interceptor for aiohttp.client_reqrep.ClientRequest.send()
    """

    # Access the aiohttp-mock framework
    # if the URI is managed by it then pass it off to the framework
    import aiohttp_mock.manager
    mocker = aiohttp_mock.manager.ConnectionManager.get_instance()
    print('send_interceptor() - Found Mocker - id {0}'.format(id(mocker)))
    if mocker is not None:
        print('send_interceptor() - Checking URL: {0}'.format(args[0].url))
        if mocker.is_managed(args[0].url):
            print('send_interceptor() - URI is managed')
            try:
                print('send_interceptor() - Attempting to intercept URI')
                return mocker.intercept(args[0])
            except ConnectionManagerUnhandled:
                print('ConnectionManager not configured.')
                pass

    # Default to the original implementation
    return aiohttp_mock.manager.ConnectionManager.aiohttp_clientreq_send(*args)


def patch():
    """Python monkey patch aiohttp so calls are intercepted by aiohttp-mock
    """
    import aiohttp_mock.manager

    # just like gevent...use python's overwrite functionality to switch out the calls
    patches = [
        (aiohttp.client_reqrep.ClientRequest, 'send', aiohttp_mock.manager.ConnectionManager, 'aiohttp_clientreq_send', send_interceptor)
    ]

    for source, source_attr, dest, dest_attr, handler in patches:
        if getattr(source, source_attr) != handler:
            setattr(dest, dest_attr, getattr(source, source_attr))
        setattr(source, source_attr, handler)
