from autobahn.twisted.websocket import WebSocketServerProtocol


# WebSocket Protocol
class WebSocketServer(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"WebSocket connection from {request.peer}")

    def onMessage(self, payload, isBinary):
        msg = payload.decode() if not isBinary else payload
        print(f"WebSocket message received: {msg}")
        self.sendMessage(payload, isBinary)  # Echo back
