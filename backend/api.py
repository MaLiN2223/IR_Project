from flask import Flask
from flask_restful import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)
# cors = CORS(app, resource={
#     r"/*":{
#         "origins":"*"
#     }
# })


limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])


@app.before_first_request
def startup():
    print("Starting the app...")


class SearchEngine(Resource):
    def get(self, query):
        return query


class Admin(Resource):
    def get(self):
        return "admin!"


api.add_resource(SearchEngine, "/engine/<string:query>")
api.add_resource(Admin, "/admin/")
