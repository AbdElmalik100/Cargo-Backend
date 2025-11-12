from channels.generic.websocket import AsyncJsonWebsocketConsumer


class ShipmentsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("shipments", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("shipments", self.channel_name)

    async def shipments_event(self, event):
        await self.send_json({
            "model": event.get("model"),
            "action": event.get("action"),
            "id": event.get("id"),
            "message": event.get("message"),
        })
