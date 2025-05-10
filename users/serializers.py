from rest_framework import serializers, validators
from rest_framework_simplejwt.tokens import AccessToken
from django.core.validators import MinLengthValidator

from .models import Customer

from django.contrib.auth import get_user_model


User = get_user_model()


# class UserCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ["username", "email", "password"]

class CustomerCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=200, validators=[MinLengthValidator(limit_value=4)])
    email = serializers.EmailField()
    password = serializers.CharField(max_length=50, validators=[MinLengthValidator(limit_value=4)])

    class Meta:
        model = Customer
        fields = ["username", "email", "password", "phone_number"]
    

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data.get("username"),
            password=validated_data.get("password"), 
            email=validated_data.get("email")
        )

        customer = Customer.objects.create(
            user = user,
            phone_number=validated_data.get("phone_number")
        )

        return customer
    
    def update(self, instance, validated_data):
        if 'email' in validated_data and instance.user.email != validated_data.get('email'):
            if User.objects.filter(email=validated_data.get("email")).exclude(pk=instance.pk).exists():
                raise serializers.ValidationError("unvalid email")
            else:
                setattr(instance.user, 'email', validated_data.get("email"))
        
        if 'username' in validated_data:
            setattr(instance.user, 'username', validated_data.get("username"))
        
        if 'password' in validated_data:
            instance.user.set_password(validated_data['password'])        


        instance.phone_number = validated_data.get("phone_number", instance.phone_number) 

        instance.user.save()
        instance.save()

        return instance    
    
    def to_representation(self, instance):
        user_token = AccessToken.for_user(instance.user)
        return {
            "id": instance.id,
            'phone_number': instance.phone_number,
            'username': instance.user.username,
            'email': instance.user.email,
            "token": str(user_token)
        }
    
    
    
    
    