from __future__ import absolute_import
from tornado import gen, httpclient, web
import tornado
from urllib.parse import urlparse


class ProxyHandler(web.RequestHandler):
    """
    Simple handler form request, use Proxy from application.proxy, and send response to user
    Supported method's GET, POST
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy = self.application.proxy  # tools.CacheControl
        parsed_uri = urlparse(self.application.uri)
        self.uri = self.application.uri
        self.host = parsed_uri.hostname
        self.outer_port = parsed_uri.port if parsed_uri.port else 80

    @gen.coroutine
    def post(self, path):
        yield self._main_handler(path)

    @gen.coroutine
    def get(self, path):
        yield self._main_handler(path)

    @gen.coroutine
    def _main_handler(self, path):

        # Let`s send user headers
        body = self.request.body if self.request.body else None
        self.request.headers['Host'] = "{}:{}".format(self.host, self.outer_port)
        opt = dict(
            method=self.request.method,
            body=body,
            headers=self.request.headers,
        )
        # Form full request
        req = httpclient.HTTPRequest("%s/%s" % (self.uri, path), **opt)

        # Call proxy instance, for work like caching and fetching
        response = yield self.proxy.get_page(req)

        self.set_status(response.code, response.reason)  # set right status
        self._headers = tornado.httputil.HTTPHeaders()  # clear tornado default header
        # set headers
        for header, value in response.headers.get_all():
            if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                self.add_header(header, value)
        # write body, if answer have it
        if response.body:
            self.set_header('Content-Length', len(response.body))
            self.write(response.body)
        self.finish()
