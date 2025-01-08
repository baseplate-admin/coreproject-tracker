import asyncio
import websockets


async def check_websocket(uri):
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket connection is working.")
            # Send a simple message if needed
            await websocket.send("Hello WebSocket!")
            response = await websocket.recv()
            print(f"Received: {response}")
    except Exception as e:
        print(f"Error connecting to WebSocket: {e}")


# Example usage with a WebSocket URI
uri = "ws://localhost:9000/"  # Replace with your WebSocket URI
asyncio.run(check_websocket(uri))
