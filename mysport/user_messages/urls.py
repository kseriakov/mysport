from django.urls import path

from .views import *


urlpatterns = [
    path('', UserMessageList.as_view(), name='user_message'),
    path('chat/<int:user_pk>/', UserMessageChat.as_view(), name='user_message_detail'),
]