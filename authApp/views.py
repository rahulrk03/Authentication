from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from datetime import datetime
from django.conf import settings
from rest_framework.decorators import permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from refresh_token.models import RefreshToken
import jwt
from .serializers import (UserCreateSerializer,
                          UserLoginSerializer,
                          ResetPasswordSerilaizer,
                          EditProfileSerilaizer,
                          GenrateTokenSerilaizer,
                          TokenSerializer)
from .models import User
from django.contrib.auth import authenticate, login
import random
import string

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
null = None


class UserRegistrationAPI(APIView):
    def post(self, request, format=None):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            userName = request.data["userName"]
            password = request.data.get("password")
            try:
                user = User.objects.get(email__exact=email)
                if user:
                    if user.is_active is False:
                        user.delete()
                    else:
                        return Response({"data": null,
                                         "message": "User exists",
                                         "requestStatus": 0},
                                        status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                profile = User.objects.create(email=email,
                                              userName=userName,
                                              is_active=True,
                                              createdTime=datetime.now())
                profile.set_password(password)
                profile.save()
                return Response({"data": null,
                                 "message": "Success",
                                 "requestStatus": 1},
                                status=status.HTTP_200_OK)
        return Response({"data": serializer.errors,
                         "message": "Input error",
                         "requestStatus": 0},
                        status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPI(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = request.data["email"]
            password = request.data["password"]
            try:
                user = User.objects.get(email__exact=email)
                if user.is_active is False:
                    return Response({"message": "User Inactive",
                                     "requestStatus": 0},
                                    status=status.HTTP_400_BAD_REQUEST)
                user = authenticate(email=email, password=password)
                if user is not None:
                    login(request, user)
                    try:
                        x = RefreshToken.objects.get(user=user)
                        RefreshToken.revoke(x)
                    except RefreshToken.DoesNotExist:
                        RefreshToken.objects.create(user=user).save()
                    jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
                    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                    payload = jwt_payload_handler(user)
                    token = jwt.encode(payload, settings.SECRET_KEY)
                    tk = token.decode('unicode_escape')
                    tk = jwt_response_payload_handler(tk, user)
                    if user.profilePicture == '':
                        profilePicture = None
                    else:
                        profilePicture = str(user.profilePicture)
                    token = {
                            "token": tk,
                            "userId": user.id,
                            "userName": user.userName,
                            "email": user.email,
                            "phoneNumber": user.phoneNumber,
                            "profilePicture": profilePicture,
                            }
                    return Response({"data": token,
                                     "message": "SUCC_AUTH",
                                     "requestStatus": 1},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({"data": None,
                                     "message": "Invalid credentials",
                                     "requestStatus": 0},
                                    status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"data": None,
                                 "message": "User does not exist",
                                 "requestStatus": 0},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": serializer.errors,
                         "message": "Input error",
                         "requestStatus": 0},
                        status=status.HTTP_400_BAD_REQUEST)


@permission_classes((IsAuthenticated,))
@authentication_classes([JSONWebTokenAuthentication])
class ResetPasswordAPI(APIView):
    def post(self, request, format=None):
        serializer = ResetPasswordSerilaizer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(id=request.user.id)
                user.set_password(request.data["password"])
                user.save()
                x = RefreshToken.objects.get(user=user)
                x.delete()
                return Response({"data": null,
                                 "message": "Password Changed",
                                 "requestStatus": 1},
                                status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"data": null,
                                 "message": "User does not exist",
                                 "requestStatus": 0},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": serializer.errors,
                         "message": "Input error",
                         "requestStatus": 0},
                        status=status.HTTP_400_BAD_REQUEST)


@permission_classes((IsAuthenticated,))
@authentication_classes([JSONWebTokenAuthentication])
class UpdateProfileAPI(APIView):
    def put(self, request, format=None):
        serializer = EditProfileSerilaizer(data=request.data)
        if serializer.is_valid():
            email = request.data.get("email")
            userName = request.data.get('userName')
            phoneNumber = request.data.get('phoneNumber')
            profilePicture = request.data.get('profilePicture')
            try:
                if email:
                    request.user.email = email
                    sendData = {
                                "email": email
                    }
                if userName:
                    request.user.userName = userName
                if phoneNumber:
                    request.user.phoneNumber = phoneNumber
                request.user.profilePicture = profilePicture
                request.user.save()
                return Response({"data": sendData,
                                 "message": "Profile Updated",
                                 "requestStatus": 1},
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response({"data": str(e),
                                 "message": "Something Went wrong",
                                 "requestStatus": 0},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"data": serializer.errors,
                         "message": "Input error",
                         "requestStatus": 0},
                        status=status.HTTP_400_BAD_REQUEST)


@permission_classes((IsAuthenticated,))
@authentication_classes([JSONWebTokenAuthentication])
class UserDataAPI(APIView):
    def get(self, request):
        if request.user.profilePicture == '':
            profilePicture = None
        else:
            profilePicture = str(request.user.profilePicture)
        data = {
                 "userName": request.user.userName,
                 "email": request.user.email,
                 "phoneNumber": request.user.phoneNumber,
                 "profilePicture": profilePicture,
                }
        return Response({"data": data,
                         "message": "Success",
                         "requestStatus": 1},
                        status=status.HTTP_200_OK)


class GenerateTokenAPI(APIView):
    def post(self, request, format=None):
        serializer = GenrateTokenSerilaizer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email__exact=request.data["email"])
            try:
                x = RefreshToken.objects.get(user=user)
                RefreshToken.revoke(x)
            except RefreshToken.DoesNotExist:
                RefreshToken.objects.create(user=user).save()
            jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt.encode(payload, settings.SECRET_KEY)
            tk = token.decode('unicode_escape')
            tk = jwt_response_payload_handler(tk, user)
            if user.profilePicture == '':
                profilePicture = None
            else:
                profilePicture = str(user.profilePicture)
            user.last_login = datetime.now()
            user.save()
            token = {
                    "token": tk,
                    "userName": user.userName,
                    "email": user.email,
                    "phoneNumber": user.phoneNumber,
                    "profilePicture": profilePicture,
                    }
            return Response({"data": token,
                             "message": "SUCC_AUTH",
                             "requestStatus": 1},
                            status=status.HTTP_200_OK)
        return Response({"data": serializer.errors,
                         "message": "Input error",
                         "requestStatus": 0},
                        status=status.HTTP_400_BAD_REQUEST)


class ValidateToken(APIView):
    def post(self, request, format=None):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
            # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER
            try:
                payload = jwt_decode_handler(request.data["token"])
                username = jwt_get_username_from_payload(payload)
                if not username:
                    return Response({"data": null,
                                     "message": "Session expired",
                                     "requestStatus": 1},
                                    status=status.HTTP_400_BAD_REQUEST)
                try:
                    user = User.objects.get(email=username)
                    if user.is_active:
                        return Response({"data": null,
                                         "message": "Token Active",
                                         "requestStatus": 1},
                                        status=status.HTTP_200_OK)
                    else:
                        return Response({"data": null,
                                         "message": "Inactive User",
                                         "requestStatus": 0},
                                        status=status.HTTP_400_BAD_REQUEST)
                except User.DoesNotExist:
                    return Response({"data": null,
                                     "message": "User unavailable",
                                     "requestStatus": 0},
                                    status=status.HTTP_400_BAD_REQUEST)
            except jwt.DecodeError:
                return Response({"data": null,
                                 "message": "verification failed",
                                 "requestStatus": 0},
                                status=status.HTTP_400_BAD_REQUEST)

# class ForgotPasswordAPI(APIView):
#     def post(self, request,format=None):
#         serializer=ForgotPasswordSerializer(data=request.data)
#       if serializer.is_valid():
#           email=request.data["email"]
#           try:
#               user=User.objects.get(email=email)
#               if user.is_active:
#                   user.otp = str(User.generate_otp())
#                   user.otp_validation =datetime.utcnow()+ timedelta(minutes = 15) 
#                   user.save()
#                   subject = 'Study App Account'
#                   message = 'Your otp is ' + user.otp
#                   to=[user.email]
#                   msg = EmailMessage(subject, message, to=to, from_email=settings.EMAIL_HOST_USER)
#                   msg.send()
#                   return Response({"data":null,"message":"Otp sent on email","requestStatus":1},status=status.HTTP_200_OK)
#               else:
#                   return Response({"data":null,"message":"Inactive user","requestStatus":0},status=status.HTTP_400_BAD_REQUEST)
#           except User.DoesNotExist:
#               return Response({"message":"User does not exist","requestStatus":0},status=status.HTTP_400_BAD_REQUEST)
#       return Response({"data": serializer.errors,"message":"Input error","requestStatus":0},status=status.HTTP_400_BAD_REQUEST)