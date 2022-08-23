from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from foodgram.models import Subscription

from .models import User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        if self.context.get("request"):
            user = self.context.get("request").user
        else:
            user = obj
        if not user.is_authenticated:
            return False
        return Subscription.objects.filter(user=user, author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    password = serializers.CharField(
        style={"input_type": "password"},
        write_only=True
    )
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )
