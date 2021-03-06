from __future__ import absolute_import

import threading
import time
from sys import argv

from tornado import web, httpserver, ioloop
from urllib.parse import urlparse
from handlers import ProxyHandler

import tools


class Proxy(threading.Thread):
    """

    Simple HTTP async proxy.

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
            )
            web.Application.__init__(self, handlers, **settings)

    def __init__(self, uri, port=8809):
        """
        :param uri: path proxying to recourse
        :param port: proxy working port. Default 8809
        """

        super().__init__()

        self.uri = uri.strip('/')

        parsed_uri = urlparse(uri)
        if parsed_uri.scheme != "http":
            raise self.ProxyException('Bad scheme')

        self.proxy_port = int(port)

    def run(self):
        application = self.TornadoProxyServer()
        application.uri = self.uri
        application.proxy = tools.ProxyLogic()
        http_server = httpserver.HTTPServer(application)
        http_server.listen(self.proxy_port)
        self.ioloop = ioloop.IOLoop.instance()
        self.ioloop.start()

    def stop(self):
        self.ioloop.stop()

    class ProxyException(Exception):
        pass


if __name__ == "__main__":

    # args = argv[2:]
    args = ("http://bash.im",)

    proxy = Proxy(*args)
    proxy.start()
    while True:
        print("Print 'stop' to stop server")
        command = input()
        if command == 'stop':
            break
        else:
            print('Unknown command')
    proxy.stop()
    while proxy.is_alive():
        time.sleep(0.5)
        print("Proxy stopping... ")
    print("Proxy stop. Goodbye")
