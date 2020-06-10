from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('login/', views.Login.as_view(), name="login"),    
    path('login-as/<str:user_type>/<str:username>', views.login_as, name="login_as"),    
    path('logout/', views.logout_user, name="logout"),
    
    path('fetch_users/', views.fetch_users, name="fetch_users"),
]