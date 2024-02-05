import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["name"]

        await self .channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()



    async def disconnect(self, close_code):
        await self .channel_layer.group_discard(self.room_name, self.channel_name)




    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_name, 
            {
                "type":"chat_message",
                "message":text_data_json['message'],
                "sender_id":text_data_json["sender_id"],
                "time":datetime.now().strftime("%h-%d  %H:%M")
            }
        )

    async def chat_message(self, event):

        await self.send(
            text_data=json.dumps(
                {
                    "message":event["message"],
                    "sender_id":event["sender_id"],
                    "time":event["time"],
                }
            )
        )