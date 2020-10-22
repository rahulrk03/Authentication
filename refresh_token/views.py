from calendar import timegm
from datetime import datetime

from django.utils.translation import ugettext as _
from rest_framework import exceptions, generics, status, viewsets
#from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework.decorators import action

from .models import RefreshToken
from .serializers import DelegateJSONWebTokenSerializer, RefreshTokenSerializer

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class DelegateJSONWebToken(generics.CreateAPIView):
    """
    API View that checks the veracity of a refresh token, returning a JWT if it
    is valid.
    """
    permission_classes = [AllowAny]
    serializer_class = DelegateJSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                _('User inactive or deleted.'))

        payload = jwt_payload_handler(user)
        if api_settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(datetime.utcnow().utctimetuple())
        token = jwt_encode_handler(payload)
        response_data = jwt_response_payload_handler(token, user, request)
        return Response(response_data,
                        status=status.HTTP_200_OK)


class RefreshTokenViewSet(viewsets.ModelViewSet):
    """
    API View that will Create/Delete/List `RefreshToken`.

    https://auth0.com/docs/refresh-token
    """
    serializer_class = RefreshTokenSerializer
    queryset = RefreshToken.objects.all()
    lookup_field = 'key'

    def get_queryset(self):
        queryset = super(RefreshTokenViewSet, self).get_queryset()
        if self.request.user.is_superuser or self.request.user.is_staff:
            return queryset
        else:
            return queryset.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def revoke(self, request, key=None):
        obj = self.get_object()
        new_rt = obj.revoke()
        serializer = self.get_serializer(new_rt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


delegate_jwt_token = DelegateJSONWebToken.as_view()