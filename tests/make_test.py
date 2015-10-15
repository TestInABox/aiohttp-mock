import asyncio
import aiohttp
import aiohttp_mock.manager
import aiohttp_mock.monkey
import unittest

@asyncio.coroutine
def make_url_call(instance, response_code):
    session = aiohttp.ClientSession()
    resp = yield from session.get('http://www.google.com')
    data = yield from resp.read()
    session.close()
    print('make_url_call - resp status is: {0}'.format(resp.status))
    print('make_url_call - resp type is: {0}'.format(type(resp)))
    print('make_url_call - data type is: {0}'.format(type(data)))
    instance.assertEqual(resp.status, response_code)
    return resp


def make_future(loop, coroutine):
    task = loop.create_task(coroutine)



class TestEssential(unittest.TestCase):

    def test_basic(self):

        print('test_basic - Initial Check')
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(make_url_call(self, 200))
        ]
        loop.run_until_complete(asyncio.wait(tasks))

        print('\n\ntest_basic - Monkey Patching')
        aiohttp_mock.monkey.patch()

        tasks = [
            loop.create_task(make_url_call(self, 200))
        ]
        loop.run_until_complete(asyncio.wait(tasks))

        print('\n\ntest_basic - Creating interceptor')
        interceptor = aiohttp_mock.manager.ConnectionManager.get_instance()
        print('test_basic - id mocker: {0}'.format(id(interceptor)))

        tasks = [
            loop.create_task(make_url_call(self, 200))
        ]
        loop.run_until_complete(asyncio.wait(tasks))

        print('\n\ntest_basic - Adding managed url')
        response = aiohttp_mock.manager.ConnectionManager.make_response('http://www.google.com/', 'GET', status_code=405)
        print('test_basic - id mocker: {0}'.format(id(interceptor)))
        interceptor.register('http://www.google.com/', 'GET', response)
        print('test_basic - id mocker: {0}'.format(id(interceptor)))

        tasks = [
            loop.create_task(make_url_call(self, 405))
        ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

        self.assertTrue(False)
