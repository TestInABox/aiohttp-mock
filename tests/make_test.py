import asyncio
import aiohttp
import aiohttp_mock.manager
import aiohttp_mock.monkey
import unittest

@asyncio.coroutine
def make_url_call():
    session = aiohttp.ClientSession()
    resp = yield from session.get('http://www.google.com')
    data = yield from resp.read()
    session.close()
    print('resp type is: {0}'.format(type(resp)))
    #print(dir(resp))
    print('data type is: {0}'.format(type(data)))


class TestEssential(unittest.TestCase):

    def test_basic():
        asyncio.get_event_loop().run_until_complete(make_url_call())

        print('Monkey Patching')
        aiohttp_mock.monkey.patch()

        asyncio.get_event_loop().run_until_complete(make_url_call())

        print('Creating interceptor')
        interceptor = aiohttp_mock.manager.ConnectionManager()

        asyncio.get_event_loop().run_until_complete(make_url_call())

        print('Adding managed url')
        response = aiohttp_mock.manager.ConnectionManager.make_response('http://www.google.com/', 'GET', status_code=405)
        interceptor.register('http://www.google.com', 'GET', response)

        asyncio.get_event_loop().run_until_complete(make_url_call())

        self.assertTrue(False)
