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

    if command == "list-vms":
        print("command recieved list-vms")
        result = "{"
        domainIDs = conn.listDomainsID()
        print("domids:" + str(domainIDs))
        if domainIDs == None:
            print('Failed to get a list of domain IDs')
            return {"error": "There are no VM's on this hypervisor"}
        if "running" in params:
            for domainID in domainIDs:
                print(domainID)
                dom = conn.lookupByID(domainID)
                print(dom.isActive())
                if dom.isActive():
                    state = 'running'
                else:
                    state = 'off'
                if state == 'running':
                    print('in running')
                    result += '\n\t"'+ str(dom.name()) + '": "' + state + '"'
            return result + "\n}"
        elif "stopped" in params:
            for domainID in domainIDs:
                dom = conn.lookupByID(domainID)
                if dom.isActive():
                    state = 'running'
                else:
                    state = 'off'
                if state == 'off':
                    result += '\n\t"'+ str(dom.name()) + '": "' + state + '"'
            return result + "\n}"
        elif "all" in params:
            for domainID in domainIDs:
                dom = conn.lookupByID(domainID)
                if dom.isActive():
                    state = 'running'
                else:
                    state = 'off'
                result += '\n\t"'+ str(dom.name()) + '": "' + state + '"'
            return result + "\n}"
    elif command == "start-vm":
        dom = conn.lookupByName(vm)
        if dom.isActive():
            return {"result": "Allready started"}
        else:
            dom.create()
        return {"result": "started"}
    elif command == "stop-vm":
        dom = conn.lookupByName(vm)
        if dom.isActive():
            dom.destroy()
        else:
            return {"result": "Allready started"}
        return {"result": "stopped"}
    elif command == "get-mem":
        mem = conn.getInfo()
        memused = conn.getFreeMemory()
        return str('{"totalmem": "' + str(mem[1]) + 'MB", "memfree": "' + str(memused/1024/1024) + 'MB"}')
    return run_command(virshCommand, hypervisor)

run(host='0.0.0.0', port=11111, debug=True)
