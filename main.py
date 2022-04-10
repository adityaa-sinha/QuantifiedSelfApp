from flask import Flask
from application.database import db
from flask_restful import Api
from application.api import *
from application.prettyts import prettyts


app=None 
api=None

def create_app():
    app = Flask(__name__)
    app.jinja_env.filters['prettyts'] = prettyts
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectdb.sqlite3'
    db.init_app(app)
    app.app_context().push()
    api=Api(app)
    return app, api
    
app,api=create_app()


from application.controllers import *

api.add_resource(TrackersAPI, '/api/trackers/<int:user_id>', '/api/trackers/<int:user_id>/<int:tracker_id>')
api.add_resource(TrackerLogsAPI, '/api/trackerlogs/<int:user_id>/<int:tracker_id>', '/api/trackerlogs/<int:user_id>/<int:tracker_id>/<int:log_id>')

if __name__ == "__main__":
    app.run()