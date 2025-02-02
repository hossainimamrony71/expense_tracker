from django.urls import path
from . import views
urlpatterns = [
    path("token/", view= views.CustomAuthToken.as_view(), name="create_token"),
    path("create_user/", view= views.creat_user, name="create_user"),
    path("user/<int:pk>/change_pass/", view= views.change_pass, name="change_pass"),
]
