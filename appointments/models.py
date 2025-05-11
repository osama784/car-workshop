from django.db import models
from django.core import exceptions

from users.models import Customer


class Appointment(models.Model):
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)
    car_brand = models.CharField(max_length=50)
    car_model = models.CharField(max_length=50)
    car_year = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problem_type = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    cost = models.PositiveIntegerField()
    canceled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username}: {self.car_brand} {self.car_model} {self.car_year} from {self.start_time} to {self.end_time}"
    
    class Meta:
        ordering = ['end_time']
        indexes = [
            models.Index(fields=['start_time','end_time']),  # Speeds up ordering
        ]

        constraints = [
            # Prevent overlapping appointments
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_after_start'
            ),
            # Ensure no overlapping time slots
            models.UniqueConstraint(
                fields=['start_time', 'end_time'],
                name='unique_appointment_slot'
            )
        ]
    
    def clean(self):
        # Validate no overlapping appointments
        overlapping = Appointment.objects.filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exists()
        
        if overlapping:
            raise exceptions.ValidationError("This time slot is already booked")
    
    def save(self, *args, **kwargs):
        self.full_clean()  # Enforce model validation
        super().save(*args, **kwargs)    


