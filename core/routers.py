from rest_framework.routers import SimpleRouter
from core.user.viewsets import UserViewSet, ProfileViewSet, DashboardViewSet
from core.auth.viewsets import LoginViewSet, RegistrationViewSet, RefreshViewSet

routes = SimpleRouter()

# AUTHENTICATION
routes.register(r'auth/login', LoginViewSet, basename='auth-login')
routes.register(r'auth/register', RegistrationViewSet, basename='auth-register')
routes.register(r'auth/refresh', RefreshViewSet, basename='auth-refresh')


routes.register(r'user', UserViewSet, basename='user')
routes.register(r'profile', ProfileViewSet, basename='profile')


routes.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    *routes.urls
]
