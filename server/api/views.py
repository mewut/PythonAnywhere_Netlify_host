from django.shortcuts import render
from .serializers import TodoSerializer, TodoToggleCompleteSerializer
from todo.models import Todo

from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from django.db import IntegrityError
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


# class TodoList(generics.ListAPIView):
#     serializer_class = TodoSerializer
#     def get_queryset(self):
#         user = self.request.user
#         return Todo.objects.filter(user=user).order_by('-created')


class TodoListCreate(generics.ListCreateAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user).order_by('-created')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user)


class TodoToggleComplete(generics.UpdateAPIView):
    serializer_class = TodoToggleCompleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user)

    def perform_update(self, serializer):
        serializer.instance.completed = not (serializer.instance.completed)
        serializer.save()

# Поскольку POST-запрос приходит из другого домена (домена фронтенда) и не будет иметь токена, необходимого для прохождения проверки CSRF (межсайтовой обработки запросов), используем csrf_exempt для регистрации пользователя
# И JWT Токен для безопасности действий зарегистрированного

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request)
            user = User.objects.create_user(
                username=data['username'], password=data['password'])
            user.save()

            # Создание JWT токена
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=201)
        except IntegrityError:
            return JsonResponse({'error': 'username taken. choose another username'}, status=400)
    
    # Обработка GET-запроса
    return JsonResponse({'error': 'Method not allowed'}, status=405)
