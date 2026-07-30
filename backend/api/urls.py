from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views_auth


router = DefaultRouter()
router.register(r'machines', views.MachineTypeViewSet)
router.register(r'faults', views.FaultViewSet)
router.register(r'solutions', views.SolutionViewSet)
router.register(r'diagnose', views.DiagnosisViewSet, basename='diagnose')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views_auth.register, name='register'),
    path('auth/login/', views_auth.login, name='login'),
    path('auth/logout/', views_auth.logout, name='logout'),
    path('auth/me/', views_auth.me, name='me'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]