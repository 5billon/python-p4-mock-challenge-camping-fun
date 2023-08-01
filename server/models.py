from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)

    # Add relationship
    signups = db.relationship('Signup', back_populates='activity', cascade = 'all, delete-orphan')
    campers = association_proxy('signups', 'camper')

    # Add serialization rules
    serialize_rules = ('-signups','-camper.signups',)
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    # Add relationship
    signups = db.relationship('Signup', back_populates='camper')
    activities = association_proxy('signups', 'activity')

    # Add serialization rules
    serialize_rules = ('-signups.camper','-signups.activity.signups')
    
    # Add validation
    @validates('name')
    def validate_camper_name(self, key, new_camper_name):
        if not new_camper_name:
            raise ValueError('Please give a new camper name.')
        return new_camper_name

    @validates('age')
    def validate_camper_age(self, key, new_camper_age):
        if not  8 <= new_camper_age <= 18:
            raise ValueError('Please enter and age between 8 and 18.')
        return new_camper_age
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer, nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)

    # Add relationships
    activity = db.relationship('Activity', back_populates='signups')
    camper = db.relationship('Camper', back_populates='signups')

    # Add serialization rules
    #serialize_rules = ('-camper.signups', '-activity.signups')

    # Add validation
    @validates('time')
    def validate_time(self, key, new_time):
        if not 0 <= new_time <= 23:
            raise ValueError('Please enter a time between the values of 0 to 23.')
        return new_time

    @validates('activity_id')
    def validate_time(self, key, new_activity_id):
        if not new_activity_id:
            raise ValueError('A activity id must exist.')
        return new_activity_id
    
    @validates('camper_id')
    def validate_time(self, key, new_camper_id):
        if not new_camper_id:
            raise ValueError('A camper id must exist.')
        return new_camper_id
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
