from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

import re
from datetime import datetime


from .serializers import CustomerCreateSerializer, ResetPasswordSerializer, CustomTokenObtainPairSerializer
from .models import Customer
from users.models import User


class CustomerCreateAPIView(CreateAPIView):
    serializer_class = CustomerCreateSerializer
    queryset = Customer.objects.all()

    

class CustomerUpdateAPIView(UpdateAPIView):
    serializer_class = CustomerCreateSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = request.user.customer
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)    
    

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer    

@api_view(['POST'])
def get_verification_code(request):
    email = request.data.get("email")
    valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

    if not valid:
        return Response(data={"detail": "invalid email"}, status=status.HTTP_400_BAD_REQUEST)
    
    user = get_object_or_404(User, email=email)
    reset_code = user.generate_reset_code()

    # rendering reset password template
    html_message = render_to_string('email/password_reset.html', {
        'username': user.username,
        'reset_code': reset_code,
        'current_year': datetime.now().year,
    })
    email = EmailMessage(
        subject='Password Reset Request',
        body=html_message,
        from_email='osamadoage0@gmail.com',
        to=[email]
    )
    email.content_subtype = 'html'
    try:
        email.send()
    except OSError:
        return Response(data={"detail": "Please resend your email, something goes wrong with the connection"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)    
    
    return Response(data={"detail": "Email sent successfully"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    reset_code = serializer.validated_data.get("reset_code")
    email = serializer.validated_data.get("email")
   
    user = get_object_or_404(User, reset_code=reset_code, email=email)
    user.set_password(serializer.validated_data.get("password"))
    user.save()

    return Response(data={"success": True}, status=status.HTTP_200_OK)


