from flask import Flask
from flasgger import Swagger
from routes import routes

app = Flask(__name__)
app.register_blueprint(routes)
swagger = Swagger(app, template_file='swagger.yaml')

if __name__ == '__main__':
    app.run(debug=True)
