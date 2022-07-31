from rest_framework import serializers
from .models import *


class WorkoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workout
        fields = ['date', 'content', 'telegram_id']


