from django.db.models.signals import post_save, post_delete
from .models import Customer


def delete_user(sender, instance, **kwargs):
    instance.user.delete()


post_delete.connect(delete_user, sender=Customer)