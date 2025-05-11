from rest_framework import serializers, exceptions, status
from django.utils import timezone
from datetime import datetime

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
 
    def create(self, validated_data):
        appointment_start_time = validated_data.get("start_time")
        appointment_end_time = validated_data.get("end_time")

        # check start, end conditions
        if not 120 <= ((appointment_end_time - appointment_start_time).seconds / 60) <= 300:
            raise exceptions.PermissionDenied("end_time should be bigger than start_time, and the difference between the start and the end is between 120 and 300 minutes")
        
        # check if reserved before
        
        overlapping = Appointment.objects.filter(
                start_time__lt=appointment_end_time,
                end_time__gt=appointment_start_time
        ).exists()
        if overlapping:
            raise exceptions.PermissionDenied("This time slot is already booked", code=status.HTTP_400_BAD_REQUEST)
        return super().create(validated_data)
    
        