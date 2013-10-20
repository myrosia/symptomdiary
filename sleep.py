'''
Created on 20 Nov 2013

@author: myrosia
'''
from diary_content import EditBlock, InfoBlock
from main import SymptomDiaryApp
from diary_widgets import ErrorPopup
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
import sys
from data import SleepInfo

class SleepInfoBlock(InfoBlock):
    sleep_summary = StringProperty()
 
    def __init__(self, **kwargs):
        self.update_info()                                   
        super(SleepInfoBlock, self).__init__(**kwargs)

    def create_edit_block(self):
        return SleepEditBlock(self.record)

    def format_time_value(self, time_val):
        if (time_val is None):
            return "unspecified"
        else:
            return time_val.strftime("%H:%M")
    
    def update_info(self):
        if (self.record is not None) and (self.record.sleep_info is not None):
            short_descr = "{!s} hours {!s} minutes".format(self.record.sleep_info.hours, self.record.sleep_info.minutes)
            if ((self.record.sleep_info.light_out_time is not None)
                 or (self.record.sleep_info.asleep_time is not None)
                 or (self.record.sleep_info.awake_time is not None)):
                short_descr += " (Lights out: {!s}; Asleep: {!s}; Awake: {!s})".format(
                                    self.format_time_value(self.record.sleep_info.light_out_time), 
                                    self.format_time_value(self.record.sleep_info.asleep_time), 
                                    self.format_time_value(self.record.sleep_info.awake_time)
                                )

            if (self.record.sleep_info.quality is not None):
                short_descr += ", quality: {!s}".format(self.record.sleep_info.quality)
            else:
                short_descr += ", quality not recorded"
            self.sleep_summary = short_descr
        else:
            self.sleep_summary = "Not recorded"
                   

class SleepEditBlock(EditBlock):

    def fill_in(self):
        '''Fill in the fields from the current record'''
                
        if (self.record.sleep_info is not None):
            self.hours_input_field.value = self.record.sleep_info.hours
            self.minutes_input_field.value = self.record.sleep_info.minutes
            self.quality_slider.value = self.record.sleep_info.quality
            self.lights_out_input_field.value = self.record.sleep_info.light_out_time
            self.asleep_input_field.value = self.record.sleep_info.asleep_time
            self.awake_input_field.value = self.record.sleep_info.awake_time
            
    def validate(self):
        if (self.hours_input_field.value is None):
            ep = ErrorPopup("Hours must be a number, not empty")
            ep.open()
            return False
        elif (self.minutes_input_field.value is None):
            ep = ErrorPopup("Minutes must be a number, not empty")
            ep.open()
            return False
        return True
            

    def update_record(self):
        '''Update the record with fields from the block'''
        
        print >> sys.stderr, "Updating record in sleep edit block"
        
        if (self.record.sleep_info is None):
            ### we need t create a new pain info
            app = SymptomDiaryApp.get_running_app()  
            session = app.getDBSession()
            sinfo = SleepInfo(record_id=self.record.record_id)
            session.add(sinfo)
            self.record.sleep_info = sinfo
            

        self.record.sleep_info.hours = self.hours_input_field.value
        self.record.sleep_info.minutes = self.minutes_input_field.value
        self.record.sleep_info.quality = self.quality_slider.value
        self.record.sleep_info.light_out_time = self.lights_out_input_field.value
        self.record.sleep_info.asleep_time = self.asleep_input_field.value
        self.record.sleep_info.awake_time = self.awake_input_field.value
