# Disable annoying 'no member' error
# pylint: disable=E1101

import json

from django.contrib.auth.models import User

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.core.exceptions import ObjectDoesNotExist

from project01.forms import (AccoutManagementForm,
                             AccountEditForm,
                             ProfileEditForm)
from project01.models import LSOCProfile
from project01.websockets.commands import AccountManagement


def return_message(cmd, status=True, data=''):
    return {'command': cmd.name, 'status': status, 'data': data}

def parse_form(form, command):
    data = {}

    try:
        for key in form:
            data[key['name']] = key['value']
    except (KeyError, TypeError) as e:
        print("ERROR: account_management.py -> Could not parse the submitted form.")
        print(str(e))

        return (False, return_message(command, False, 'Could not parse the submitted form.'))

    return (True, data)

def register_account(data):

    data_parsed = parse_form(data, AccountManagement.AccountRegister)

    if data_parsed[0] == False:
        return data_parsed[1]
    else:
        data_parsed = data_parsed[1]

    form = AccoutManagementForm(data_parsed)

    if form.is_valid():

        try:
            lsoc_perms = json.loads(form.cleaned_data['lsoc_permissions'])
        except json.JSONDecodeError:
            return return_message(AccountManagement.AccountRegister, False, "Permission data is not valid JSON.")

        saved_user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password1'])

        lsocprofile = LSOCProfile()
        lsocprofile.user = saved_user
        lsocprofile.lsoc_permissions = lsoc_perms
        lsocprofile.description = form.cleaned_data['description']
        lsocprofile.save()

        return return_message(AccountManagement.AccountRegister)
    else:
        # Still not sure if this would ever need to be shown to the user...
        # So we just print it to the console
        if form.non_field_errors():
            print(form.non_field_errors())

        return return_message(AccountManagement.AccountRegister, False, str(form.errors))

def staff_edit_account(data):
    data_parsed = parse_form(data, AccountManagement.AccountEdit)

    if data_parsed[0] == False:
        return data_parsed[1]
    else:
        data_parsed = data_parsed[1]

    data_parsed["lsoc_permissions"] = data_parsed["lsoc_permissions"].replace("'", '"')

    try:
        user = User.objects.get(username=data_parsed["username"])
    except ObjectDoesNotExist as e:
        return return_message(AccountManagement.AccountEdit, False, str(e))

    form_account = AccountEditForm(data_parsed, instance=user)

    try:
        profile = LSOCProfile.objects.get(user_id=user.pk)
    except ObjectDoesNotExist as e:
        print("Presuming that the LSOCProfile is non-existant (might be the actual user!)...")

        profile = LSOCProfile(
            user = user,
            lsoc_permissions = data_parsed["lsoc_permissions"].replace('"', "'"),
            description = data_parsed["description"]
        )
        profile.save()

    form_profile = ProfileEditForm(data_parsed, instance=profile)

    if form_account.is_valid() and form_profile.is_valid():
        form_account.save()
        form_profile.user = user
        form_profile.save()

        if data_parsed["old_password"]:
            form_password = PasswordChangeForm(user, data_parsed)
            if form_password.is_valid():
                #usr =
                form_password.save()
                # This is needed to prevent the current user session from invalidating
                #update_session_auth_hash(request, usr)
            else:
                if form_password.non_field_errors():
                    print(form_password.non_field_errors())
                return return_message(AccountManagement.AccountEdit, False, str(form_password))

        return return_message(AccountManagement.AccountEdit)
    else:
        # Still not sure if this would ever need to be shown to the user...
        # So we just print it to the console
        if form_account.non_field_errors():
            print(form_account.non_field_errors())

        msg = ""
        msg += str(form_account.errors)
        msg += str(form_profile.errors)

        if form_profile.non_field_errors():
            print(form_profile.non_field_errors())

        return return_message(AccountManagement.AccountEdit, False, msg)

def staff_remove_account(data):
    data_parsed = parse_form(data, AccountManagement.AccountRemove)

    if data_parsed[0] == False:
        return data_parsed[1]
    else:
        data_parsed = data_parsed[1]

    try:
        user = User.objects.get(username=data_parsed["username"])

        try:
            profile = LSOCProfile.objects.get(user_id=user.pk)
            profile.delete()
        except:
            print("While removing an account, tried to remove the LSOC profile that does not exist, ignoring...")

        user.delete()

        return return_message(AccountManagement.AccountRemove)
    except ObjectDoesNotExist as e:
        return return_message(AccountManagement.AccountRemove, False, str(e))
    except Exception as e:
        print(e)
        return return_message(AccountManagement.AccountRemove, False, "The field 'username' is missing.")
