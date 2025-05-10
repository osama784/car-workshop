from rest_framework import serializers
from django.utils import timezone

from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(
        input_formats=[
            '%Y-%m-%dT%H:%M:%S%z',  # ISO 8601
            '%Y-%m-%d %H:%M:%S',     # Without timezone
            '%Y-%m-%d',              # Date-only
            '%d/%m/%Y %H:%M'         # European format
        ],
        default_timezone=timezone.get_current_timezone()
    )
    end_time = serializers.DateTimeField(
        input_formats=[
            '%Y-%m-%dT%H:%M:%S%z',  # ISO 8601
            '%Y-%m-%d %H:%M:%S',     # Without timezone 
            '%Y-%m-%d',              # Date-only
            '%d/%m/%Y %H:%M'         # European format
        ],
        default_timezone=timezone.get_current_timezone()
    )

    class Meta:
        model = Appointment
        fields = [
            'customer', 
            'start_time', 
            'end_time', 
            'car_brand',
            'car_model',
            'car_year',
            'problem_type',
            'description',
            'cost',
            ]
 
        