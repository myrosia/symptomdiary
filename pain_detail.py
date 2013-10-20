'''
Created on 20 Nov 2013

@author: myrosia
'''
from diary_content import ListManagePopup, EditBlock, ListSummaryInfoBlock, ListManagerEditBlock
from main import SymptomDiaryApp
from data import PainSite, PainSiteInfo
from diary_widgets import ErrorPopup, SliderWithValue
from sqlalchemy.sql.expression import func
from sqlalchemy.orm.exc import NoResultFound
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import operator
import sys
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

class PainSiteListManagePopup(ListManagePopup): 

    def __init__(self, record, **kwargs):
        self.item_class = PainSite
        super(PainSiteListManagePopup, self).__init__(record, **kwargs)

    def describe_list_item(self, obj):
        return obj.location
                                
    def create_edit_panel(self, record):
        return PainSiteEditPanel(record)
    
    def create_new_record(self):
        return PainSite(None, location = "")



class PainSiteEditPanel(GridLayout):
    record = None
    
    def __init__(self, record, **kwargs):
        self.record = record
        super(PainSiteEditPanel, self).__init__(**kwargs)
        self._update_fields_from_record()
    
    def fill_in(self):
        self._update_fields_from_record()
    
    def validate(self):
        location = self.name_input.value
        
        if (location is None) or (not ListManagerEditBlock.is_alnum_phrase(location)):
            error_popup = ErrorPopup(text="Name must be non-empty and contain only alphanumeric characters. Entered: %s" % location)
            error_popup.open()
            return False
                
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        
        pain_site_query = session.query(PainSite).filter(func.lower(PainSite.location) == location)

        try:
            result = pain_site_query.one()
        except NoResultFound:
            result = None
            
        if (result is not None) and (result.pain_site_id != self.record.pain_site_id):
            # We found a similar record (same name ) but it has a different ID
            # We should not allow such duplicates            
            error_popup = ErrorPopup(text = "Pain site %s is already defined in the DB. You must edit that record instead" 
                                                % (location) )
            error_popup.open()
            return False
        
        return True

    def _update_fields_from_record(self):
        self.name_input.value = self.record.location

    def _update_record_from_fields(self):
        self.record.location = self.name_input.value



class PainDetailInfoBlock(ListSummaryInfoBlock):
 
    def create_edit_block(self):
        return PainDetailEditBlock(self.record)

    def create_list_manage_popup(self):
        return PainSiteListManagePopup(self.record, title="Manage Medications");

    def summarize_record(self):
        summary = None
        if (self.record is not None) and (self.record.pain_site_info is not None):
            for psi in self.record.pain_site_info:
                short_descr = "%s: %s" % (psi.site.location, psi.painlevel)
                if summary is None:
                    summary = short_descr
                else:
                    summary += ", " + short_descr        
        return summary


class PainDetailEditBlock(EditBlock):
    pain_sites_block = ObjectProperty()
    sliders = []

    def fill_in(self):
        '''Fill in the fields from the current record'''
        self._create_symptom_info()
                
        for pi in self.record.pain_site_info:
            self.pain_sites_block.add_widget(Label(text=pi.site.location))
            slider = SliderWithValue(value=pi.painlevel)
            self.sliders.append((slider, pi))
            self.pain_sites_block.add_widget(slider)

    def update_record(self):
        '''Update the record with fields from the block'''
        for (slider,pi) in self.sliders:
            pi.painlevel = slider.value
        
    def _create_symptom_info(self):
        if self.record.pain_site_info is not None:
            known_sites = set(map(operator.attrgetter('site_id'), self.record.pain_site_info))
        else:
            known_sites = set()
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        all_sites_found = session.query(PainSite).filter(PainSite.active == True).all()
        found_ids = set(map(operator.attrgetter('site_id'), all_sites_found))
        for site_id in (found_ids - known_sites):
            psi = PainSiteInfo(record_id=self.record.record_id, site_id=site_id)
            session.add(psi)
        session.flush()
        session.refresh(self.record)
    
