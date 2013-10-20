'''
Created on 20 Nov 2013

@author: myrosia
'''
from diary_content import ListManagePopup, EditBlock, ListSummaryInfoBlock,\
    ListManagerEditBlock
from main import SymptomDiaryApp
from diary_widgets import ErrorPopup, SliderWithValue
from sqlalchemy.sql.expression import func
from sqlalchemy.orm.exc import NoResultFound
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import operator
import sys
from kivy.uix.label import Label
from data import Symptom, SymptomInfo
from kivy.uix.gridlayout import GridLayout



class SymptomListManagePopup(ListManagePopup): 

    def __init__(self, record, **kwargs):
        self.item_class = Symptom
        super(SymptomListManagePopup, self).__init__(record, **kwargs)

    def describe_list_item(self, obj):
        return obj.name
                
    def create_edit_panel(self, record):
        return SymptomEditPanel(record)

    def create_new_record(self):
        return Symptom(None, name = "")



class SymptomEditPanel(GridLayout):
    record = None
    
    def __init__(self, record, **kwargs):
        self.record = record
        super(SymptomEditPanel, self).__init__(**kwargs)
        self._update_fields_from_record()
    
    def fill_in(self):
        self._update_fields_from_record()
    
    def validate(self):
        name = self.name_input.value
        
        if (name is None) or (not ListManagerEditBlock.is_alnum_phrase(name)):
            error_popup = ErrorPopup(text="Symptom name must be non-empty and contain only alphanumeric characters. Entered: %s" % name)
            error_popup.open()
            return False
                
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        
        symptom_query = session.query(Symptom).filter(func.lower(Symptom.name) == name)

        try:
            result = symptom_query.one()
        except NoResultFound:
            result = None
            
        if (result is not None) and (result.symptom_id != self.record.symptom_id):
            # We found a similar record (same name ) but it has a different ID
            # We should not allow such duplicates            
            error_popup = ErrorPopup(text = "Symptom %s is already defined in the DB. You must edit that record instead" 
                                                % (name) )
            error_popup.open()
            return False
        
        return True

    def _update_fields_from_record(self):
        self.name_input.value = self.record.name

    def _update_record_from_fields(self):
        self.record.name = self.name_input.value




class SymptomInfoBlock(ListSummaryInfoBlock):
         
    def create_edit_block(self):
        return SymptomDetailEditBlock(self.record)

    def create_list_manage_popup(self):
        return SymptomListManagePopup(self.record, title="Manage Symptoms");

    def summarize_record(self):
        summary = None
        if (self.record is not None) and (self.record.symptom_info is not None):
            for si in self.record.symptom_info:
                short_descr = "%s: %s" % (si.symptom.name, si.intensity)
                if summary is None:
                    summary = short_descr
                else:
                    summary += ", " + short_descr
        return summary



class SymptomDetailEditBlock(EditBlock):
    symptoms_block = ObjectProperty()
    sliders = []

    def fill_in(self):
        '''Fill in the fields from the current record'''
        self._create_symptom_info()
                
        for si in self.record.symptom_info:
            self.symptoms_block.add_widget(Label(text=si.symptom.name))
            slider = SliderWithValue(value=si.intensity)
            self.sliders.append((slider, si))
            self.symptoms_block.add_widget(slider)

    def update_record(self):
        '''Update the record with fields from the block'''
        for (slider,si) in self.sliders:
            si.intensity = slider.value
        
    def _create_symptom_info(self):
        if self.record.symptom_info is not None:
            known_symptoms = set(map(operator.attrgetter('symptom_id'), self.record.symptom_info))
        else:
            known_symptoms = set()
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        all_symptoms_found = session.query(Symptom).filter(Symptom.active == True).all()
        found_ids = set(map(operator.attrgetter('symptom_id'), all_symptoms_found))
        for symptom_id in (found_ids - known_symptoms):
            si = SymptomInfo(record_id=self.record.record_id, symptom_id=symptom_id, intensity=None)
            session.add(si)
        session.flush()
        session.refresh(self.record)
