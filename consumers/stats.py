from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer


class ShipmentsStatsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("shipments_stats", self.channel_name)
        await self.accept()
        print(f"WebSocket connected: {self.channel_name}")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("shipments_stats", self.channel_name)
        print(f"WebSocket disconnected: {self.channel_name} (code: {close_code})")


    async def stats_update(self, event):
        await self.send_json({"message": "update stats"})
        print(f"Sending message to {self.channel_name}: {event['message']}")
