from django.contrib import admin
from django.urls import path
from auth_service.register import UserCreate
from auth_service.login import CustomTokenObtainPairView, CustomTokenRefreshView, ValidateTokenView
from auth_service.mailing import verify_email
from auth_service.oauth import authenticate_with_42, oauth_callback
from auth_service.twoFactor import Activate2FAView, Confirm2FAView
from auth_service.userRequests import UpdateClientInfo, UpdateProfilePicture, GetUserPersonnalInfos
from auth_service.views import LogoutRequest

urlpatterns = [
	# path('auth/reset_password/', PasswordRequestReset.as_view(), name='password_request_reset'),
	# path('auth/password_reset_confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
	path('admin/', admin.site.urls),
	path('auth/signup/', UserCreate.as_view(), name='signup'),
	path('auth/token/',CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
	path('auth/verify-email/<uidb64>/<token>/', verify_email, name='verify_email'),
	path('auth/authenticate_with_42/', authenticate_with_42, name='authenticate_with_42'),
	path('auth/Oauth/', oauth_callback, name='oauth_callback'),
    path('auth/activate2FA/', Activate2FAView.as_view(), name='activate_2FA'),
    path('auth/confirm2FA/', Confirm2FAView.as_view(), name='confirm_2FA'),
	path('auth/validate_token/', ValidateTokenView.as_view(), name='validate_token'),
	path('auth/update_client/', UpdateClientInfo.as_view(), name='update_client'),
	path('auth/update_picture/', UpdateProfilePicture.as_view(), name='update_picture'),
	path('auth/get_pers_infos/', GetUserPersonnalInfos.as_view(), name='get_user_personnal_infos'),
	path('auth/logout/', LogoutRequest.as_view(), name='logout_request'),
]