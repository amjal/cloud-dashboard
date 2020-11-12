import os

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
            else:
                temp_out[arr[0]] = arr[1].replace('\n', '')
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
    info_of_vms = out_vms
    return render(request, 'index.html', out_vms)


def change_status(request):
    vm_name = request.GET.get('vm')
    new_state = request.GET.get('new_state')
    command = None
    if new_state == 'off':
        command = 'VBoxManage controlvm  ' + vm_name + ' poweroff'
    elif new_state == 'on':
        command = 'VBoxManage startvm ' + vm_name + ' --type headless'
    if command is not None:
        os.system(command)
    return redirect('dashboard')

