
from __future__ import absolute_import
from tornado import gen, httpclient, web
import  tornado
import time
from urllib.parse import urlparse


class ProxyHandler(web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = self.application.cache  # tools.CacheControl
        for key, value in self.application.uri_data.items():
            setattr(self, key, value)
        # uri_data = dict(uri=uri.strip("/"),
        #                      host=parsed.hostname,
        #                      outer_port=parsed.port,


    @gen.coroutine
    def post(self, path):
        yield self._main_handler(path)

    @gen.coroutine
    def get(self, path):
        yield self._main_handler(path)

    @gen.coroutine
    def _main_handler(self, path):
        self.outer_port = 80
        body = self.request.body if self.request.body else None
        self.request.headers['Host'] = "{}:{}".format(self.host, self.outer_port)
        opt = dict(
            method=self.request.method,
            body=body,
            headers=self.request.headers,
        )

        req = httpclient.HTTPRequest("%s/%s" % (self.uri, path), **opt)

        response = yield self.cache.get_page(req)
        if isinstance(response, str):
            self.write(response)
        else:
            self.set_status(response.code, response.reason)
            self._headers = tornado.httputil.HTTPHeaders() # clear tornado default header

            for header, value in response.headers.get_all():
                if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                    self.add_header(header, value)
            if response.body:
                self.set_header('Content-Length', len(response.body))
                self.write(response.body)
            # self.finish(response.decode('cp1251'))
        self.finish()
