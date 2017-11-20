from flask_restful import reqparse, Resource
from flask import jsonify
import os

#class which connects to a hypervisor and performs a command requested from the api
class libvirt(Resource):
    def run_command(self,command,hypervisor):
        virsh_command = "virsh -c qemu+ssh://libvirtuser@{0} {1}".format(hypervisor, command)
        print(str(virsh_command))
        result = os.command(virsh_command)
        return result

    def virt_install(self,command,hypervisor,customer):
        virsh_command = "virt-install --connect=qemu+ssh://libvirtuser@{0} {1} {2}".format(hypervisor, customer, command)
        result = os.command(virsh_command)
        return result

# POST /controller command=<string:command>&params=<string:hypervisorID>&customer=<string:customerID>
class api(Resource):
    def post(self):
        # parse post arguments
        parser = reqparse.RequestParser()
        parser.add_argument('command')
        parser.add_argument('params')
        parser.add_argument('hypervisor')
        parser.add_argument('customernetwork')
        args = parser.parse_args()

        if args['command'] == "list-vms":
            if args['params'] == "powered-on":
                command = "virsh list"
                result = libvirt.run_command(command,args['hypervisor'],args['customer'])
            elif args['params'] == "powered-off":
                command = "virsh list"
                result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            else:
                command = "virsh list"
                result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "get-vm":
            command = "virsh list {0}".format(args['params'])
            result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "vm-info":
            command = "dominfo {0}".format(args['params'])
            result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "new-vm":
            if args['params'] == "win7":
                command = "virt-clone windows7VM"
            elif args['params'] == "ubuntu":
                command = "virt-clone ubuntuVM"
            elif args['params'] == "debian":
                command = "virt-clone debianVM"
            result = libvirt.virt_install(command, args['hypervisor'], args['customer'])
            return jsonify(result) # return VMnaam

        elif args['command'] == "start-vm":
            command = "start {0}".format(args['params'])
            result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "stop-vm":
            command = "stop {0}".format(args['params'])
            result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "backup-vm":
            command = "snapshot-create {0}".format(args['params'])
            result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "restore-vm":
            command = "snapshot-revert {0}".format(args['params'])
            result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)

        elif args['command'] == "modify-vm":
            command = "setmem {0}".format(args['params'])
            result = libvirt.run_command(command, args['hypervisor'], args['customer'])
            return jsonify(result)



