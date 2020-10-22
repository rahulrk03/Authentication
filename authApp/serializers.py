from rest_framework import serializers


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    userName = serializers.CharField(required=True)
    # password = serializers.CharField(required=False)


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class ResetPasswordSerilaizer(serializers.Serializer):
    # email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


class EditProfileSerilaizer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    userName = serializers.CharField(required=False)
    phoneNumber = serializers.CharField(required=False)
    language = serializers.CharField(required=False)
    profilePicture = serializers.ImageField(required=False)
    # location = serializers.CharField(required=False)


class GenrateTokenSerilaizer(serializers.Serializer):
    email = serializers.EmailField(required=False)


class TokenSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


# class ForgotPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField(required=True)
#     userName = serializers.CharField(required=True)
