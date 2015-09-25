import asyncio
import aiohttp
import aiohttp_mock.manager
import aiohttp_mock.monkey

@asyncio.coroutine
def run_test():
    session = aiohttp.ClientSession()
    resp = yield from session.get('http://www.google.com')
    data = yield from resp.read()
    session.close()
    print('resp type is: {0}'.format(type(resp)))
    #print(dir(resp))
    print('data type is: {0}'.format(type(data)))

asyncio.get_event_loop().run_until_complete(run_test())

print('Monkey Patching')
aiohttp_mock.monkey.patch()

asyncio.get_event_loop().run_until_complete(run_test())

print('Creating interceptor')
interceptor = aiohttp_mock.manager.ConnectionManager()

asyncio.get_event_loop().run_until_complete(run_test())

print('Adding managed url')
#interceptor.add_url('http://www.google.com')
response = aiohttp_mock.manager.ConnectionManager.make_response('http://www.google.com/', 'GET', status_code=405)
interceptor.register('http://www.google.com', 'GET', response)

asyncio.get_event_loop().run_until_complete(run_test())
