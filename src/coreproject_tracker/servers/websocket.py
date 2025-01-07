import json
from twisted.protocols.basic import LineReceiver
from twisted.internet import protocol


class WebSocketServer(LineReceiver):
    def __init__(self, opts=None):
        self.opts = opts or {}
        self.socket = None
        self.ip = None
        self.port = None
        self.addr = None
        self.headers = None

    def connectionMade(self):
        # This is called when the connection is established
        self.socket = self.transport
        self.ip = self.transport.getPeer().host
        self.port = self.transport.getPeer().port

    def connectionLost(self, reason):
        # Clean up when the connection is lost
        self.socket = None
        self.ip = None
        self.port = None
        self.addr = None
        self.headers = None

    def lineReceived(self, line):
        # This method is called when data is received
        try:
            params = json.loads(line)  # may raise ValueError if the JSON is malformed
            params["type"] = "ws"
            params["socket"] = self.socket

            # Handle WebSocket request
            params = self.handle_ws_request(params)
            self.sendResponse(params)

        except ValueError as e:
            self.sendError(str(e))

    def handle_ws_request(self, params):
        pass

    def sendResponse(self, params):
        # Send a response back to the client (e.g., via WebSocket)
        pass

    def sendError(self, error_message):
        # Send an error message back to the client
        pass


class WebSocketFactory(protocol.ServerFactory):
    protocol = WebSocketServer

    def __init__(self, opts=None):
        self.opts = opts or {}

    def buildProtocol(self, addr):
        return WebSocketServer(self.opts)
