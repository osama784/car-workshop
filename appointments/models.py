from django.db import models

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

    
   


