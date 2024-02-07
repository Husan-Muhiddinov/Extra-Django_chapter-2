from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
import json
from .models import ChatGroup, Message, Profile
from django.contrib.auth.models import User
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["name"]

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()
        await self.fetch_history()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        time = await self.create_messages(message=text_data_json["message"], sender_id=text_data_json["sender_id"])

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

    @database_sync_to_async
    def create_messages(self, message, sender_id):
        chatgroup = ChatGroup.objects.get(name=self.room_name)
        sender = User.objects.get(id=sender_id)
        message = Message.objects.create(body=message, sender=sender, chatgroup=chatgroup)

        return message.time.strftime("%h-%d  %H:%M")

    async def fetch_history(self):
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
                "sender_id":msg.sender.id,
                "time":msg.time.strftime("%h-%d  %H:%M")
            } for msg in messages
        ]
        return serialized_messages
    


class ProfileListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope["user"].id
        self.group_name = "online_users"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.update_user_profile("online")
        await self.channel_layer.group_send(self.group_name, {"type":"users_list"})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.update_user_profile(datetime.now().strftime("%H:%M, %d-%m-%Y"))
        await self.channel_layer.group_send(self.group_name, {"type":"users_list"})


    async def receive(self):
        pass

    async def users_list(self, event):
        users = await self.all_users()
        await self.send(text_data=json.dumps(users))

    @database_sync_to_async
    def all_users(self):
        profiles = Profile.objects.all()

        serialized_profiles = [
            {
                "full_name": str(profile.user.get_full_name()),
                "status":profile.status,
                "username":profile.user.username,
                "picture":profile.picture.url,
            } for profile in profiles
        ]

        return serialized_profiles
    
    async def update_user_profile(self, status):
        await self.update_from_database(status)

    @database_sync_to_async
    def update_from_database(self, status):
        Profile.objects.filter(user__id=self.user_id).update(status=status)