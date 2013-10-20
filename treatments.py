'''
Created on 20 Nov 2013

@author: myrosia
'''
from diary_content import ListManagePopup, EditBlock, ListSummaryInfoBlock,\
    ListManagerEditBlock
from main import SymptomDiaryApp
from diary_widgets import ErrorPopup, EditPanelLabel
from sqlalchemy.orm.exc import NoResultFound
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import operator
import sys
from kivy.uix.label import Label
from data import Treatment, TreatmentInfo
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout



class TreatmentListManagePopup(ListManagePopup): 

    def __init__(self, record, **kwargs):
        self.item_class = Treatment
        super(TreatmentListManagePopup, self).__init__(record, **kwargs)
    
    def describe_list_item(self, obj):
        text = "{}".format(obj.name)
        if (obj.provider is not None):
            text += ", from {}".format(obj.provider)
        if (obj.frequency is not None):
            text += ", {}".format(obj.frequency)   
        return text

    def create_edit_panel(self, record):
        return TreatmentEditPanel(record)

    def create_new_record(self):
        return Treatment(name = "")



class TreatmentEditPanel(GridLayout):
    record = None
    
    def __init__(self, treatment_info, **kwargs):
        self.record = treatment_info
        super(TreatmentEditPanel, self).__init__(**kwargs)
        self._update_fields_from_record()

    def fill_in(self):
        self._update_fields_from_record()
    
    def validate(self):

        name = self.name_input.value
        provider = self.provider_input.value
        
        if (name is None) or (not ListManagerEditBlock.is_alnum_phrase(name) ):
            error_popup = ErrorPopup(text="Name must be non-empty and contain only alphanumeric characters")
            error_popup.open()
            return False
                
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        
        treatment_query = session.query(Treatment).filter(Treatment.name == name)\
                                .filter(Treatment.provider == provider) 
        try:
            result = treatment_query.one()
        except NoResultFound:
            result = None
            
        if (result is not None) and (result.treatment_id != self.record.treatment_id):
            # We found a similar record (same treatment and dosage ) but it has a different ID
            # We should not allow such duplicates            
            error_popup = ErrorPopup(text = "Treatment %s from provider %s is already defined in the DB. You must edit that record instead" 
                                                % (name, provider) )
            error_popup.open()
            return False
        
        return True

    def _update_fields_from_record(self):
        self.name_input.value = self.record.name
        self.provider_input.value = self.record.provider
        self.frequency_input.value = self.record.frequency

    def _update_record_from_fields(self):
        self.record.name = self.name_input.value
        self.record.provider = self.provider_input.value
        self.record.frequency = self.frequency_input.value
        


class TreatmentInfoBlock(ListSummaryInfoBlock):
 
    def create_edit_block(self):
        return TreatmentDetailEditBlock(self.record)

    def create_list_manage_popup(self):
        return TreatmentListManagePopup(self.record, title="Manage treatments");

    def summarize_record(self):
        summary = None

        if (self.record is not None) and (self.record.treatment_info is not None):
            for si in self.record.treatment_info:
                if (si.times_per_day) or (si.hours) or (si.minutes):
                    short_descr = "{}".format(si.treatment.name)
                    if (si.treatment.provider is not None):
                        short_descr += " from {}".format(si.treatment.provider)                         
                    if (si.times_per_day):
                        short_descr += " %d times" % (si.times_per_day)
                    if (si.hours) or (si.minutes):
                        short_descr += " for "
                        if (si.hours):
                            short_descr += " %d hours" % si.hours
                        if (si.minutes):
                            short_descr += " %d minutes" % si.minutes
                else:
                    short_descr = "%s: not taken" % (si.treatment.name)
                    
                if summary is None:
                    summary = short_descr
                else:
                    summary += ", " + short_descr

        return summary


class TreatmentDetailEditBlock(EditBlock):
    treatments_block = ObjectProperty()
    ti_panels = []
    

    def fill_in(self):
        '''Fill in the fields from the current record'''
        self._create_treatment_info()
        prev_ti_panel = None
                
        for ti in self.record.treatment_info:
            self.treatments_block.add_widget(Label(text=ti.treatment.name, size_hint_x=0.2))
            ti_panel = SingleTreatmentDetailEditPanel(ti)
            if (prev_ti_panel is not None):
                prev_ti_panel.last_editable_field.next = ti_panel.first_editable_field
            prev_ti_panel = ti_panel
            self.ti_panels.append(ti_panel)
            self.treatments_block.add_widget(ti_panel)
            
        if (self.ti_panels):
            self.ti_panels[0].first_editable_field.focus = True

    def update_record(self):
        '''Update the record with fields from the block'''
        for ti_panel in self.ti_panels:
            # this will actually update the record
            ti_panel.update_record()
                    
    def _create_treatment_info(self):
        if self.record.treatment_info is not None:
            known_treatment_ids = set(map(operator.attrgetter('treatment_id'), self.record.treatment_info))
        else:
            known_treatment_ids = set()
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        all_treatments_found = session.query(Treatment).filter(Treatment.active == True).all()
        not_known_treatments = filter(lambda med: med.treatment_id not in known_treatment_ids, all_treatments_found )
        
        for treatment in not_known_treatments:
            mi = TreatmentInfo(record_id=self.record.record_id, 
                               treatment_id=treatment.treatment_id, 
                               times_per_day = None,
                               hours = None,
                               minutes = None
                               )
            session.add(mi)
        session.flush()
        session.refresh(self.record)
    

class SingleTreatmentEditLabel(EditPanelLabel):
    pass

class SingleTreatmentDetailEditPanel(BoxLayout):
    treatment_detail = None
    
    def __init__(self, td_record, **kwargs):
        self.treatment_detail = td_record
        super(SingleTreatmentDetailEditPanel, self).__init__(**kwargs)
        self.fill_in()

    def fill_in(self):
        self.times_per_day_input.value = self.treatment_detail.times_per_day
        self.hours_input.value = self.treatment_detail.hours
        self.minutes_input.value = self.treatment_detail.minutes

    def update_record(self):
        '''Update the record with fields from the block'''
        self.treatment_detail.times_per_day = self.times_per_day_input.value
        self.treatment_detail.hours = self.hours_input.value 
        self.treatment_detail.minutes = self.minutes_input.value

