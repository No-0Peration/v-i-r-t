from bottle import request, route, run
import libvirt

conn = None
hypie = ''

# POST /controller command=<string:command>&vm=<string:vm name>&params=<string:additional parameters>&hypervisor=<string:hypervisorIP>
@route('/command', method='POST')
def command():
    command = request.json['command']
    params = request.json['params']
    hypervisor = request.json['hypervisor']
    vm = request.json['vm']

# check if the command is for a new hypervisor, then the current connection, if so make a new connection else use current connection
    global conn, hypie
    if hypervisor != hypie:
        hypie = hypervisor
        conn = libvirt.open('qemu+ssh://{0}/system'.format(hypervisor))

# command lists all vm's in a specified state: running, stopped, all
    if command == "list-vms":
        result = "{"
        domains = conn.listAllDomains(0)

        if domains == None:
            return {"error": "There are no VM's on this hypervisor"}
        if "running" in params:
            for domain in domains:
                if domain.isActive():
                    state = 'running'
                else:
                    state = 'off'
                if state == 'running':
                    result += '\n\t"' + str(domain.name()) + '": "' + state + '"'
            return result + "\n}"
        elif "stopped" in params:
            for domain in domains:
                if domain.isActive():
                    state = 'running'
                else:
                    state = 'off'
                if state == 'off':
                    result += '\n\t"' + str(domain.name()) + '": "' + state + '"'
            return result + "\n}"
        elif "all" in params:
            for domain in domains:
                if domain.isActive():
                    state = 'running'
                else:
                    state = 'off'
                result += '\n\t"' + str(domain.name()) + '": "' + state + '"'
            return result + "\n}"
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
    # if no commands match the request parameters, return an error
    return {"Error": "Not a valid command"}

run(host='0.0.0.0', port=11111, debug=True)
