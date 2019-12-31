"""project01 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django.contrib.auth.views
from django.contrib import admin
from django.urls import path

from project01 import views
from project01 import forms


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('settings/', views.settings, name='settings'),

    path('staff/system_configuration', views.system_configuration, name='system_configuration'),

    path('staff/system_configuration/accounts', views.account_management, name='account_management'),

    path('staff/system_configuration/nodes/registration', views.node_registration, name='node_registration'),

    path('staff/system_configuration/nodes/CP', views.node_control_panel, name='node_control_panel'),

    path('staff/system_configuration/zones', views.zones, name='zones'),

    path('staff/system_configuration/nodes/registration/mqtt-cert', views.mqtt_cert, name='node_registration_mqtt_cert'),

    #POST Request views
    path('staff/system_configuration/mqtt_configuration', views.mqtt_configuration),

    path('login/',
         django.contrib.auth.views.LoginView.as_view(template_name = 'auth/login.html',
                                                     authentication_form = forms.BootstrapAuthenticationForm,
                                                     extra_context =
                                                     {
                                                         'title': 'Log in',
                                                     }),
         name='login'),
    path('logout/', django.contrib.auth.views.LogoutView.as_view(next_page = 'login/'), name='logout'),

    path('admin/', admin.site.urls),
]
