from flask_restful import reqparse, Resource
from flask import jsonify
import json
import xmltodict, xmltojson
import os

#class which connects to a hypervisor and performs a command requested from the api
def run_command(command,hypervisor):
    virsh_command = "virsh -c qemu+ssh://{0}/system {1}".format(hypervisor, command)
    print(virsh_command)
    result = os.popen(virsh_command).read().strip("\n")
    dictresult = xmltodict.parse(result, xml_attribs=True)
    result = json.dumps(dictresult, indent=4)
    print(result)
    return result

def virt_install(command,hypervisor,customer):
    virsh_command = "virt-install --connect=qemu+ssh://libvirtuser@{0} {1} {2}".format(hypervisor, customer, command)
    result = os.system(virsh_command)
    return result

# POST /controller command=<string:command>&params=<string:additional parameters>&hypervisor=<string:hypervisorIP>
class api(Resource):
    def post(self):
        # parse post arguments
        parser = reqparse.RequestParser()
        parser.add_argument('command')
        parser.add_argument('params')
        parser.add_argument('hypervisor')
        parser.add_argument('customer')
        args = parser.parse_args()

        if args['command'] == "list-vms":
            print("command recieved list-vms")
            if args['params'] == "powered-on":
                command = "list --all"
                result = run_command(command,args['hypervisor'])
            elif args['params'] == "powered-off":
                command = "list --all"
                result = run_command(command, args['hypervisor'])
            else:
                command = "dumpxml sne1"
                result = run_command(command, args['hypervisor'])

            return result

        elif args['command'] == "get-vm":
            command = "virsh list {0}".format(args['params'])
            result = run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "vm-info":
            command = "dominfo {0}".format(args['params'])
            result = run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "new-vm":
            if args['params'] == "win7":
                command = "virt-clone windows7VM"
            elif args['params'] == "ubuntu":
                command = "virt-clone ubuntuVM"
            elif args['params'] == "debian":
                command = "virt-clone debianVM"
            result = virt_install(command, args['hypervisor'], args['customer'])
            return jsonify(result) # return VMnaam

        elif args['command'] == "start-vm":
            command = "start {0}".format(args['params'])
            result = run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "stop-vm":
            command = "stop {0}".format(args['params'])
            result = run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "backup-vm":
            command = "snapshot-create {0}".format(args['params'])
            result = run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "restore-vm":
            command = "snapshot-revert {0}".format(args['params'])
            result = run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "modify-vm":
            command = "setmem {0}".format(args['params'])
            result = run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

# live migration or just migration
# virsh migrate --live GuestName DestinationURL
