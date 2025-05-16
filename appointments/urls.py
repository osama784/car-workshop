from django.urls import path
from . import views


urlpatterns = [
    path("get-appointments", views.get_appointments),
    path("cancel-appointment/<int:pk>", views.cancel_appointment),
    path("get-available-times", views.get_available_times),
    path("book-appointment", views.AppointmentCreateAPIView.as_view())
    
]