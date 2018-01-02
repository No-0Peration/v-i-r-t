from bottle import request, route, run
import libvirt
import requests, json
conn = None
hypie = ''

def template(command, vm, hypervisor):
    url = "http://" + str(hypervisor)+"/template"
    data = {'command': command, 'vm': vm}
    data_json = json.dumps(data)
    headers = {'Content-type': 'application/json'}
    response = requests.post(url, data=data_json, headers=headers)
    return response


# POST /controller command=<string:command>&vm=<string:vm name>&params=<string:additional parameters>&hypervisor=<string:hypervisorIP>
@route('/command', method='POST')
def command():
    if request.json['command']:
        command = request.json['command']
    else:
        return {"error": "no command"}
    if request.json['params']:
        params = request.json['params']
    else:
        params = ''
    if request.json['hypervisor']:
        hypervisor = request.json['hypervisor']
    else:
        return {"error": "no hypervisor"}
    if request.json['vm']:
        vm = request.json['vm']
    else:
        vm = ''

# check if the command is for a new hypervisor, then the current connection, if so make a new connection else use current connection
    global conn, hypie
    if hypervisor != hypie:
        hypie = hypervisor
        conn = libvirt.open('qemu+ssh://{0}/system'.format(hypervisor))

# command lists all vm's in a specified state: running, stopped, all
    if command == "list-vms":
        result = {}
        domains = conn.listAllDomains(0)

        if domains == None:
            return {"error": "There are no VM's on this hypervisor"}
        if params:
            if "running" in params:
                for domain in domains:
                    if domain.isActive():
                        state = 'running'
                    else:
                        state = 'off'
                    if state == 'running':
                        result[str(domain.name())] = state
                return json.dumps(result)
            elif "stopped" in params:
                for domain in domains:
                    if domain.isActive():
                        state = 'running'
                    else:
                        state = 'off'
                    if state == 'off':
                        result[str(domain.name())] = state
                return json.dumps(result)
            elif "all" in params:
                for domain in domains:
                    if domain.isActive():
                        state = 'running'
                    else:
                        state = 'off'
                    result[str(domain.name())] = state
            return json.dumps(result)
        else:
            for domain in domains:
                if domain.isActive():
                    state = 'running'
                else:
                    state = 'off'
                result[str(domain.name())] = state
            return json.dumps(result)


    #command to start an stopped VM
    elif command == "start-vm":
        dom = conn.lookupByName(vm)
        if dom.isActive():
            return {"result": "Allready started"}
        else:
            dom.create()
        return {"result": "started"}

    #command to stop an running VM
    elif command == "stop-vm":
        dom = conn.lookupByName(vm)
        if dom.isActive():
            dom.destroy()
        else:
            return {"result": "Allready stopped"}
        return {"result": "stopped"}

    #command to delete an vm
    elif command == "delete-vm":
        dom = conn.lookupByName(vm)
        if dom.isActive():
            return {"result": "Cannot delete an running VM"}
        else:
            dom.undefine()
            template('delete-vm', vm, hypervisor)
            return {"result": "R.I.P. {0}".format(vm)}
        return {"result": "stopped"}

    #get all hardware info from an specified VM
    elif command == "get-vm":
        dom = conn.lookupByName(vm)
        state, maxmem, mem, cpus, cput = dom.info()
        return {"state": str(state), "maxMemory": str(maxmem), "currentMemory": str(mem), "numberCPU": str(cpus), "cpuTime": str(cput)}

    #get all memory vs free memory of the hypervisor
    elif command == "get-mem":
        mem = conn.getInfo()
        memused = conn.getFreeMemory()
        return str('{"totalmem": "' + str(mem[1]) + 'MB", "memfree": "' + str(memused/1024/1024) + 'MB"}')

    #installs a new vm
    elif command == "new-vm":
        if params != None:
            template(params, vm, hypervisor)
        xmlconfig = "<domain type='qemu'><name>{0}</name><memory unit='MB'>1024</memory><vcpu>1</vcpu><on_poweroff>destroy</on_poweroff>" \
                "<on_reboot>restart</on_reboot><on_crash>destroy</on_crash><devices><emulator>/usr/bin/qemu-system-x86_64</emulator>" \
                "<disk type='file' device='disk'><source file='/var/lib/libvirt/images/{1}.img'/>" \
                "<driver name='qemu' type='raw'/><target dev='hda'/></disk><interface type='network'><source network='default'/>" \
                "<model type='virtio'/></interface><input type='mouse' bus='ps2'/><graphics type='vnc' port='-1' listen='127.0.0.1'/></devices>" \
                "<os><type arch='x86_64' machine='pc'>hvm</type><boot dev='hd'/></os></domain>".format(vm, vm)

        dom = conn.defineXML(xmlconfig)
        if dom == None:
            print('XML not Accepted')

        if dom.create() < 0:
            return {"error": "Cannot boot VM"}
        return {str(dom.name()): "has booted"}

    # command to delete an vm
    elif command == "update-vm":
        dom = conn.lookupByName(vm)
        dom.setMemory(params)
    return {str(dom.name()): " updated"}

    # if no commands match the request parameters, return an error
    return {"Error": "Not a valid command"}

run(host='0.0.0.0', port=11111, debug=True)
