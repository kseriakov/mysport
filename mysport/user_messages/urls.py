from django.urls import path

from .views import *


urlpatterns = [
    path('', UserMessageList.as_view(), name='user_message'),
    path('new-chat/', UsersListView.as_view(), name='new_chat'),
    path('chat/<int:user_pk>/', UserMessageChat.as_view(), name='user_message_detail'),
]