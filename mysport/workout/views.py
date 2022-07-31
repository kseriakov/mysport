from django.contrib import messages
from django.core.exceptions import FieldError
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, DetailView, UpdateView
from datetime import datetime
import calendar

from django.views.generic.base import TemplateResponseMixin, TemplateView, ContextMixin
from django.views.generic.edit import FormMixin, ProcessFormView, ModelFormMixin

from rest_framework import viewsets
from rest_framework import permissions

from workout_telebot.bot import add_new_workout
from .forms import *
from .serializers import WorkoutSerializer
from users.link_workouts import LinkWorkouts


class WorkoutCreateView(FormView):
    form_class = WorkoutFormCreate
    template_name = 'workout/new_workout.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        content = form.cleaned_data['content']
        user = self.request.user
        add_new_workout(content=content, user=user)
        return super(WorkoutCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(WorkoutCreateView, self).get_context_data(**kwargs)
        current_date = datetime.today()
        context['current_date'] = current_date
        return context

# Отрабатывает перенаправление по нажатию на разные кнопки
    def get_success_url(self):
        success_url = ''
        if 'save_add_w' in self.request.POST:
            success_url = reverse_lazy('create_workout')
        return str(success_url) or str(self.success_url)


def workout_history(request):
    return render(request, 'workout/workout_history.html')


class WorkoutListMonthView(ListView):
    model = Workout
    context_object_name = 'workouts'
    template_name = 'workout/workout_history_month.html'

    def get_queryset(self):
        year = self.kwargs['year']
        month = self.kwargs['month']
        last_day = calendar.monthrange(year, month)[1]
        self.extra_context = {'date': [month, year]}

        # Сортировка тренировок за месяц
        key = 'start'
        if 'end' in self.request.GET:
            key = 'end'
        order = ['-date', 'date'][key == 'start']
        self.extra_context.update({'order': key})

        query = Q(date__gte=f'{year}-{month}-01') & Q(date__lte=f'{year}-{month}-{last_day}') & Q(user_id=self.request.user.id)
        qs = Workout.objects.filter(query).order_by(order)
        return qs


class WorkoutUpdateView(FormMixin, TemplateResponseMixin, ProcessFormView):
    template_name = 'workout/workout_detail.html'
    form_class = WorkoutFormUpdate

    def post(self, request, *args, **kwargs):
        exercises = dict(request.POST).get('exercise')
        if not isinstance(exercises, list):
            exercises = [exercises]

        redirect_url = reverse('history_workout_detail',
                              kwargs={
                                    'year': kwargs.get('year'),
                                    'month': kwargs.get('month'),
                                    'day': kwargs.get('day'),
                                    'pk': kwargs.get('pk'),
                              })
        if not exercises:
            return redirect(redirect_url)
        try:
            obj = Workout.objects.get(pk=kwargs.get('pk'))
            obj.content = {}
            for i, exercise in enumerate(exercises):
                if exercise:
                    obj.content.update({f'Упражнение {i + 1}': exercise})
            obj.save()
        except:
            messages.add_message(request, messages.ERROR, 'Не удалось обновить тренировку, проверьте введенные данные')
            return redirect(redirect_url)

        messages.add_message(request, messages.SUCCESS, 'Изменения успешно применены')
        return redirect(redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        form_class = self.get_form_class()
        # Формируем список форм, одна форма - на одно упражнение
        form_list = []
        obj = Workout.objects.get(pk=pk)
        list_field = tuple(obj.content.values())
        for field in list_field:
            # Получаем форму с заполненными данными
            form_list.append(form_class(initial={'exercise': field}))
        # Передаем в шаблон
        context['forms'] = form_list
        # Также добавляем дату тренировки
        context['w_date'] = obj.date
        return context


# DRF
class WorkoutViewSet(viewsets.ModelViewSet, LinkWorkouts):
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Workout.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        # Сохраняем пользователя
        serializer.save(user=user)
        secure_code_obj = user.securecode
        # Добавляем телеграмм и сливаем в одну тренировку
        self.link_data_user(secure_code_obj)





