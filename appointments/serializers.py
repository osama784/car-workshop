from rest_framework import serializers, exceptions, status
from django.utils import timezone
from django.db.models import Q

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
            'id',
            'start_time', 
            'end_time', 
            'car_brand',
            'car_model',
            'car_year',
            'problem_type',
            'description',
            'cost',
            'cancelled'
            ]
 
    def create(self, validated_data: dict):
        appointment_start_time = validated_data.get("start_time")
        appointment_end_time = validated_data.get("end_time")

        # check start, end conditions
        if not 120 <= ((appointment_end_time - appointment_start_time).seconds / 60) <= 300:
            raise exceptions.PermissionDenied("end_time should be bigger than start_time, and the difference between the start and the end is between 120 and 300 minutes")
        
        # check if reserved before
        overlapping = Appointment.objects.filter(
            Q(start_time__gte = appointment_start_time,
            start_time__lt = appointment_end_time) |

            Q(end_time__gt = appointment_start_time,
            end_time__lte = appointment_end_time) |

            Q(start_time__lte=appointment_start_time,
            end_time__gte=appointment_end_time),

            cancelled=False
        ).exists()
        if overlapping:
            raise exceptions.PermissionDenied("This time slot is already booked", code=status.HTTP_409_CONFLICT)
        customer = self.context.get("request").user.customer
        validated_data["customer"] = customer
        return super().create(validated_data)
    
        

class AvailableTimesSerializer(serializers.Serializer):
    car_brand = serializers.CharField(max_length=50)
    car_model = serializers.CharField(max_length=50)
    car_year = serializers.IntegerField()
    problem_type = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False)       