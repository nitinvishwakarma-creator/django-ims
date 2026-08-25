from django.urls import path

from apps.accounts.api.v1 import views


app_name = "accounts_api_v1"


urlpatterns = [
    path(
        "",
        views.auth_root,
        name="root",
    ),

    path(
        "login/",
        views.login_api,
        name="login",
    ),

    path(
        "logout/",
        views.logout_api,
        name="logout",
    ),

    path(
        "me/",
        views.me_api,
        name="me",
    ),

    path(
        "csrf/",
        views.csrf_api,
        name="csrf",
    ),
    path(
        "logout-all/",
        views.logout_all_api,
        name="logout_all",
    ),
]