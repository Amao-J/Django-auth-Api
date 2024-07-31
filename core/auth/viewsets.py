from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from core.auth.serializers import LoginSerializer, RegisterSerializer
from core.user.serializers import DashboardSerializer, ProfileSerializer, UserSerializer
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from core.user.models import User, Dashboard
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status


class LoginViewSet(GenericViewSet, TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegistrationViewSet(GenericViewSet):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "user": serializer.data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)


class RefreshViewSet(GenericViewSet, TokenRefreshView):
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class VerifyOTPViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_otp(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        user = get_object_or_404(User, email=email)

        if user.profile.otp == otp:
            user.is_active = True
            user.profile.otp = ''
            user.save()
            user.profile.save()
            return Response({'message': 'OTP verified successfully. Account activated.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


class DashboardViewSet(ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        dashboard = get_object_or_404(Dashboard, user=request.user, pk=kwargs['pk'])
        serializer = self.get_serializer(dashboard)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        user = request.user
        profile = user.profile
        profile_serializer = ProfileSerializer(profile)
        dashboard = user.dashboard
        dashboard_serializer = DashboardSerializer(dashboard)
        return Response({
            'user': UserSerializer(user).data,
            'profile': profile_serializer.data,
            'dashboard': dashboard_serializer.data
        })

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        user = request.user
        profile_data = request.data.get('profile', {})
        user_data = request.data.get('user', {})
        dashboard_data = request.data.get('dashboard', {})

        user_serializer = UserSerializer(user, data=user_data, partial=True)
        profile_serializer = ProfileSerializer(user.profile, data=profile_data, partial=True)
        dashboard_serializer = DashboardSerializer(user.dashboard, data=dashboard_data, partial=True)

        if user_serializer.is_valid() and profile_serializer.is_valid() and dashboard_serializer.is_valid():
            user_serializer.save()
            profile_serializer.save()
            dashboard_serializer.save()
            return Response({
                'user': user_serializer.data,
                'profile': profile_serializer.data,
                'dashboard': dashboard_serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            'user_errors': user_serializer.errors,
            'profile_errors': profile_serializer.errors,
            'dashboard_errors': dashboard_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
