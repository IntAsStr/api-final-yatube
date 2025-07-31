from rest_framework import viewsets, filters, permissions, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Post, Follow, Comment, Group
from .serializers import (
    FollowSerializer, PostSerializer, CommentSerializer, GroupSerializer
)
from .permissions import IsOwnerOrReadOnly


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated,]
    filter_backends = [filters.SearchFilter]
    search_fields = ['following__username']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        following_user = serializer.validated_data.get('following')
        if self.request.user == following_user:
            raise serializers.ValidationError('Нельзя подписаться на себя')

        if Follow.objects.filter(
                user=self.request.user,
                following=following_user
            ).exists():
            raise serializers.ValidationError(
                {'following': 'Вы уже подписаны на этого пользователя'},
            )
        serializer.save(user=self.request.user)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related('author').all()
    serializer_class = PostSerializer
    permission_classes = [
        IsOwnerOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly,
    ]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого контента запрещено!')
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого комментария запрещено!')
        return super().perform_destroy(instance)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes =[permissions.IsAuthenticatedOrReadOnly,]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return (
            Comment.objects
            .select_related('author', 'post')
            .filter(post_id=post_id)
        )

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        serializer.save(author=self.request.user, post_id=post_id)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise PermissionDenied('Изменение чужого комментария запрещено!')
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise PermissionDenied('Удаление чужого комментария запрещено!')
        return super().perform_destroy(instance)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
