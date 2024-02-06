import json
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatGroup, Message
from django.contrib.auth.models import User
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["name"]

        await self .channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.room_name, {"type":"fetch_history"})



    async def disconnect(self, close_code):
        await self .channel_layer.group_discard(self.room_name, self.channel_name)




    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        time = await self.create_messages(message=text_data_json['message'], sender_id=text_data_json['sender_id'])

        await self.channel_layer.group_send(
            self.room_name, 
            {
                "type":"chat_message",
                "message":text_data_json['message'],
                "sender_id":text_data_json["sender_id"],
                "time":time
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

    @ database_sync_to_async
    def create_messages(self, message, sender_id):
        chatgroup = ChatGroup.objects.get(name=self.room_name)
        sender = User.objects.get(id=sender_id)
        message = Message.objects.create(body=message, sender=sender, chatgroup=chatgroup)

        return message.time.strftime("%h-%d  %H:%M")


    async def fetch_history(self, event):
        messages = await self.history_messages()
        for message in messages:
            await self.send(text_data=json.dumps(message))


    @database_sync_to_async
    def history_messages(self):
        chatgroup = ChatGroup.objects.get(name=self.room_name)
        messages = Message.objects.filter(chatgroup=chatgroup)

        serialized_messages = [
            {
                "message":msg.body,
                "sender_id":msg.sender_id,
                "time":msg.time.strftime("%h-%d  %H:%M")
            } for msg in messages
        ]
        return serialized_messages
