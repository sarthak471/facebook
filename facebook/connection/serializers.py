from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('id','username', 'password', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'email': {
                'validators': [UniqueValidator(queryset=User.objects.all(), lookup='iexact')]
            }
        }

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'], 
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
from django.contrib.auth import authenticate
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
    
from rest_framework import serializers
from .models import Friendship

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'friend_status', 'request_status', 'reject_status']
        read_only_fields = ['from_user']  
    def create(self, validated_data):
        validated_data['from_user'] = self.context['request'].user
        return super(FriendshipSerializer, self).create(validated_data)

class ViewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
class FriendShipListResponseSerializer(serializers.ModelSerializer):
    to_user = ViewUserSerializer(read_only=True)

    class Meta:
        model = Friendship

        fields = ['id', 'to_user']

class PendingListResponseSerializer(serializers.ModelSerializer):
    from_user = ViewUserSerializer(read_only=True)

    class Meta:
        model = Friendship

        fields = ['id', 'from_user']