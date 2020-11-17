import os
import re

from django.http import HttpResponse
from django.shortcuts import redirect, render

info_of_vms = {}


def get_vms():
    os.system('VBoxManage list -l vms >> text.txt')
    file1 = open('text.txt', 'r')
    lines = file1.readlines()
    out = {}
    temp_out = {}
    count = 0
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
    out[vm] = temp_out
    os.system('rm text.txt')
    return out


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
    print(out_vms)
    return render(request, 'index.html', {'vms': out_vms})


def change_status(request):
    vm_name = request.POST.get('vm')
    new_state = request.POST.get('new_state')
    command = None
    if new_state == 'off':
        command = 'VBoxManage controlvm  ' + vm_name + ' poweroff'
    elif new_state == 'on':
        command = 'VBoxManage startvm ' + vm_name + ' --type headless'
    if command is not None:
        os.system(command)
    return HttpResponse('status changed')


def clone(request):
    vm = request.GET.get('vm')
    vm_name = request.GET.get('vm_name')
    if vm is not None and vm_name is not None:
        command = 'VBoxManage clonevm ' + vm + ' --name=' + vm_name + ' --register --mode=all '
        os.system(command)
    return redirect('dashboard')


def change_config(request):
    vm_name = request.GET.get('vm_name')
    cores = request.GET.get('cores')
    ram = request.GET.get('ram')
    if vm_name is not None and cores is not None and ram is not None:
        command = 'VBoxManage modifyvm ' + vm_name + ' --memory ' + ram + ' --cpus ' + cores
        os.system(command)
    return redirect('dashboard')


def remove(request):
    vm_name = request.GET.get('vm_name')
    if vm_name is not None:
        command = 'VBoxManage unregistervm ' + vm_name + ' --delete'
        os.system(command)
    return redirect('dashboard')


def command(request):
    user_command = request.GET.get('command')
    vm = request.GET.get('vm')
    user = request.GET.get('user')
    password = request.GET.get('password')
    user_command_parts = user_command.split()
    command = None
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
