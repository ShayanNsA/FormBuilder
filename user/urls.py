from django.urls import path

from . import views


app_name = "user"


urlpatterns = [
    # Authentication
    path("send-otp/",views.send_otp,name="send-otp"),

    path("verify-otp/",views.verify_otp_view,name="verify-otp"),

    path("register/",views.register,name="register"),

    path("login/",views.login_user,name="login"),

    path("logout/",views.logout_user,name="logout"),

    # Profile
    path("profile/",views.profile,name="profile"),

    path("profile/update/",views.update_profile,name="update-profile"),
]