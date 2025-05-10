from rest_framework.generics import CreateAPIView, UpdateAPIView
from .serializers import CustomerCreateSerializer
from .models import Customer
from .permissions import IsOwner



class CustomerCreateAPIView(CreateAPIView):
    serializer_class = CustomerCreateSerializer
    queryset = Customer.objects.all()

    

class CustomerUpdateAPIView(UpdateAPIView):
    serializer_class = CustomerCreateSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsOwner]    
    lookup_field = "pk"
    lookup_url_kwarg = "customer_pk"


