# Disable annoying 'no member' error
# pylint: disable=E1101
import json
import hashlib

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render

from project01.models import MQTTConfig
from project01.forms import AccoutManagementForm, MQTTConfigurationForm
from project01.system_scripts.mqtt_connection import (update_mqttconfig,
                                                      init_mqtt)


@login_required(redirect_field_name='', login_url='login/')
def dashboard(request):
    template = 'dashboard.html'
    return render(request, template, {'title': 'Dashboard'})


# @login_required(redirect_field_name='', login_url='login/')
@permission_required('superuser')
def settings(request):
    template = 'settings.html'
    return render(request, template, {'title': 'Settings'})


@permission_required('superuser')
def system_configuration(request):
    template = 'staff/system_configuration.html'

    conf = MQTTConfig.objects.all()

    if len(conf) > 0:
        form = MQTTConfigurationForm({
            'ip': conf[0].ip,
            'port': conf[0].port,
            'username': conf[0].username,
            'password': conf[0].password
        })

    return render(request, template, {
        'title': 'System Configuration',
        'mqtt_form': form
    })


@permission_required('superuser')
def account_management(request):
    template = 'staff/account_management.html'

    return render(request, template, {
        'title': 'Account Management',
        'users': User.objects.all(),
        'form': AccoutManagementForm
    })


@permission_required('superuser')
def node_registration(request):
    template = 'staff/node_registration.html'

    return render(request, template, {
        'title': 'Node Registration'
    })


@permission_required('superuser')
def node_control_panel(request):
    template = 'staff/node_control_panel.html'

    return render(request, template, {
        'title': 'NCP'
    })


@permission_required('superuser')
def zones(request):
    template = 'staff/zones.html'

    return render(request, template, {
        'title': 'Zones'
    })


@permission_required('superuser')
def mqtt_cert(request):
    from django.http import HttpResponse
    from django.utils.encoding import smart_str
    from wsgiref.util import FileWrapper
    from project01.settings import DEBUG

    if DEBUG:
        file_name = "/etc/mosquitto/ca.crt"
    else:
        file_name = "/run/secrets/mqtt_ca.crt"

    wrapper = FileWrapper(open(file_name, 'rb'))

    response = HttpResponse(wrapper, content_type='application/x-x509-ca-cert')
    response['Content-Disposition'] = 'attachment; filename=node.crt'

    return response


# POST request handlers

@permission_required('superuser')
def mqtt_configuration(request):
    if request.method == 'POST':
        form = MQTTConfigurationForm(request.POST)

        # If the form is valid, update mqtt configuration
        if form.is_valid():
            update_mqttconfig(form)

            # Try to reconnect now
            init_mqtt()

        return redirect(to='system_configuration')
