from django.contrib import admin
from django.urls import path
from auth_service.views import UserCreate, CustomTokenRefreshView, verify_email, CustomTokenObtainPairView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/signup/', UserCreate.as_view(), name='signup'),
	path('api/token/',CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('api/verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
]