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

import asyncio
from aiohttp_mock.exceptions import *
from aiohttp_mock.router import ConnectionRouter
from aiohttp.client_reqrep import ClientResponse
from aiohttp_mock.utils import cidict


class ConnectionManager(object):

    # The official instance
    instance = None

    # The original send method
    aiohttp_clientreq_send = None

    status_reason_map = {
        # 1xx Informational
        100: "Continue",
        101: "Switching Protocol",
        102: "Processing",

        # 2xx Success
        200: "OK",
        201: "Created",
        202: "Accepted",
        203: "Non-Authoritative Information",
        204: "No Content",
        205: "Reset Content",
        206: "Partial Content",
        207: "Multi-Status",
        208: "Already Reported",
        226: "IM used",

        # 3xx Redirection
        300: "Multiple Choices",
        301: "Permanently Moved",
        302: "Found",
        303: "See Other",
        304: "Not Modified",
        305: "Use Proxy",
        306: "Switch Proxy",
        307: "Temporary Redirect",
        308: "Resume Incomplete",

        # 4xx Client Errors
        400: "Bad Request",
        401: "Unauthorized",
        402: "Payment Required",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        406: "Not Acceptable",
        407: "Proxy Authentication Required",
        408: "Request Time-out",
        409: "Conflict",
        410: "Gone",
        411: "Length Required",
        412: "Precondition Failed",
        413: "Payload Too Large",
        414: "Request-URI Too Long",
        415: "Unsupported Media Type",
        416: "Requested Range Not Satisfiable",
        417: "Expectation Failed",
        418: "I'm A Tea Pot",
        419: "Authentication Time-out",
        420: "Method Failure",
        421: "Misdirected Request",
        422: "Unprocessable Entity",
        423: "Locked",
        424: "Failed Dependency",
        426: "Upgrade Required",
        428: "Precondition Required",
        429: "Too Many Requests",
        431: "Request Header Fields Too Large",
        440: "Login Time-out",
        444: "No Response",
        449: "Retry With",
        450: "Blocked By Windows Parental Control",
        451: "Unavailable For Legal Reasons",
        494: "Request Header Too Large",
        495: "Cert Error",
        496: "No Cert",
        497: "HTTP To HTTPS",
        498: "Token Expired/Invalid",
        499: "Client Closed Request",

        # 5xx Server Errors
        500: "Internal Server Error",
        501: "Not Implemented",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Time-out",
        505: "HTTP Version Not Supported",
        506: "Variant Also Negotiates",
        507: "Insufficient Storage",
        508: "Loop Detected",
        509: "Bandwidth Limit Exceeded",
        510: "Not Extended",
        511: "Network Authentication Required",
        520: "Unknown Error",
        522: "Origin Connection Time-out",
        598: "Network Read Time-out Error",
        599: "Network Connect Time-out Error"
    }

    @staticmethod
    def get_instance():
        """Access the global instance or create one

        :returns: instance of ConnectionManager
        """
        print('ConnectionManager.get_instance() - entering - id = {0}'.format(id(ConnectionManager.instance)))
        if ConnectionManager.instance is None:
            return ConnectionManager()

        print('ConnectionManager.get_instance() - returning - id = {0}'.format(id(ConnectionManager.instance)))
        return ConnectionManager.instance

    def __init__(self):
        self.managed_urls = []
        self.router = ConnectionRouter()
        self.globify()

    def __del__(self):
        self.reset()

    def reset(self):
        """Reset Manager State

        Clear the known route supports
        """
        print('ConnectionManager - Resettings - id {0}'.format(id(self)))
        self.deglobify()
        self.router.reset()

    @staticmethod
    def reset_global():
        """Reset the global variables
        """
        print('ConnectionManager.reset_global() - entering - id = {0}'.format(id(ConnectionManager.instance)))
        if ConnectionManager.instance is not None:
            ConnectionManager.instance = None
        print('ConnectionManager.reset_global() - exiting - id = {0}'.format(id(ConnectionManager.instance)))

    def deglobify(self):
        """De-register the global instance

        If this instance is the official global instance then
        reset the global instance
        """
        # if this is the official instance, then clear it
        print('ConnectionManager.deglobify() - self = {0}'.format(id(self)))
        print('ConnectionManager.deglobify() - entering - global id = {0}'.format(id(ConnectionManager.instance)))
        if ConnectionManager.instance == self:
            ConnectionManager.instance = None
        print('ConnectionManager.deglobify() - exiting - global id = {0}'.format(id(ConnectionManager.instance)))

    def globify(self, force=False):
        """Register the global instance

        Attempts to register the instance as the official
        global instance.

        :param force: boolean - if true, forces this instance to become
                                the official one
        """
        # if this is the first instance, then make it the official one
        print('ConnectionManager.globify() - self = {0}'.format(id(self)))
        print('ConnectionManager.globify() - entering - global id = {0}'.format(id(ConnectionManager.instance)))
        if ConnectionManager.instance is None or force == True:
            ConnectionManager.instance = self
        print('ConnectionManager.globify() - exiting - global id = {0}'.format(id(ConnectionManager.instance)))

    def is_managed(self, uri):
        """Checks if the specific URL is managed by the instance

        :param uri: string - URI of the route to check
        :returns: boolean - True if the URL is managed, otherwise False
        """
        print('ConnectionManager.is_managed() - self = {0}'.format(id(self)))
        print('ConnectionManager.is_managed() - checking uri - {0}'.format(uri))
        print('ConnectionManager.is_managed() - router - {0}'.format(id(self.router)))
        if self.router is None:
            print('ConnectionManager.is_managed() - no router')
            return False

        try:
            print('ConnectionManager.is_managed() - checking route')
            self.router.get_route(uri)
            print('ConnectionManager.is_managed() - found route')
            return True

        except RouteNotHandled:
            print('ConnectionManager.is_managed() - no route')
            return False

    @staticmethod
    def get_reason_for_status(status_code):
        """Given an HTTP Status Code get the Associated HTTP Reason

        :param status_code: int - http response status code
        :returns: string - http reason for the status code
        """
        if status_code in ConnectionManager.status_reason_map:
            return ConnectionManager.status_reason_map[status_code]
        else:
            return 'Unknown'

    @staticmethod
    def make_response(uri, method, status_code=200, body=None, add_headers=None):
        """Utility function for building a ClientResponse object

        :param uri: string - URI of the request being handled
        :param method: string - HTTP verb being responded to
        :param status_code: int - HTTP Response Status Code
        :param body: bytes - HTTP Response Body Data
        :param add_headers: dict - HTTP Response Headers

        :returns: ClientResponse instance
        """
        content_length = 0
        if body:
            content_length = len(body)

        response = ClientResponse(method, uri, host='aiohttp_mock')
        response._post_init(loop=asyncio.get_event_loop())
        response._continue = None
        response.status = status_code
        response.reason = ConnectionManager.get_reason_for_status(status_code)
        response.content = body

        response._closed = True
        response._should_code = False
        response._headers = cidict({
            'x-agent': 'aiohttp-mock',
            'content-length': content_length
        })
        return response

    def register(self, uri, method, response):
        """Register a response for a given URI and HTTP Method

        :param uri: string - URI of the request to be handled
        :param method: string - HTTP Verb to be responded to
        :param response: ClientResponse instance to be returned or
                         a callable that returns a ClientResponse instance

        Note: callers can use make_response() to create a static ClientResponse
              object to use for a given URI+Method.
        """
        if not isinstance(response, ClientResponse):
            if not hasattr(response, '__call__'):
                raise ConnectionManagerInvalidHandler

        print('ConnectionManager.register() - self = {0}'.format(id(self)))
        print('ConnectionManager.register() - uri = {0}'.format(uri))
        print('ConnectionManager.register() - method = {0}'.format(method))
        print('ConnectionManager.register() - response = {0}'.format(id(response)))
        self.router.add_route_handler(uri, method, response)
        print('ConnectionManager.register() - route added')

    def intercept(self, request):
        """Request Intercept Handler

        :param request: aiohttp.client_reqrep.ClientRequest the request is for
        :returns: aiohttp.client_reqrep.ClientResponse
        """
        print('ConnectionManager.intercept() - self = {0}'.format(id(self)))
        print('ConnectionManager.intercept() - request = {0}'.format(id(request)))

        uri = request.url
        method = request.method
        try:
            print('ConnectionManager.intercept() - attempting to route')
            return self.router.handle(method, uri, request)

        except RouteNotHandled:
            print('ConnectionManager.intercept() - no route')
            raise ConnectionManagerUnhandled('no configured handler')
