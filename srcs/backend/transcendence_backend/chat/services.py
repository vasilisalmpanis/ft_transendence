from .models            import Chat, Message, chat_model_to_dict, message_model_to_dict
from users.models       import User
from typing             import List, Dict

from channels.layers    import get_channel_layer
from asgiref.sync       import async_to_sync


class ChatService:
    @staticmethod
    def get_chat_id(user : User, user_id : int) -> int:
        """
        Get ID of chat between User and user_id
        :param user: User instance
        :param user_id: int
        :return: int
        """
        chat = Chat.objects.filter(participants__id=user.id).filter(participants__id=user_id).first()
        if chat:
            return chat.id
        return None
    
    @staticmethod
    def create_chat(sender : User, user_id, name=None) -> Dict[str, str]:
        """
        Create chat between two users
        :param user: User instance
        :param user_id: int
        :param name: str
        :return: Chat instance
        """
        if sender.id == user_id:
            raise ValueError("Cannot create chat with self")
        receiver = User.objects.get(id=user_id)
        if not receiver:
            raise ValueError("Receiver not found")
        if not sender.friends.filter(id=user_id).exists():
            raise ValueError("User is not your friend")
        if not name:
            name = f"{sender.username} and {receiver.username} chat"
        chat = Chat.objects.create(name=name)
        chat.participants.add(sender)
        chat.participants.add(receiver)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('0', {
            'type': 'manager.update',
            'status': 'chat_id {chat.id} created',
            'sender_id': sender.id,
        })
        return chat_model_to_dict(chat, sender)
    
    @staticmethod
    def delete_chat(user : User, chat_id : int) -> Dict[str, str]:
        """
        Delete chat by ID
        :param chat_id: int
        :return: bool
        """
        chat = Chat.objects.filter(id=chat_id, participants__id=user.id).first()
        if chat:
            response = chat_model_to_dict(chat, user)
            chat.delete()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('0', {
                'type': 'manager.update',
                'status': 'chat_id {chat_id} deleted',
                'sender_id': user.id,
            })
            return response
        return {}

    @staticmethod
    def get_chats(user : User, skip : int = 0, limit : int = 10) -> List[Dict[str, str]]:
        """
        Get all chats for a user
        :param user: User instance
        :param skip: int
        :param limit: int
        :return: list
        """
        chats = Chat.objects.filter(participants__id=user.id)[skip:skip+limit]
        return [chat_model_to_dict(chat, user) for chat in chats]


class MessageService:
    @staticmethod
    def create_message(user : User, chat_id : int, content : str) -> Message:
        """
        Send message to chat
        :param user: User instance
        :param chat_id: int
        :param content: str
        :return: bool
        """
        chat = Chat.objects.filter(id=chat_id, participants__id=user.id).first()
        if chat:
            message = Message.objects.create(
                chat=chat,
                sender=user,
                content=content
            )
            return message_model_to_dict(message)
        return None

    @staticmethod
    def read_messages(user : User, message_ids : List[int], chat_id: int) -> int:
        """
        Mark message as read
        :param user: User instance
        :param message_id: int
        :return: Number of unread messages for this user
        """
        messages = Message.objects.filter(id__in=message_ids, chat__id=chat_id, chat__participants__id=user.id)
        for message in messages:
            if message.sender != user:
                message.read = True
                message.save()
        unread_chat_messages = Message.objects.filter(chat__id=chat_id, read=False, chat__participants__id=user.id).exclude(sender=user.id).count()
        return unread_chat_messages

    @staticmethod
    def get_messages(chat_id : int, skip=0, limit=10) -> list:
        messages = Message.objects.filter(chat__id=chat_id).order_by("-timestamp")[skip:skip+limit]
        return [
            message_model_to_dict(message)
            for message in messages
        ]

    @staticmethod
    def get_messages_by_state(chat_id : int, state : str, user : User) -> List[Dict[str, str]]:
        """
        Get all messages of "state" for chat for user me
        :param user: User instance
        :param chat_id: int
        :param state: str
        :return: list
        """
        messages = Message.objects.filter(chat__id=chat_id, read=state, chat__participants__id=user.id)
        return [
            message_model_to_dict(message) 
            for message in messages]
