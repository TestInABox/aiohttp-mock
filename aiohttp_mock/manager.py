from aiohttp_mock.exceptions import *
from aiohttp_mock.router import ConnectionRouter
from aiohttp.client_reqrep import ClientResponse


class ConnectionManager(object):

    instance = None
    aiohttp_clientreq_send = None

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
    def make_response(uri, method, body):
        response = ClientResponse(method, uri, host='aiohttp_mock')
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
