from django import template
from django.db.models import Q

from ..models import *

register = template.Library()


@register.simple_tag(takes_context=True)
def show_new_messages(context):
    user = context.get('user')

    # Помечаем сообщения как прочитанные, при просмотре чата
    if 'chat_messages' in context:
        chat_messages = context.get('chat_messages')
        print(chat_messages)
        size = len(chat_messages)
        # Начинаем перебирать с конца, чтобы не идти по старым, просмотренным сообщениям
        for i in range(size - 1, -1, -1):
            if chat_messages[i].read or chat_messages[i].user_sender == user:
                break
            elif chat_messages[i].user_recipient == user:
                chat_messages[i].read = True
                chat_messages[i].save()

    # Получаем 5 последних непрочитанных чатов
    new_messages = UserMessage.objects.filter(Q(user_recipient=user) & Q(read=False))
    last_five_chats = {}
    for ms in new_messages:

        if len(last_five_chats) == 5:
            break

        user_recipient = ms.user_recipient
        user_sender = ms.user_sender

        if user_recipient not in last_five_chats and user_sender not in last_five_chats:
            key_user = [user_recipient, user_sender][user_recipient == user]
            last_five_chats[key_user] = ms

    return len(new_messages), last_five_chats
