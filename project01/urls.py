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
    path('', views.index, name='index'),
    path('settings/', views.settings, name='settings'),

    path('staff/accounts', views.account_management, name='account_management'),
    path('staff/accounts/designer', views.account_designer, name='account_management_designer'),
    path('staff/sysconfig', views.system_configuration, name='system_configuration'),

    path('staff/sysconfig/nodes/registration', views.node_registration, name='node_registration'),
    path('staff/sysconfig/nodes/registration/get/discovery_status', views.get_discovery_mode_status, name='get_discovery_mode_status'),
    path('staff/sysconfig/nodes/registration/get/unregistered_list', views.get_unregistered_list, name='get_unregistered_list'),

    path('staff/sysconfig/nodes/CP', views.node_control_panel, name='node_control_panel'),
    path('staff/sysconfig/nodes/CP/get/node_element_list', views.get_node_element_list, name='get_node_element_list'),

    #POST Request views
    path('staff/sysconfig/mqtt_settings_update', views.mqtt_settings_update, name='mqtt_settings_update'),
    path('staff/sysconfig/node/registration/discovery', views.set_blackbox_discovery, name='set_blackbox_discovery'),
    path('staff/sysconfig/nodes/CP/post/send_node_command', views.send_node_command, name='send_node_command'),

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
