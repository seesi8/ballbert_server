import asyncio
import websockets

async def echo(websocket, path):
    try:
        async for message in websocket:
            # Echo the received message back to the client
            print(message)
            await websocket.send(message)
    except websockets.ConnectionClosed:
        pass  # Connection was closed, ignore

if __name__ == "__main__":
    host = "0.0.0.0"  # Listen on all available network interfaces
    port = 8765  # Use a port of your choice

    # Create a WebSocket server
    server = websockets.serve(echo, host, port)

    print(f"WebSocket server is running on {host}:{port}")

    # Start the server
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
