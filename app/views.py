from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Task
from .serializers import UserSerializer, TaskSerializer

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.none()


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Task.objects.all()
        elif user.type == User.TYPE_EMPLOYEE:
            return Task.objects.filter(employee=user) | Task.objects.filter(client=user)
        return Task.objects.filter(client=user)

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[IsAuthenticated])
    def assign(self, request):
        task = self.get_object()
        if request.user.type == User.TYPE_EMPLOYEE:
            task.employee = request.user
            task.status = "in_progress"
            task.save()
            return Response({"status": "task assigned"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Only employees can assign tasks"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status == "done":
            return Response(
                {"error": "Completed task cannot be edited"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status == "done":
            return Response(
                {"error": "Completed task cannot be edited"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().partial_update(request, *args, **kwargs)
