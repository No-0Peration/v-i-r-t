from bottle import request, route, run
import shutil, os


@route('/template', method='POST')
def command():
    command = request.json['command']
    vm = request.json['vm']

    if command == 'new-disk1':
        shutil.copyfile('/var/lib/libvirt/images/templ1.img', '/var/lib/libvirt/images/' + vm + '.img')
        return {"result": "image created"}
    elif command == 'new-disk2':
        shutil.copyfile('/var/lib/libvirt/images/templ2.img', '/var/lib/libvirt/images/' + vm + '.img')
        return {"result": "image created"}
    elif command == 'new-disk3':
        shutil.copyfile('/var/lib/libvirt/images/templ3.img', '/var/lib/libvirt/images/' + vm + '.img')
        return {"result": "image created"}
    elif command == 'delete-vm':
        os.remove('/var/lib/libvirt/images/' + vm + '.img')
        return {"result": "image removed"}

run(host='0.0.0.0', port=80, debug=True)