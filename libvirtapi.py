from bottle import request, route, run
import libvirt
import os, re

conn = libvirt.open('qemu+ssh://192.168.50.12/system')

def run_command(command,hypervisor):
    virshCommand = "virsh -c qemu+ssh://{0}/system {1}".format(hypervisor, command)
    result = os.popen(virshCommand).read()
    result = result.splitlines()
    newresult = []
    first = 0
    for i in result[2:]:
        if i == " ":
            if first == 0:
                i = ""
                first = 1
        else:
            i = re.sub('[\r\n\t\f\v]', '', i)
            first = 0
        newresult.append(i)
        result = newresult[0].split()
        result = '{"id": ' + result[0] + ', "hostname": ' + '"' + result[1] + '", "state": ' + str(result[2:]).strip(
            "[]").replace("\'", "\"") + '}'
    return result

def virt_install(command,hypervisor):
    virsh_command = "virt-install --connect=qemu+ssh://{0}{1}".format(hypervisor, command)
    result = response_parser(os.popen(virsh_command).read().strip("\n"))
    return result

def parse_params(params):
    return params.split(",").replace(" ", "")

def response_parser(result):
    parsed_result = ""
    return parsed_result

# POST /controller command=<string:command>&vm=<string:vm name>&params=<string:additional parameters>&hypervisor=<string:hypervisorIP>
@route('/command', method='POST')
def command():
    command = request.json['command']
    params = request.json['params']
    hypervisor = request.json['hypervisor']
    vm = request.json['vm']
    virshCommand = ""

    if command == "list-vms":
        print("command recieved list-vms")
        if "running" in params:
            virshCommand = "list --all"
        elif "stopped" in params:
            virshCommand = "list --all"
        elif "all" in params:
            virshCommand = "list --all"
    elif command == "start-vm":
        virshCommand = "start {0}".format(vm)
    elif command == "stop-vm":
        virshCommand = "destroy {0}".format(vm)
    elif command == "get-mem":
        mem = conn.getInfo()
        memused = conn.getFreeMemory()
        return str('{"totalmem": "' + str(mem[1]) + 'MB", "memfree": "' + str(memused/1024/1024) + 'MB"}')
    return run_command(virshCommand, hypervisor)

run(host='0.0.0.0', port=11111, debug=True)
