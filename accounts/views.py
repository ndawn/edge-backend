from accounts.models import User
from rest_framework import viewsets
from accounts.serializers import UserSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.response import Response
from rest_framework.views import APIView


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser, )

    queryset = User.objects.all()
    serializer_class = UserSerializer


class TestView(APIView):
    def post(self, request, format=None):
        return Response(request.user.is_anonymous)


class CurrentUserView(APIView):
    def get(self, request, format=None):
        return Response(UserSerializer(request.user).data)


class RegisterView(APIView):
    def post(self, request, format=None):
        if request.user.is_anonymous:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                user = User.objects.create_user(**serializer.initial_data)
                return Response({
                    'email': user.email,
                    'last_name': user.last_name,
                    'first_name': user.first_name,
                    'patronymic': user.patronymic,
                }, status=HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Already logged in'}, status=HTTP_403_FORBIDDEN)
