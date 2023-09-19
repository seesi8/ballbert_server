import inspect
import json
import threading

import Backend.websocket as websocket


class WebsocketException(Exception):
    pass


WS_URL = "ws://localhost:8765"


class Websocket_Client:
    def __init__(self) -> None:
        self.url = WS_URL
        self.ws = None
        self.thread = None
        self.routes = dict()
        self.connect()

    def add_route(self, func, name=None):
        pass

    def on_message(self, ws, message):
        pass

    def on_error(self, ws, error):
        pass

    def on_close(self, ws, close_status_code, close_msg):
        pass

    def on_open(self, ws):
        pass

    def connect(self):
        pass

    def send_request(self, request):
        pass

    def send_message(self, type, data=None, **kwargs):
        pass

    def close(self):
        pass
