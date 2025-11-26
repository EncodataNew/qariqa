import websockets
import asyncio

async def test_ocpp():
    uri = "ws://localhost:9000/test_chargepoint"
    async with websockets.connect(uri) as websocket:
        await websocket.send('{"action": "Authorize", "idTag": "12345"}')
        response = await websocket.recv()
        print(response)

asyncio.run(test_ocpp())
