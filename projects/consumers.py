# projects/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Project
from accounts.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket pour le chat en temps réel par projet.
    Chaque projet a son propre canal de chat.
    """

    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.room_name  = f'chat_project_{self.project_id}'
        self.user       = self.scope['user']

        # Vérifier que l'utilisateur est membre du projet
        is_member = await self.check_membership()
        if not is_member:
            await self.close()
            return

        # Rejoindre le groupe de chat du projet
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()

        # Annoncer la connexion
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':    'chat_message',
                'message': f'{self.user.first_name or self.user.username} a rejoint le chat',
                'sender':  'Système',
                'time':    timezone.now().strftime('%H:%M'),
                'is_system': True,
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Reçoit un message et le diffuse à tous les membres."""
        data    = json.loads(text_data)
        message = data.get('message', '').strip()

        if not message:
            return

        await self.channel_layer.group_send(
            self.room_name,
            {
                'type':      'chat_message',
                'message':   message,
                'sender':    self.user.first_name or self.user.username,
                'role':      self.user.role,
                'time':      timezone.now().strftime('%H:%M'),
                'is_system': False,
            }
        )

    async def chat_message(self, event):
        """Envoie le message au WebSocket."""
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_membership(self):
        try:
            project = Project.objects.get(pk=self.project_id)
            return (
                self.user == project.created_by or
                self.user in project.members.all()
            )
        except Project.DoesNotExist:
            return False