from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from lib import controller

app = Flask(__name__)
api = Api(app)
CORS(app)

api.add_resource(controller.api, '/controller')

if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0', port=8080)
