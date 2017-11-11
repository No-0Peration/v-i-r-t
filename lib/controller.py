from flask_restful import reqparse, Resource
from flask import jsonify


def list_vms(state, hypervisor, customer):
    command = "virsh %command%"
    result = run_command(command,hypervisor,customer)
    return result

def run_command(command,hypervisor,customer):
    connect_hypervisor()



# POST /controller command=<string:command>&hypervisor=<string:hypervisorID>&customer=<string:customerID>
class Libvirt(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('command')
        parser.add_argument('params')
        parser.add_argument('hypervisor')
        parser.add_argument('customer')
        args = parser.parse_args()
        if args['command'] == "list-vms":
            if args['params'] == "powered-on":
                result = list_vms(1,args['hypervisor'],args['customer'])
            result.append({'result': 'succeeded'})
            pass
        elif args['command'] == "get-vm":
            result = {'result': 'succeeded'}
            pass
        elif args['command'] == "new-vm":
            result = {'result': 'succeeded'}
            pass
        elif args['command'] == "start-vm":
            result = {'result': 'succeeded'}
            pass
        elif args['command'] == "stop-vm":
            result = {'result': 'succeeded'}
            pass
        elif args['command'] == "backup-vm":
            result = {'result': 'succeeded'}
            pass
        elif args['command'] == "restore-vm":
            result = {'result': 'succeeded'}
            pass
        elif args['command'] == "modify-vm":
            result = {'result': 'succeeded'}
            pass
        return jsonify(result)


