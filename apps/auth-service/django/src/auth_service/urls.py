from django.contrib import admin
from django.urls import path
from auth_service.views import UserCreate, CustomTokenRefreshView, verify_email, CustomTokenObtainPairView, PasswordRequestReset,  CustomPasswordResetConfirmView, ValidateTokenView


urlpatterns = [
	path('admin/', admin.site.urls),
	path('auth/signup/', UserCreate.as_view(), name='signup'),
	path('auth/token/',CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
	path('auth/verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
	path('auth/reset_password/', PasswordRequestReset.as_view(), name='password_request_reset'),
	path('auth/password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
	path('auth/validate_token/', ValidateTokenView.as_view(), name='validate_token'),
]