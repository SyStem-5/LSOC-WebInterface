# Disable annoying 'no member' error
# pylint: disable=E1101
import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth.models import User

from project01.models import LSOCProfile
from project01.forms import MQTTConfigurationForm, AccoutManagementForm
from project01.system_scripts import mqtt_connection


@login_required(redirect_field_name='', login_url='login/')
def index(request):
    template = 'index.html'

    print("BLACKBOX STATUS: ")
    print(mqtt_connection.blackbox_status)

    return render(request, template, {'title': 'LSOC - Dashboard', 'blackbox_state': mqtt_connection.blackbox_status})


@login_required(redirect_field_name='', login_url='login/')
def settings(request):
    template = 'settings.html'

    return render(request, template, {'title': 'LSOC - Settings', 'blackbox_state': mqtt_connection.blackbox_status})


@permission_required('superuser')
def account_management(request):
    # if request.method == 'GET':
    template = 'staff/account_management.html'

    return render(request, template, {
        'title': 'LSOC - Account Management',
        'users': User.objects.all(),
        'blackbox_state': mqtt_connection.blackbox_status
    })


@permission_required('superuser')
def account_designer(request):
    template = 'staff/account_designer.html'

    if request.method == 'GET':
        return render(request, template, {
            'title': 'LSOC - Account Designer',
            'form': AccoutManagementForm,
            'node_element_list': mqtt_connection.node_element_list,
            'blackbox_state': mqtt_connection.blackbox_status
        })
    elif request.method == 'POST':
        form = AccoutManagementForm(request.POST)

        if form.is_valid():
            new_user = User()
            new_user.username = form.cleaned_data['username']
            new_user.password = form.cleaned_data['password1']

            saved_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'])

            lsocprofile = LSOCProfile()
            lsocprofile.user = saved_user
            lsocprofile.lsoc_permissions = form.cleaned_data['lsoc_permissions']
            lsocprofile.description = form.cleaned_data['description']
            lsocprofile.save()

            return redirect(to='account_management')
        else:
            return render(request, template, {'form': form, 'blackbox_state': mqtt_connection.blackbox_status})


@permission_required('superuser')
def connectivity_settings(request):
    # if request.method == 'GET':
    template = 'staff/connectivity_settings.html'

    form = MQTTConfigurationForm({
        'ip': mqtt_connection.settings.ip,
        'port': mqtt_connection.settings.port,
        'username': mqtt_connection.settings.username,
        'password': mqtt_connection.settings.password
    })


    return render(request, template, {
        'title': 'LSOC - Connectivity',
        'mqtt_form': form,
        'blackbox_state': mqtt_connection.blackbox_status
    })

@permission_required('superuser')
def node_registration(request):
    if request.method == 'GET':
        template = 'staff/node_registration.html'

        return render(request, template, {
            'title': 'LSOC - Node Registration',
            'blackbox_state': mqtt_connection.blackbox_status
        })
    elif request.method == 'POST':
        data = json.dumps(request.POST)

        mqtt_connection.blackbox_node_registration(json.loads(data))

        return redirect(to='node_registration')

@permission_required('superuser')
def get_unregistered_list(request):
    print("Django: Sending Unregistered Nodes list.")
    return JsonResponse({"data": mqtt_connection.unregistered_nodes_list})
@permission_required('superuser')
def get_discovery_mode_status(request):
    print("Django: Sending Discovery Mode status.")
    return JsonResponse({"data": mqtt_connection.discovery_mode})

@permission_required('superuser')
def node_control_panel(request):
    template = 'staff/node_control_panel.html'

    if request.method == 'GET':
        return render(request, template, {
            'title': 'LSOC - NCP',
            'blackbox_state': mqtt_connection.blackbox_status
        })
    elif request.method == 'POST':
        data = json.dumps(request.POST)

        mqtt_connection.blackbox_update_node_info(json.loads(data))
        return redirect(to='node_control_panel')

@permission_required('superuser')
def get_node_element_list(request):
    print("Django: Sending Node-Element list.")
    return JsonResponse({"data": mqtt_connection.node_element_list})

# POST request handlers

@permission_required('superuser')
def mqtt_settings_update(request):
    if request.method == 'POST':
        form = MQTTConfigurationForm(request.POST)

        # If the form is valid, update mqtt configuration
        if form.is_valid():
            mqtt_connection.settings = mqtt_connection.update_mqttconfig(form)

            # We just saved the new settings, disconnected/stopped
            # connection threads so we should try to reconnect now
            mqtt_connection.connect_mqtt()

        return redirect(to='connectivity_settings')


@permission_required('superuser')
def set_blackbox_discovery(request):
    if request.method == 'POST':
        data = request.POST["data"]
        if data == "enable":
            return mqtt_connection.blackbox_discovery_enable()
        elif data == "disable":
            return mqtt_connection.blackbox_discovery_disable()
        else:
            print("Unknown POST request made to 'set_blackbox_discovery': ", data)
            return JsonResponse({"data":"unknown_cmd"})


@permission_required('superuser')
def send_node_command(request):
    if request.method == 'POST':
        return mqtt_connection.blackbox_send_node_command(request.POST)
