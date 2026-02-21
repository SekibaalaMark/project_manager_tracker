from django.urls import path
from .views import *

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("create-users/", CreateOrganizationUserView.as_view()),
    path("set-password/", SetNewPasswordView.as_view()),
    path("verify-email/<uidb64>/<token>/",VerifyEmailView.as_view(),name="verify-email",),
    path("resend-verification/",ResendVerificationView.as_view(),name="resend-verification",),
    path("change-password/",ChangePasswordView.as_view(),name="change-password",),

]
