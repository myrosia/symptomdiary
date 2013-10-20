'''
Created on 18 Dec 2013

@author: myrosia
'''
from data import PainInfo
from main import SymptomDiaryApp
from diary_content import InfoBlock, EditBlock

from kivy.properties import StringProperty, NumericProperty


class PainInfoBlock(InfoBlock):
    pain_info = None
    average_pain = StringProperty("Not recorded");
    max_pain = StringProperty("Not recorded");
    
    def update_info(self):
        if (self.record.pain_info is not None):
            self.average_pain = "{}".format(self.record.pain_info.average_pain)
            self.max_pain = "{}".format(self.record.pain_info.max_pain)
        else:
            self.average_pain = "Not recorded"
            self.max_pain = "Not recorded"
            
    def create_edit_block(self):
        return PainEditBlock(self.record)
    

class PainEditBlock(EditBlock):
    average_pain = NumericProperty(None, allownone=True)
    max_pain = NumericProperty(None, allownone=True)

    def __init__(self, record, **kwargs):
        super(PainEditBlock, self).__init__(record, **kwargs)

    def fill_in(self):
        '''Fill in the fields from the current record'''
        if (self.record.pain_info is not None):
            self.average_pain = self.record.pain_info.average_pain
            self.max_pain = self.record.pain_info.max_pain

    def update_record(self):
        '''Update the record with fields from the block'''
        if (self.record.pain_info is None):
            ### we need t create a new pain info
            app = SymptomDiaryApp.get_running_app()  
            session = app.getDBSession()
            pinfo = PainInfo(record_id=self.record.record_id)
            session.add(pinfo)
            self.record.pain_info = pinfo

        self.record.pain_info.average_pain = self.average_pain
        self.record.pain_info.max_pain = self.max_pain
