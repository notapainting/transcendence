from django.urls import path
from accounts.views import UserCreate, CustomTokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('api/signup/', UserCreate.as_view(), name='signup'),
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]