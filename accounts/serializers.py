from django.contrib.auth.models import Group
from rest_framework import serializers
from accounts.models import User, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('country', 'region', 'locality', 'street', 'building', 'apartment', 'zipcode')


class UserSerializer(serializers.ModelSerializer):
    address_set = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'last_name', 'first_name', 'patronymic', 'address_set')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('name',)
