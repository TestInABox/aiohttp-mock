from aiohttp_mock.exceptions import *
import aiohttp


def send_interceptor(*args):
    '''Interceptor for aiohttp.client_reqrep.ClientRequest.send()
    '''
    import aiohttp_mock.manager
    mocker = aiohttp_mock.manager.ConnectionManager.instance
    if mocker is not None:
        if mocker.is_managed(args[0].url):
            try:
                return mocker.intercept(args[0])
            except ConnectionManagerUnhandled:
                print('ConnectionManager not configured.')
                pass

    return aiohttp_mock.manager.ConnectionManager.aiohttp_clientreq_send(*args)


def patch():
    import aiohttp_mock.manager

    patches = [
        (aiohttp.client_reqrep.ClientRequest, 'send', aiohttp_mock.manager.ConnectionManager, 'aiohttp_clientreq_send', send_interceptor)
    ]

    for source, source_attr, dest, dest_attr, handler in patches:
        if getattr(source, source_attr) != handler:
            setattr(dest, dest_attr, getattr(source, source_attr))
        setattr(source, source_attr, handler)
