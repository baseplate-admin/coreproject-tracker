from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from twisted.internet import reactor


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


# Start the WebSocket server
if __name__ == "__main__":
    # Create the WebSocket server factory and bind it to the server address
    factory = WebSocketServerFactory("ws://localhost:9000")
    factory.protocol = WebSocketServer

    reactor.listenTCP(9000, factory)  # Listen on port 9000
    print("WebSocket server running at ws://localhost:9000")
    reactor.run()
