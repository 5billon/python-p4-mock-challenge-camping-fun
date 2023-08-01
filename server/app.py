#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class Campers(Resource):

    def get(self):
        return make_response([c.to_dict(rules = ('-signups',)) for c in Camper.query.all()])
    
    def post(self):
        data = request.json
        try:
            camper = Camper(name = data['name'], age = data['age'])
        except ValueError as v_error:
            return make_response({'errors': [str(v_error)]}, 422)
        except KeyError as k_error:
            return make_response({'errors': [str(k_error)]}, 422)

        db.session.add(camper)
        db.session.commit()
        return make_response(camper.to_dict(rules = ('-signups',)), 201)

api.add_resource(Campers, '/campers')

class CampersById(Resource):

    def get(self, id):
        camper = Camper.query.filter_by(id = id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        return make_response(camper.to_dict(), 200)

    def patch(self, id):
        camper = Camper.query.filter_by(id = id).first()
        if not camper:
            return make_response({"error": "Camper not found"}, 404)
        data = request.json
        for key in data:
            try:
                setattr(camper, key, data[key])
            except ValueError as v_error:
                return make_response({'errors':[str(v_error)]}, 422)
        db.session.commit()
        return make_response(camper.to_dict(rules = ('-signups',)))

api.add_resource(CampersById, '/campers/<id>')

class Activities(Resource):
    def get(self):
        return make_response([ a.to_dict() for a in Activity.query.all()])

api.add_resource(Activities, '/activities')

class ActivitiesById(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id = id).first()
        if not activity:
            return make_response({"error": "Activity not found"}, 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response('', 204)

api.add_resource(ActivitiesById, '/activities/<int:id>')


class Signups(Resource):
    def post(self):
        data = request.json
        try:
            signup = Signup(camper_id=data['camper_id'], activity_id=data['activity_id'], time=data['time'])
        except ValueError as v_error:
            return make_response({'errors': [str(v_error)]}, 422)
        db.session.add(signup)
        db.session.commit()
        return make_response(signup.to_dict(), 204)

api.add_resource(Signups, '/signups')

@app.route('/')
def home():
    return ''



# @app.route('/campers', methods=['GET', 'POST'])
# def camper():
#     if request.method == 'GET':
#         all_camper = Camper.query.all()
#         camper_list = [camper.to_dict() for camper in all_camper]
#         response = make_response(camper_list, 200)
#         return response
#     elif request.method == 'POST':
#         data = request.get_json()
#         try:
#             camper = Camper(
#                 name=data['name'],
#                 age=data['age'],
#             )
#             db.session.add(camper)
#             db.session.commit()
#             response = make_response(scientist.to_dict(), 201)
#             return response
#         except Exception as error:
#             response_dict = {'error':[error.__str__()]}
#             response = make_response(response_dict, 422)
#             return response

# @app.route('/campers/<int:id>')
# def camper_by_id(id):
#     camper = Camper.query.filter_by(id=id).first()
#     if camper:
#         response = make_response(camper.to_dict(rules=('signups', '-signup.camper',)), 200)
#         return response
#     else:
#         response = make_response({'error':'Camper not found'}, 404)
#         return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
