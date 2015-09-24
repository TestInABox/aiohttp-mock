import aiohttp

def interceptor(*args):
    '''Interceptor function for the aiohttp.connector.BaseConnector.connect

    This function will intercept connections and redirect to the Transport/Protocol of its choosing.
    '''
    print('Running interceptor')
    request = None
    for arg in args:
        if isinstance(arg, aiohttp.client_reqrep.ClientRequest):
            request = arg
            print('Found request')
            break

    import aiohttp_mock.manager
    if request is not None:
        mocker = aiohttp_mock.manager.ConnectionManager.instance
        if mocker is not None:
            print('Interceptor present')
            if mocker.is_managed(request.url):
                print('Managed URL!')
                # TODO: make our own Connection object that gets returned here

    else:
        print('Bad Request!')

    return aiohttp_mock.manager.ConnectionManager.aiohttp_base_connect(*args)

def patch():
    import aiohttp_mock.manager
    if getattr(aiohttp.connector.BaseConnector, 'connect') != interceptor:
        setattr(aiohttp_mock.manager.ConnectionManager, 'aiohttp_base_connect', getattr(aiohttp.connector.BaseConnector, 'connect'))
    setattr(aiohttp.connector.BaseConnector, 'connect', interceptor)


