import os
import re

from django.http import HttpResponse
from django.shortcuts import redirect, render


# function for getting data from VBoxManage

def get_vms():
    # command for getting list of vms
    os.system('VBoxManage list -l vms >> text.txt')
    file1 = open('text.txt', 'r')
    lines = file1.readlines()
    out = {}
    temp_out = {}
    count = 0
    vm = None
    for line in lines:
        arr = line.split(':')
        if len(arr) == 2:
            if arr[0] == 'Name':
                if len(temp_out) > 0:
                    out[vm] = temp_out
                    temp_out = {}
                vm = arr[1].replace('\n', '')
                vm = re.sub(r'\s+', '', vm)
            else:
                temp_out[arr[0]] = arr[1].replace('\n', '')
                temp_out[arr[0]] = re.sub(r'\s+', '', temp_out[arr[0]])
        elif len(arr) > 2 and arr[0] == 'State' and 'off' in arr[1]:
            temp_out['state'] = 'off'
        elif len(arr) > 2 and arr[0] == 'State' and 'running' in arr[1]:
            temp_out['state'] = 'on'
        elif len(arr) == 1 and 'Memory size' in arr[0]:
            temp_out['ram'] = arr[0].split()[2]
    if vm is not None:
        out[vm] = temp_out
    os.system('rm text.txt')
    return out


# main view of our website that show all vms
def dashboard(request):
    out_vms = {}
    vms = get_vms()
    for key in vms:
        vm = vms.get(key)
        out_vms[key] = {
            'name': key,
            'os': vm.get('Guest OS'),
            'ram': vm.get('ram'),
            'num_of_cpus': vm.get('Number of CPUs'),
            'state': vm.get('state')
        }
    return render(request, 'index.html', {'vms': out_vms})


# view for changing status of vm

def change_status(request):
    vm_name = request.POST.get('vm')
    new_state = request.POST.get('new_state')
    command = None
    # check if new state is off
    if new_state == 'off':
        # command for turning off vm
        command = 'VBoxManage controlvm  ' + vm_name + ' poweroff'
    # check if new state is on
    elif new_state == 'on':
        # command for turning on vm
        command = 'VBoxManage startvm ' + vm_name + ' --type headless'
    if command is not None:
        os.system(command)
    return HttpResponse('status changed')


# view for cloning vm
def clone(request):
    vm = request.POST.get('vm')
    vm_name = request.POST.get('vm_name')
    if vm is not None and vm_name is not None:
        # command for cloning vm
        command = 'VBoxManage clonevm ' + vm + ' --name=' + vm_name + ' --register --mode=all '
        os.system(command)
    return redirect('dashboard')


# view for changing config of vm
def change_config(request):
    vm_name = request.POST.get('vm')
    cores = request.POST.get('core-numbers')
    ram = request.POST.get('ram-space')
    response = ""
    if vm_name is not None:
        # making command of changing vm config
        command = 'VBoxManage modifyvm ' + vm_name
        if ram is not None:
            command = command + ' --memory ' + ram
            response = response + "ram changed "
        if cores is not None:
            command = command + ' --cpus ' + cores
            response = response + "cpus changed "
        os.system(command)
    return HttpResponse(response)


# command for removing vm
def remove(request):
    vm_name = request.POST.get('vm')
    if vm_name is not None:
        # command for remove vm
        command = 'VBoxManage unregistervm ' + vm_name + ' --delete'
        os.system(command)
    return redirect('dashboard')


# view for running command in vms
def command(request):
    user_command = request.POST.get('command')
    vm = request.POST.get('vm')
    user = request.POST.get('user')
    password = request.POST.get('password')
    user_command_parts = user_command.split()
    command = None
    # making command for running command
    if len(user_command_parts) > 0:
        main_command = user_command_parts[0]
        command = 'VBoxManage guestcontrol ' + vm + ' run --exe /bin/' + main_command + ' ' + \
                  user_command + ' --username ' + user + ' --password ' + \
                  password + '  --wait-stdout'
    else:
        command = 'VBoxManage guestcontrol ' + vm + ' run --exe /bin/' + user_command + \
                  user_command + ' --username ' + user + ' --password ' + \
                  password + '  --wait-stdout'
    if command is not None:
        system_result = os.system(command)
        result = os.popen(command).read()
        if system_result == 0:
            return HttpResponse(result)
        else:
            return HttpResponse('your command has problem permission or something else')
    return HttpResponse('Something went wrong!')
