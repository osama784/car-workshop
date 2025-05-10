from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework import status, exceptions

from django.utils import timezone

from .models import Appointment
from .serializers import AppointmentSerializer
from .utils import fetch_prompt_info
from .ai import send_prompt

# from ..ai import send_prompt

# Create your views here.


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_appointments(request):
    appointment_status = request.GET.get("status")
    appointments = Appointment.objects.filter(customer=request.user.customer)

    if appointment_status == "pending":
        appointments = appointments.filter(end_time__lt=timezone.now())
    if appointment_status == "completed":
        appointments= appointments.filter(end_time__gte=timezone.now())
    if appointment_status == "canceled":
        appointments = appointments.filter(canceled=True)   
    

    return Response(data={"appointments": appointments, "success": True}, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, pk):
    try:
        appointment = Appointment.objects.get(customer=request.user.customer, pk=pk)
        appointment.canceled = True
        appointment.save()
    except:
        return Response(data={"success": False, "message": "not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response(data={"success": True}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_available_times(request):
    appointments = Appointment.objects.all()
    fetched_resposne = fetch_prompt_info(send_prompt(request.data.get("user_message")))

    # get every day and see available appointments in it, and if there is, any increase the counter
    num_of_appointments = 0
    today = timezone.now()
    
    appointment_duration = int(fetched_resposne.get("time to fix"))
    available_dates = {}
    
    current_timezone = timezone.get_current_timezone()
    appointment_start_time = timezone.datetime(today.year, today.month, today.day, 8, 0, tzinfo=current_timezone)
    appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)
    
    while (appointment_start_time - today).days != 11 or num_of_appointments != 10:
        appointments_for_day = appointments.filter(start_time__day=appointment_start_time.day)
        current_day_hours = []
        while appointment_end_time.hour <= 18:
            if appointments_for_day.filter(start_time__lt=appointment_end_time).exists():
                appointment_start_time = appointments_for_day.last().end_time # note: appointments sorted by end_time
                appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)
            else:
                appointment_start_time = appointment_end_time
                appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)

                current_day_hours.append(f'{appointment_start_time.hour}:{appointment_start_time.minute}:00 to {appointment_end_time.hour}:{appointment_end_time.minute}:00')

                num_of_appointments += 1

        # prevent any empty keys
        if current_day_hours:
            available_dates[f"{appointment_start_time.year}-{appointment_start_time.month}-{appointment_start_time.day}"] = current_day_hours

        # change the appointment_start_time to the start of the next day (8:00 am)
        appointment_start_time = timezone.datetime(appointment_start_time.year, appointment_start_time.month, appointment_start_time.day, 8, 0, tzinfo=current_timezone) + timezone.timedelta(days=1)
        appointment_end_time = appointment_start_time + timezone.timedelta(minutes=appointment_duration)

    return Response(data= {
        'appointments': available_dates,
        'AI_response': fetched_resposne.get("possibilities"),
        "cost": int(fetched_resposne.get("cost")),
        "duration": appointment_duration
    }, status=status.HTTP_200_OK)    


class AppointmentCreateAPIView(CreateAPIView):
    serializer_class = AppointmentSerializer
    queryset = Appointment.objects.all()

    def check_permissions(self, request):
        if request.data.get("customer") != request.user.customer.id:
            raise exceptions.PermissionDenied("you don't have the permission to perform this action")
        return super().check_permissions(request)