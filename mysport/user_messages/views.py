from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import ProcessFormView, ModelFormMixin, FormMixin

from .models import *
from .forms import *


class UserMessageChat(ListView, ProcessFormView, FormMixin):
    model = UserMessage
    template_name = 'user_messages/messages_detail.html'
    context_object_name = 'chat_messages'
    form_class = UserMessageCreateForm
    object = None
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        to_user = get_user_model().objects.get(pk=self.kwargs['user_pk'])
        user_messages_list = UserMessage.objects.filter(Q(user_sender=user) | Q(user_recipient=user))
        chat_messages_list = user_messages_list.filter(
            Q(user_sender=to_user) | Q(user_recipient=to_user)).order_by('create_at').reverse()

        self.extra_context = {
            # 'last_five_chats': last_five_chats.items(),
            'to_user': to_user
        }

        return chat_messages_list

    def get_success_url(self):
        return reverse_lazy('user_message_detail', kwargs={'user_pk': self.kwargs['user_pk']})

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            data = form.cleaned_data
            if data.get('content'):
                dict_create = {}
                dict_create['content'] = data.get('content')
                dict_create['user_sender'] = self.request.user
                dict_create['user_recipient'] = get_user_model().objects.get(pk=self.kwargs['user_pk'])
                obj = UserMessage.objects.create(**dict_create)

            return self.form_valid(form)
        return self.form_invalid(form)

    def paginate_queryset(self, queryset, page_size):
        objects = super().paginate_queryset(queryset, page_size)
        object_list = objects[2][:]
        return objects[0], objects[1], object_list[::-1], objects[3]


class UserMessageList(ListView):
    model = UserMessage
    template_name = 'user_messages/messages.html'
    context_object_name = 'last_chats'
    # paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        user_messages_list = UserMessage.objects.filter(Q(user_sender=user) | Q(user_recipient=user))
        last_chats = {}

        for ms in user_messages_list:

            user_recipient = ms.user_recipient
            user_sender = ms.user_sender

            if user_recipient not in last_chats and user_sender not in last_chats:

                key_user = [user_recipient, user_sender][user_recipient == user]
                last_chats[key_user] = ms

        return list(last_chats.items())
