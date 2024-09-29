from django.urls import path
from .views import delete_account, homepage
from LoginApp import views

urlpatterns = [
    path('home/',homepage,name="home"),
    path('',views.SignupPage,name="Signup"),
    path('login/',views.LoginPage,name="login"),
    path('home/',views.homepage,name="home"),
    path('logout/',views.Logout,name="logout"),
    path('forgotpassword/',views.ForgetPassword,name='forgotpassword'),
    path('changepassword/<str:token>/', views.change_password, name='changepassword'),
    path('delete_account/', delete_account, name='delete_account'),
]
 