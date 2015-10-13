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
from aiohttp.client_reqrep import ClientResponse
from aiohttp_mock.utils import cidict


class ConnectionRouterHandler(object):
    """Handler for a given URI

    This class handles all the HTTP Verbs for a given URI.
    """

    def __init__(self, uri):
        self.uri = uri
        self._method_handlers = {}

    def add_method_handler(self, method, handler):
        """Add or update the Method handler

        :param method: string - HTTP Verb
        :param handler: ClientResponse object or callable
                        that will be used to respond to
                        the request
        """
        self._method_handlers[method] = handler

    def handle(self, method, request):
        """Handle a request

        :param method: string - HTTP Verb
        :param request: aiohttp.client_reqrep.ClientRequest

        :returns: aiohttp.client_reqrep.ClientResponse

        Note: Returns an HTTP 405 if the HTTP Verb is not
              supported
        """

        # If the method has a registered handler, then
        # return it. Otherwise, create a 405 response
        if method in self._method_handlers:
            handler = self._method_handlers[method]
            # Callbacks must be callables
            if hasattr(handler, '__call__'):
                return self._method_handlers[method](_request)
            else:
                return handler

        else:
            response = ClientResponse(method, self.uri, host='aiohttp_mock')
            response.status = 405
            response.reason = 'Method Not Supported'
            response._should_close = False
            response._headers = cidict({
                'x-agent': 'aiohttp-mock',
                'content-length': 0
            })
            return response


class ConnectionRouter(object):

    def __init__(self):
        self._routes = {}

    def reset(self):
        """Reset all the routes
        """
        self._routes = {}

    def add_route(self, uri):
        """Add a route to be managed

        :param uri: string - URI to be handled
        """
        if uri not in self._routes:
            self._routes[uri] = ConnectionRouterHandler(uri)

    def get_route(self, uri):
        """Access the handler for a URI

        :param uri: string - URI of the request

        :returns: ConnectionRouterHandler instance managing the route
        :raises: RouteNotHandled if the route is not handled
        """
        if uri in self._routes:
            return self._routes[uri]
        else:
            raise RouteNotHandled('{0} not handled'.format(uri))

    def add_route_handler(self, uri, method, handler):
        """Add an HTTP Verb handler to the URI

        :param uri: string - URI that the handler is for
        :param method: string - HTTP Verb the handler is for
        :param handle: ClientResponse or callable that will handle the request
        """
        try:
            router = self.get_route(uri)
        except RouteNotHandled:
            self.add_route(uri)
            router = self.get_route(uri)

        router.add_method_handler(method, handler)

    def handle(self, method, uri, request):
        """Handle a request and create a response

        :param method: string - HTTP Method the request is calling
        :param uri: string - URI the request is for
        :param request: aiohttp.client_reqreq.ClientRequest instance
                        for the request

        :returns: aiohttp.client_reqrep.ClientResponse instance
        :raises: RouteNotHandled if the route is not handled
        """
        router = self.get_route(uri)

        return router.handle(method, request)
