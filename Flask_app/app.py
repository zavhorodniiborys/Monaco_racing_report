from flasgger import Swagger
from flask import Flask

app = Flask(__name__)

from Flask_app.controllers.controller_api_endpoints import api_endpoints

app.register_blueprint(api_endpoints)

Swagger(app)

if __name__ == '__main__':
    app.run(debug=True)
