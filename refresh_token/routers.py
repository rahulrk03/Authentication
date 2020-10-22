from rest_framework import routers

from .views import RefreshTokenViewSet

router = routers.SimpleRouter()
router.register(r'refresh-token', RefreshTokenViewSet)