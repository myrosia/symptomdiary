from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

from sqlalchemy.dialects.sqlite import INTEGER as Integer 
from sqlalchemy.dialects.sqlite import DATE as Date, TIME as Time, BOOLEAN as Boolean

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
import sys


Base = declarative_base()

class Record(Base):
    __tablename__ = 'entries'

    record_id = Column(Integer, primary_key=True)
    date_entered = Column(Date, unique=True)
    time_entered = Column(Time)
    notes = Column(String)
    

class PainInfo(Base):
    __tablename__ = 'painlevel'
    record_id = Column(Integer, ForeignKey("entries.record_id"), primary_key=True)
    average_pain = Column(Integer, name='averagepain')
    max_pain = Column(Integer(unsigned=True), name='maxpain')
    record = relationship("Record", backref=backref('pain_info', uselist=False))
    
    def __init__(self, record_id, averagepain=None, maxpain=None):
        self.record_id = record_id
        self.average_pain = averagepain
        self.max_pain = maxpain




class PainSite(Base):
    __tablename__ = 'painsite'  
    site_id = Column(Integer, primary_key=True)
    location = Column(String, unique=True)
    active = Column(Boolean, nullable=False, default=True)

    def __init__(self, site_id, location):
        if (site_id is not None):
            self.site_id = site_id
        self.location = location
        ## The defaults are applied only on INSERT/flush
        ## But we need to use them earlier, when we are creating new entries, before they are inserted
        ## So we have to init them manually
        self.active = self.__table__.c.active.default.arg


    

class PainSiteInfo(Base):
    __tablename__ = 'paindetail'
    record_id = Column(Integer, ForeignKey("entries.record_id"), primary_key=True)
    site_id = Column(Integer, ForeignKey("painsite.site_id"), primary_key=True)
    painlevel = Column(Integer(unsigned=True))

    record = relationship("Record", backref=backref('pain_site_info'))
    site = relationship("PainSite")
 
                      
    def __init__(self, record_id, site_id, painlevel=None):
        self.record_id = record_id
        self.site_id = site_id
        self.painlevel = painlevel
 

class Symptom(Base):
    __tablename__ = 'symptom'
    symptom_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    active = Column(Boolean, nullable=False, default=True)


    def __init__(self, symptom_id, name):
        self.symptom_id = symptom_id
        self.name = name
        ## The defaults are applied only on INSERT/flush
        ## But we need to use them earlier, when we are creating new entries, before they are inserted
        ## So we have to init them manually
        self.active = self.__table__.c.active.default.arg


class SymptomInfo(Base):
    __tablename__ = 'symptomdetail'

    record_id = Column(Integer, ForeignKey("entries.record_id"), primary_key=True)
    symptom_id = Column(Integer, ForeignKey("symptom.symptom_id"), primary_key=True)
    intensity = Column(Integer(unsigned=True))

    record = relationship("Record", backref=backref('symptom_info'))
    symptom = relationship("Symptom")

    def __init__(self, record_id, symptom_id, intensity):
        self.record_id = record_id
        self.symptom_id = symptom_id
        self.intensity = intensity


class Medication(Base):
    __tablename__ = 'medication'  
    __table_args__ = (
            UniqueConstraint('name', 'unit', 'dosage'),
            {}
        )
    medication_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    dosage = Column(Integer(unsigned=True))
    quantity = Column(Integer(unsigned=True), nullable=False)
    frequency = Column(String)
    active = Column(Boolean, nullable=False, default=True)


    def __init__(self, medication_id = None, name = "", unit=None, dosage=None, quantity=None, frequency=None):
        self.name = name
        self.unit = unit
        self.dosage = dosage
        self.quantity = quantity
        self.frequency = frequency
        ## The defaults are applied only on INSERT/flush
        ## But we need to use them earlier, when we are creating new entries, before they are inserted
        ## So we have to init them manually
        self.active = self.__table__.c.active.default.arg
        

class MedicationInfo(Base):
    __tablename__ = 'medicationdetail'

    record_id = Column(Integer, ForeignKey("entries.record_id"), primary_key=True)
    medication_id = Column(Integer, ForeignKey("medication.medication_id"), primary_key=True)
    quantity = Column(Integer(unsigned=True), nullable=False)

    record = relationship("Record", backref=backref('medication_info'))
    medication = relationship("Medication")

    def __init__(self, record_id, medication_id, quantity):
        self.record_id = record_id
        self.medication_id = medication_id
        self.quantity = quantity


class Treatment(Base):
    __tablename__ = 'treatment'  

    treatment_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    provider = Column(String)
    frequency = Column(String)
    active = Column(Boolean, nullable=False, default=True)

    def __init__(self, treatment_id=None, name="", provider=None, frequency=None):
        self.treatmet_id = treatment_id
        self.name = name
        self.provider = provider
        self.frequency = frequency
        ## The defaults are applied only on INSERT/flush
        ## But we need to use them earlier, when we are creating new entries, before they are inserted
        ## So we have to init them manually
        self.active = self.__table__.c.active.default.arg
        

class TreatmentInfo(Base):
    __tablename__ = 'treatmentdetail'

    record_id = Column(Integer, ForeignKey("entries.record_id"), primary_key=True)
    treatment_id = Column(Integer, ForeignKey("treatment.treatment_id"), primary_key=True)
    times_per_day = Column(Integer, nullable=False, default=0)
    hours = Column(Integer)
    minutes = Column(Integer)

    record = relationship("Record", backref=backref('treatment_info'))
    treatment = relationship("Treatment")

    def __init__(self, record_id, treatment_id, times_per_day=None, hours=None, minutes=None):
        self.record_id = record_id
        self.treatment_id = treatment_id
        self.times_per_day = times_per_day
        self.hours = hours
        self.minutes = minutes


class Activity(Base):
    __tablename__ = 'activity'

    activity_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    active = Column(Boolean, nullable=False, default=True)

    def __init__(self, activity_id=None, name=""):
        self.activity_id = activity_id
        self.name = name
        ## The defaults are applied only on INSERT/flush
        ## But we need to use them earlier, when we are creating new entries, before they are inserted
        ## So we have to init them manually
        self.active = self.__table__.c.active.default.arg
        

class ActivityInfo(Base):
    __tablename__ = 'activitydetail'

    record_id = Column(Integer, ForeignKey("entries.record_id"), primary_key=True)
    activity_id = Column(Integer, ForeignKey("activity.activity_id"), primary_key=True)

    hours = Column(Integer)
    minutes = Column(Integer)
    
    intensity = Column(Integer(unsigned=True))

    record = relationship("Record", backref=backref('activity_info'))
    activity = relationship("Activity")

    def __init__(self, record_id=None, activity_id=None, hours=None, minutes=None, intensity=None):
        self.record_id = record_id
        self.activity_id = activity_id
        self.hours = hours
        self.minutes = minutes
        self.intensity = intensity


class SleepInfo(Base):
    __tablename__ = 'sleep'

    record_id = Column(Integer, ForeignKey("entries.record_id"), primary_key=True)

    hours = Column(Integer, nullable=False)
    minutes = Column(Integer, nullable=False)
    quality = Column(Integer(unsigned=True))
    light_out_time = Column(Time)
    asleep_time = Column(Time)
    awake_time = Column(Time)

    record = relationship("Record", backref=backref('sleep_info', uselist=False))

    def __init__(self, record_id, hours=0, minutes=0, quality=None, light_out_time=None, asleep_time=None, awake_time=None):
        self.record_id = record_id
        self.hours = hours
        self.minutes = minutes
        self.quality = quality
        self.light_out_time = light_out_time
        self.awake_time = awake_time
        self.asleep_time = asleep_time
