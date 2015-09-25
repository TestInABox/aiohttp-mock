from aiohttp_mock.exceptions import *
from aiohttp_mock.router import ConnectionRouter
from aiohttp.client_reqrep import ClientResponse
from aiohttp.multidict import (
    CIMultiDictProxy, MultiDictProxy, MultiDict,
    CIMultiDict
)


class ConnectionManager(object):

    instance = None
    aiohttp_clientreq_send = None

    status_reason_map = {
    }

    @staticmethod
    def get_instance():
        if ConnectionManager.instance is None:
            return ConnectionManager()

        else:
            return ConnectionManager.instance

    def __init__(self):
        self.managed_urls = []

        self.router = ConnectionRouter()

        if ConnectionManager.instance is None:
            ConnectionManager.instance = self

    def reset(self):
        if ConnectionManager.instance == self:
            ConnectionManager.instance = None

        self.router.reset()

    def is_managed(self, url):
        try:
            self.router.get_route(url)
            return True

        except RouteNotHandled:
            return False

    @staticmethod
    def get_reason_for_status(status_code):
        if status_code in ConnectionManager.status_reason_map:
            return ConnectionManager.status_reason_map[status_code]
        else:
            return 'Unknown'

    @staticmethod
    def make_response(uri, method, status_code=200, body=None, add_headers=None):
        response = ClientResponse(method, uri, host='aiohttp_mock')
        response.status = status_code
        response.reason = ConnectionManager.get_reason_for_status(status_code)
        response._should_code = False
        response._headers = CIMultiDictProxy({
            'x-agent': 'aiohttp-mock',
            'content-length': len(body) if body is not None else 0
        })
        return response
        
    def register(self, uri, method, response):
        # response must be an instance of ClientResponse
        # or must be a callable that takes a request
        # and returns a ClientResponse. make_response can be used
        # to create a ClientResponse if needed
        if not isinstance(response, ClientResponse):
            if not hasattr(response, '__call__'):
                raise ConnectionManagerInvalidHandler
        
        self.route.add_route_handler(method, uri, response)
        
    def intercept(self, request):
        print('Managed URL!')

        uri = request.url
        method = request.method
        try:
            return self.router.handle(method, uri, request)

        except RouteNotHandled:
            raise ConnectionManagerUnhandled('no configured handler')
