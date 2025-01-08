from autobahn.twisted.websocket import WebSocketServerProtocol


class WebSocketServer(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connected: {request}")

    def onMessage(self, msg, binary):
        # Handle incoming message
        print(f"Received message: {msg}")
        self.sendMessage(f"Echo: {msg}".encode("utf-8"))

    def onClose(self, wasClean, code, reason):
        print(f"Connection closed: {reason}")
