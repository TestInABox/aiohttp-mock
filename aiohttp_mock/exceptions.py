
class AioHttpMockException(Exception):
    pass

class AioHttpMockInvalidSource(AioHttpMockException):
    pass

class ConnectionManagerInvalid(AioHttpMockException):
    pass

class ConnectionManagerUnhandled(AioHttpMockException):
    pass

class RouteNotHandled(AioHttpMockException):
    pass

class ConnectionManagerInvalidHandler(AioHttpMockException):
    pass
