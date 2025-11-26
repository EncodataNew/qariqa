import asyncio
from websockets import serve
from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import AuthorizationStatus

class ChargePoint(cp):
    @on("Authorize")
    async def on_authorize(self, id_tag):
        print(f"Authorizing ID: {id_tag}")
        return {"idTagInfo": {"status": AuthorizationStatus.accepted}}

    @on("StartTransaction")
    async def on_start_transaction(self, **kwargs):
        print("Starting charging session.")
        return {"transactionId": 1, "idTagInfo": {"status": AuthorizationStatus.accepted}}

    @on("StopTransaction")
    async def on_stop_transaction(self, **kwargs):
        print("Stopping charging session.")
        return {"idTagInfo": {"status": AuthorizationStatus.accepted}}

async def ocpp_server(websocket, path):
    charge_point_id = path.strip("/")
    charge_point = ChargePoint(charge_point_id, websocket)
    await charge_point.start()
