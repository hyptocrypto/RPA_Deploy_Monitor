from django.urls import path
from . import views
from .views import HomeView, MonitorView
from django.contrib.auth.decorators import login_required

# All valid urls for site/application
urlpatterns = [
    path('', login_required(HomeView.as_view()), name = 'home'),
    path('deploy/', views.deploy_form, name ='deploy'),
    path('success/', views.success, name = 'success'),
    path('monitor/device/<slug:slug>/', login_required(MonitorView.as_view()), name = 'monitor'),
    path('accounts/login/', views.login_page, name = 'login'),
    path('accounts/logout/', views.logout_user, name = 'logout'),
    
]