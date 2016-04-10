__author__ = 'antigrav'
import time
from threading import Lock
from tornado import httpclient, gen


class CacheControl():

    TIMEOUT = 60

    class Page(object):
        def __init__(self, page_body=None, request=None,):
            self.timestamp = time.time()
            self.lock = Lock()
            self.path = request.url
            self.page_body = page_body

    def __init__(self):
        self.pages_storage = dict()

    @gen.coroutine
    def get_page(self, request):
        page = self.pages_storage.get(request.url, None)
        if not page or (time.time() - page.timestamp >= 60):
            new_page = yield self._update_page(request, page, new_flag=not bool(page))
            raise gen.Return(new_page)
        else:
            raise gen.Return(page.page_body)

    @gen.coroutine
    def _update_page(self, request, page, new_flag):
        lock_owner = False
        try:
            if not new_flag:
                lock_owner = True
                page.lock.acqiere()
            client = httpclient.AsyncHTTPClient()
            response = yield client.fetch(request)
            self.pages_storage[request.url] = self.Page(response, request)
            raise gen.Return(response)
        except httpclient.HTTPError as err:
            raise gen.Return(err.message)
        finally:
            if not new_flag and lock_owner:
                page.lock.release()
