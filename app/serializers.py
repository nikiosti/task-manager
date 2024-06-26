from rest_framework import serializers
from .models import Task, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'email', 'phone', 'type', 'photo']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['type'] == User.TYPE_CUSTOMER and attrs.get('is_staff'):
            raise serializers.ValidationError("Заказчик не может иметь права сотрудника")
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class TaskSerializer(serializers.ModelSerializer):
    
    client = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'client', 'employee', 'created_at', 'updated_at', 'closed_at', 'report']
        read_only_fields = ['client', 'created_at', 'updated_at', 'closed_at']

    def validate_status(self, value):
        if self.instance and self.instance.status == 'done':
            raise serializers.ValidationError("Выполненную задачу редактировать нельзя")
        return value

    def validate(self, attrs):
        if attrs.get('status') == 'done' and not attrs.get('report'):
            raise serializers.ValidationError("Отчет не может быть пустым при закрытии задачи")
        return attrs
