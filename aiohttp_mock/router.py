from aiohttp_mock.exceptions import *
from aiohttp.client_reqrep import ClientResponse
from aiohttp.multidict import (
    CIMultiDictProxy, MultiDictProxy, MultiDict,
    CIMultiDict
)


class ConnectionRouterHandler(object):

    def __init__(self, uri):
        self.uri = uri
        self._method_handlers = {}

    def add_method_handler(self, method, handler):
        self.method_handlers[method] = handler

    def handle(self, method, request):
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
            response._headers = CIMultiDictProxy({
                'x-agent': 'aiohttp-mock',
                'content-length': 0
            })
            return response


class ConnectionRouter(object):

    def __init__(self):
        self._routes = {}

    def reset(self):
        self._routes = {}

    def add_route(self, uri):
        if uri not in self._routes:
            self._routes[uri] = ConnectionRouterHandler(uri)

    def get_route(self, uri):
        if uri in self._routes:
            return self._routes[uri]
        else:
            raise RouteNotHandled('{0} not handled'.format(uri))

    def add_route_handler(self, uri, method, handler):
        try:
            router = self.get_route(uri)
        except RouteNotHandled:
            self.add_route(uri)
            router = self.get_route(uri)

        router.add_method_handler(method, handler)

    def handle(method, uri, request):
        router = self.get_route(uri)

        return router.handle(method, request)
