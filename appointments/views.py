from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import status

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Appointment
from .serializers import AppointmentSerializer, AvailableTimesSerializer
from .utils import fetch_prompt_info
from .ai import send_prompt


# Create your views here.


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_appointments(request):
    appointment_status = request.GET.get("status")
    appointments = Appointment.objects.filter(customer=request.user.customer)

    if appointment_status == "pending":
        appointments = appointments.filter(end_time__gt=timezone.now(), cancelled=False)
    if appointment_status == "completed":
        appointments= appointments.filter(end_time__lt=timezone.now(), cancelled=False)
    if appointment_status == "cancelled":
        appointments = appointments.filter(cancelled=True)   
    
    data = AppointmentSerializer(appointments, many=True).data

    return Response(data={"appointments": data, "success": True}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, customer=request.user.customer.pk, pk=pk)
    appointment.cancelled = True
    appointment.save()


    return Response(data={"success": True}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_available_times(request):
    appointments = Appointment.objects.filter(cancelled=False)
    serializer = AvailableTimesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    try :
        fetched_resposne = fetch_prompt_info(send_prompt(serializer.data))
    except:
        return Response(data={"detail": "resend your prompt, it seems that the AI model is Temporarily Unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)    

    # get every day and see available appointments in it, and if there is, any increase the counter
    num_of_appointments = 0
    
    appointment_duration = int(fetched_resposne.get("time to fix"))
    available_dates = {}

    tomorrow = timezone.now() + timezone.timedelta(days=1)
    appointment_start_time = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone.get_current_timezone())
    appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)
    end_of_day = appointment_start_time.replace(hour=18, minute=0, second=0, microsecond=0)
    FRIDAY_ORDER = 4
    for _ in range(11):
        if num_of_appointments >= 10:
            break
        
        if appointment_start_time.weekday() == FRIDAY_ORDER:
            appointment_start_time = appointment_start_time.replace(hour=8, minute=0) + timezone.timedelta(days=1)
            appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)
            end_of_day = appointment_start_time.replace(hour=18, minute=0, second=0, microsecond=0)
            continue
        
        appointments_for_day = appointments.filter(start_time__date=appointment_start_time.date())
        current_day_hours = []

        while appointment_end_time <= end_of_day:
            overlapping = appointments_for_day.filter(
                Q(start_time__gte = appointment_start_time,
                start_time__lt = appointment_end_time) |

                Q(end_time__gt = appointment_start_time,
                end_time__lte = appointment_end_time) |

                Q(start_time__lte=appointment_start_time,
                end_time__gte=appointment_end_time)
            ).exists()
            
            if overlapping:
                last_appointment = appointments_for_day.filter(end_time__gt=appointment_start_time).first()
                if last_appointment:
                    appointment_start_time = last_appointment.end_time.astimezone(timezone.get_current_timezone())
                else:
                    appointment_start_time = appointment_end_time.astimezone(timezone.get_current_timezone())
                
                appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)
            else:
                current_day_hours.append(f'{appointment_start_time.hour}:{appointment_start_time.minute}:00 to {appointment_end_time.hour}:{appointment_end_time.minute}:00')

                num_of_appointments += 1
                if num_of_appointments >= 10:
                    break
                
                appointment_start_time = appointment_end_time.astimezone(timezone.get_current_timezone())
                appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)

                

        # prevent any empty keys
        if current_day_hours:
            available_dates[f"{appointment_start_time.year}-{appointment_start_time.month}-{appointment_start_time.day}"] = current_day_hours

        # change the appointment_start_time to the start of the next day (8:00 am)
        appointment_start_time = appointment_start_time.replace(hour=8, minute=0) + timezone.timedelta(days=1)
        appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)
        end_of_day = appointment_start_time.replace(hour=18, minute=0, second=0, microsecond=0)

    return Response(data= {
        'appointments': available_dates,
        'ai_response': fetched_resposne.get("possibilities"),
        "cost": int(fetched_resposne.get("cost")),
        "duration": appointment_duration
    }, status=status.HTTP_200_OK)    


class AppointmentCreateAPIView(CreateAPIView):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():  # Start atomic transaction
                # Lock overlapping rows to prevent concurrent bookings
                start_time = serializer.validated_data.get("start_time")
                end_time = serializer.validated_data.get("end_time")

                # Check for overlaps with locked rows
                overlapping = Appointment.objects.select_for_update().filter(
                    Q(start_time__gte = start_time,
                    start_time__lt = end_time) |

                    Q(end_time__gt = start_time,
                    end_time__lte = end_time) |

                    Q(start_time__lte=start_time,
                    end_time__gte=end_time),

                    cancelled=False,
                ).exists()

                if overlapping:
                    return Response(
                        {"detail": "This time slot is already booked"},
                        status=status.HTTP_409_CONFLICT
                    )

                # Save the appointment if no overlaps
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
