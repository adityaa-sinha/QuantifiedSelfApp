from datetime import datetime
from flask_restful import Resource,fields,marshal_with,reqparse
from application.models import *
from application.validation import *
from application.database import db
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt

t_parser = reqparse.RequestParser()
t_parser.add_argument("name")
t_parser.add_argument("description")
t_parser.add_argument("tracker_type")
t_parser.add_argument("settings")

t_update_parser = reqparse.RequestParser()
t_update_parser.add_argument("name")
t_update_parser.add_argument("description")

t_fields = {"name":fields.String,"description":fields.String,"tracker_type":fields.String,"settings":fields.String,"created_by":fields.Integer}
l_fields = {"log_id":fields.Integer,"timestamp":fields.DateTime, "value":fields.String, "note": fields.String}


#CRUD FOR TRACKERS

class TrackersAPI(Resource):

    #Create
    @marshal_with(t_fields)
    def post(self,user_id):
        args = t_parser.parse_args()
        name = args.get("name",None)
        description = args.get("description",None)
        tracker_type = args.get("tracker_type",None)
        settings = args.get("settings",None)
        
        #check if user exists or not
        u = Users.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError()
        if name is None:
            raise BussinessValidationError(400,'T001','Tracker Name is required')
        if tracker_type is None:
            raise BussinessValidationError(400,'T002','Tracker type is required')
    
        #check if there is a tracker created by the user with same name and tracker type before
        t = Trackers.query.filter_by(name=name,tracker_type=tracker_type,created_by = user_id).first()
        #if yes
        if t:
            raise FourZeroNineError()
        #else
        else:
            new = Trackers(name=name,description=description,tracker_type=tracker_type,settings=settings,created_by=user_id)
            db.session.add(new)
            db.session.commit()
            return new,201

    #Read    
    @marshal_with(l_fields)
    def get(self,user_id,tracker_id):

        u = Users.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError()
        t = Trackers.query.filter_by(tracker_id=tracker_id,created_by = user_id).first()
        if t is None:
            raise NotFoundError()
        #query log table
        l = Logs.query.filter_by(luser_id = user_id,ltracker_id = tracker_id).all()
        #if no log
        if len(l)==0:
            raise NotFoundError()
        #if log, plot graph
        else:
            #query Trackers table
            #if tracker_type is boolean/mcq then pie chart, if numerical/time duartion then line chart
            tr = Trackers.query.filter_by(tracker_id = tracker_id, created_by = user_id).first()
            if tr.tracker_type == 'Numerical' or tr.tracker_type == 'Time Duration':
                d={}
                for i in l:
                    try:
                        d[i.timestamp] = i.value
                    except KeyError:
                        d[i.timestamp] = i.value
                x = [item[0] for item in sorted(d.items())]
                y = [float(item[1]) for item in sorted(d.items())]
                plt.clf()
                plt.xlabel("TimeStamp")
                plt.ylabel("Value")
                plt.xticks(rotation=90)
                plt.plot(x,y)
                plt.savefig("static/img/plot.png", bbox_inches="tight")
                plt.close()

            if tr.tracker_type == 'Boolean' or tr.tracker_type == 'Multiple Choice':  
                val = [str(item.value) for item in l]
                d= {}
                for v in val:
                    try:
                        d[v]+=1
                    except KeyError:
                        d[v]=1
                x = list(d.keys())
                y = list(d.values())
                plt.clf()
                plt.pie(y, labels = x,shadow=True, autopct="%1.1f%%")
                plt.savefig("static/img/plot.png", bbox_inches="tight")
                plt.close()

        #return values
        return l
    
    @marshal_with(t_fields)
    def put(self,user_id,tracker_id):
        args = t_update_parser.parse_args()
        name = args.get("name",None)
        description = args.get("description",None)

        u = Users.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError()
        t = Trackers.query.filter_by(tracker_id=tracker_id, created_by=user_id).first()
        if t is None:
            raise NotFoundError()

        if name is None:
            raise BussinessValidationError('400','T001','Tracker Name is required')
        
        tn = Trackers.query.filter_by(created_by=user_id,name=name,description=description).first()
        if tn:
            raise FourZeroNineError()

        t.name = name
        t.description = description
        db.session.commit()
        return t,200

    def delete(self,user_id,tracker_id):
        u = Users.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError()
        t = Trackers.query.filter_by(created_by=user_id, tracker_id=tracker_id).first()
        if t is None:
            raise NotFoundError()
        l = Logs.query.filter_by(luser_id=user_id,ltracker_id=tracker_id).all()
        db.session.delete(t)
        for i in l:
            db.session.delete(i)
        db.session.commit()
        raise AllOkError()

#CRUD FOR LOGS

log_parser = reqparse.RequestParser()
log_parser.add_argument("timestamp")
log_parser.add_argument("value")
log_parser.add_argument("note")

class TrackerLogsAPI(Resource):

    #Create
    @marshal_with(l_fields)
    def post(self,user_id,tracker_id):
        args = log_parser.parse_args()
        timestamp = args.get("timestamp",None)
        value = args.get("value",None)
        note = args.get("note",None)
        u = Users.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError()
        t = Trackers.query.filter_by(tracker_id=tracker_id,created_by = user_id).first()
        if t is None:
            raise NotFoundError()
        if timestamp is None:
            raise BussinessValidationError(400,'L001','Timestamp is required')
        if value is None:
            raise BussinessValidationError(400,'L002','Value is required')
        if note is None:
            raise BussinessValidationError(400,'L003','Note is required')
        
        new = Logs(luser_id=user_id,ltracker_id=tracker_id,timestamp=datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S.%f"),value=value,note=note)
        db.session.add(new)
        db.session.commit()

        #Updating last tracked and last logged value in trackers table for corresponding tracker
        l = Logs.query.filter_by(ltracker_id=tracker_id,luser_id=user_id).all()
        loglist = []
        for i in l:
            loglist.append(i.log_id)
        loglist.sort(reverse=True)
        last_l = Logs.query.filter_by(ltracker_id=tracker_id,luser_id=user_id,log_id=loglist[0]).first()
        t.last_tracked = last_l.timestamp
        t.last_log = last_l.value
        db.session.commit()
        return new,201

    #Update
    @marshal_with(l_fields)    
    def put(self, user_id,tracker_id,log_id):
        args = log_parser.parse_args()
        timestamp = args.get("timestamp",None)
        value = args.get("value",None)
        note = args.get("note",None)
        u = Users.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError()
        t = Trackers.query.filter_by(tracker_id=tracker_id,created_by = user_id).first()
        if t is None:
            raise NotFoundError()
        if timestamp is None:
            raise BussinessValidationError(400,'L001','Timestamp is required')
        if value is None:
            raise BussinessValidationError(400,'L002','Value is required')
        if note is None:
            raise BussinessValidationError(400,'L003','Note is required')
        
        l = Logs.query.filter_by(log_id=log_id,luser_id=user_id,ltracker_id=tracker_id).first()
        if l is None:
            raise NotFoundError()
        l.timestamp = datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S.%f")
        l.value = value
        l.note = note
        db.session.commit()

        #Updating trackers table's last tracked and last log attribute with new value..
        l = Logs.query.filter_by(ltracker_id=tracker_id,luser_id=user_id).all()
        if len(l)==0:
            t.last_tracked = None
            db.session.commit()
            raise AllOkError()
        loglist = []
        for i in l:
            loglist.append(i.log_id)
        loglist.sort(reverse=True)
        last_l = Logs.query.filter_by(ltracker_id=tracker_id,luser_id=user_id,log_id=loglist[0]).first()
        t.last_tracked = last_l.timestamp
        t.last_log = last_l.value
        db.session.commit()
        return l,200

    #Delete
    def delete(self,user_id,tracker_id,log_id):
        u = Users.query.filter_by(user_id=user_id).first()
        if u is None:
            raise NotFoundError()
        t = Trackers.query.filter_by(tracker_id=tracker_id,created_by = user_id).first()
        if t is None:
            raise NotFoundError()
        l = Logs.query.filter_by(log_id=log_id,luser_id=user_id,ltracker_id=tracker_id).first()
        if l is None:
            raise NotFoundError()
        db.session.delete(l)
        db.session.commit()
        l = Logs.query.filter_by(ltracker_id=tracker_id,luser_id=user_id).all()
        if len(l)==0:
            t.last_tracked = None
            t.last_log = None
            db.session.commit()
            raise AllOkError()
        loglist = []
        for i in l:
            loglist.append(i.log_id)
        loglist.sort(reverse=True)
        last_l = Logs.query.filter_by(ltracker_id=tracker_id,luser_id=user_id,log_id=loglist[0]).first()
        t.last_tracked = last_l.timestamp
        t.last_log = last_l.value
        db.session.commit()
        raise AllOkError()
