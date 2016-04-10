from __future__ import absolute_import

import os
import threading

from tornado import web, httpserver, ioloop
from urllib.parse import urlparse
from handlers import ProxyHandler
import tools



class Proxy(threading.Thread):
    """

    Simple HTTP proxy.

    After start that thread proxy, user can ask for target URI as 'localhost' via proxy
    Warning! If page on some 'example.com' have some hardcoded lines like 'src=example.com/1.jpg'
    they can`t be proxying (without something like beautiful soup package or router settings).

    Code Usage:

    proxy_instance = Proxy(%URI%, [port])
    proxy_instance.start() #start thread
    proxy_instance.stop()  #stop thread

    """

    ioloop = None


    class TornadoProxyServer(web.Application):

        def __init__(self):
            handlers = [
                # main handler
                (r"/(.*)", ProxyHandler),
            ]
            settings = dict(
                autoreload=True,
                debug=True,
            )
            web.Application.__init__(self, handlers, **settings)

    def __init__(self, uri, port=8809):
        """
        :param uri: path proxying to recourse
        :param port: proxy working port. Default 8809
        """

        self.uri = uri
        parsed = urlparse(uri)
        if parsed.scheme != "http":
            raise self.ProxyException('Bad scheme')
        super(Proxy, self).__init__()
        self.proxy_port = port


    def run(self):

        application = self.TornadoProxyServer()
        application.uri_data = self.uri_data
        application.cache = tools.CacheControl()
        http_server = httpserver.HTTPServer(application)
        http_server.listen(self.proxy_port)
        self.ioloop = ioloop.IOLoop.instance()
        self.ioloop.start()

    def stop(self):
        self.ioloop.stop()

    class ProxyException(Exception):
        pass


if __name__ == "__main__":
    a = Proxy('http://bash.im')
    a.start()
