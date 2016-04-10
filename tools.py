import time
from threading import Lock
from tornado import httpclient, gen


class ProxyLogic:
    """
    ProxyLogic have main proxy and cache logic

    Usage:
    ProxyLogic().get_page(request), where request - HTTPRequest

    """
    TIMEOUT = 60  # cache timeout

    def __init__(self):
        self.cache_storage = CacheStorage()

    @gen.coroutine
    def get_page(self, request):
        """
        Download page and update cache if needed
        :param request: HTTPRequest
        :return: HTTPResponse
        """

        page = self.cache_storage.get_page(request.url)  # get page by url
        # if page new or too old, page updated in cache_storage, then return to user
        if not page or (time.time() - page.timestamp >= self.TIMEOUT):
            new_page = yield self._update_page(request, page, need_answer=True)
            raise gen.Return(new_page)
        # if cache_storage have actual cache for that page
        else:
            self._update_page(request, page, need_answer=False)  # Future object. Page will be updated async
            raise gen.Return(page.page_body)

    @gen.coroutine
    def _update_page(self, request, page, need_answer):
        new_flag = not bool(page)
        try:
            # update new or not updated now page
            if new_flag or page.lock.acqiere(False):
                client = httpclient.AsyncHTTPClient()
                response = yield client.fetch(request, raise_error=False)
                if response.code in range(200, 300):
                    self.cache_storage.set_page(response, request)
                raise gen.Return(response)
            # wait for updating end, if answer needed
            elif need_answer:
                page.lock.acqiere(True)
                raise gen.Return(self.cache_storage.get_page(request.url))
        finally:
            if page.lock.locked():
                page.lock.release()


class CacheStorage:
    """
    Simple in memory cache storage. Can be replaced by some database
    """
    class Page(object):
        """
        Object stored by CacheStorage
        """
        def __init__(self, page_body):
            self.timestamp = time.time()
            self.lock = Lock()
            self.page_body = page_body

    def __init__(self):
        self.pages_storage = dict()

    def get_page(self, url):
        """
        :param url: page url
        :return: Page instance
        """
        return self.pages_storage.get(url, None)

    def set_page(self, response, request):
        """
        :param response: server response, page body
        :param request: request to server
        """
        self.pages_storage[request.url] = self.Page(response)
