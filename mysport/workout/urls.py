from django.urls import path
from .views import *

urlpatterns = [
    path('add/', WorkoutCreateView.as_view(), name='create_workout'),
    path('history/', workout_history, name='history_workout'),
    path('history/<int:year>/<int:month>', WorkoutListMonthView.as_view(), name='history_workout_month'),
    path('history/<int:year>/<int:month>', WorkoutListMonthView.as_view(), name='history_workout_month'),
    path('history/<int:year>/<int:month>/<int:day>/<int:pk>/', WorkoutUpdateView.as_view(), name='history_workout_detail'),
]
