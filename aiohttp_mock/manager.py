import aiohttp

class ConnectionManager(object):

    instance = None
    aiohttp_base_connect = None

    def __init__(self):
        self._aiohttp_baseconnector_connect = aiohttp.connector.BaseConnector.connect
        self.managed_urls = []

        if ConnectionManager.instance is None:
            ConnectionManager.instance = self

    def add_url(self, url):
        self.managed_urls.append(url)

    def reset(self):
        if ConnectionManager.instance == self:
            ConnectionManager.instance = None

        self.managed_urls = []

    def is_managed(self, url):
        if url[-1] == '/':
            url = url[:-1]

        return url in self.managed_urls

