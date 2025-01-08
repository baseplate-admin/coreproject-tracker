from autobahn.twisted.websocket import WebSocketServerProtocol


class WebSocketServer(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connecting: {request.peer}")

    def onOpen(self):
        print("WebSocket connection opened")
        self.sendMessage(b"Hello, WebSocket client!")

    def onMessage(self, payload, isBinary):
        print(f"Received message: {payload.decode('utf8')}")
        if isBinary:
            self.sendMessage(b"Binary message received")
        else:
            self.sendMessage(b"Text message received")

    def onClose(self, wasClean, code, reason):
        print(f"WebSocket closed: {reason} (code: {code}, clean: {wasClean})")
