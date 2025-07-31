from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView, TokenVerifyView
)

from .views import FollowViewSet, PostViewSet, CommentViewSet, GroupViewSet

router = DefaultRouter()
router.register('follow', FollowViewSet, basename='follow')
router.register(r'posts', PostViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path('v1/jwt/create/', TokenObtainPairView.as_view(), name='jwt-create'),
    path('v1/jwt/refresh/', TokenRefreshView.as_view(), name='jwt-refresh'),
    path('v1/jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
    path('v1/', include(router.urls)),
    path(
        'v1/posts/<int:post_id>/comments/',
        CommentViewSet.as_view({'get': 'list', 'post': 'create'})
    ),
    path(
        'v1/posts/<int:post_id>/comments/<int:pk>/',
        CommentViewSet.as_view({
            'get': 'retrieve',
            'put': 'update',
            'patch': 'partial_update',
            'delete': 'destroy'
        })
    )
]
