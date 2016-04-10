import pytest
import mock
import time

from .server import Proxy
from .handlers import ProxyHandler
from .tools import ProxyLogic

from tornado import web, ioloop


class TestProxy:
    def test_server(self, monkeypatch):

        monkeypatch.setattr(ioloop, "IOLoop", mock.MagicMock())
        monkeypatch.setattr(web, "Application", mock.MagicMock())
        proxy_server = Proxy("http://some_test")
        proxy_server.start()
        for i in range(30):
            if proxy_server.ioloop:
                break
            else:
                time.sleep(0.1)
        else:
            assert False  # server cant start
        proxy_server.stop()

        assert proxy_server.ioloop.stop.call_count == 1
        assert proxy_server.ioloop.start.call_count == 1
