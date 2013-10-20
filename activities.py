'''
Created on 20 Nov 2013

@author: myrosia
'''
from diary_content import ListManagePopup, EditBlock, ListSummaryInfoBlock, ListManagerEditBlock
from main import SymptomDiaryApp
from diary_widgets import ErrorPopup, EditPanelLabel
from sqlalchemy.orm.exc import NoResultFound
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import operator
import sys
from kivy.uix.label import Label
from data import Activity, ActivityInfo
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

class ActivityListManagePopup(ListManagePopup): 

    def __init__(self, record, **kwargs):
        self.item_class = Activity
        super(ActivityListManagePopup, self).__init__(record, **kwargs)

    def describe_list_item(self, obj):
        return "{}".format(obj.name)

    def create_edit_panel(self, record):
        return ActivityEditPanel(record)

    def create_new_record(self):
        return Activity(name = "")


class ActivityEditPanel(GridLayout):
    record = None
    
    def __init__(self, activity_info, **kwargs):
        self.record = activity_info
        super(ActivityEditPanel, self).__init__(**kwargs)
        self._update_fields_from_record()

    def fill_in(self):
        self._update_fields_from_record()
    
    def validate(self):
        name = self.name_input.value
        
        if (name is None) or (not ListManagerEditBlock.is_alnum_phrase(name) ):
            error_popup = ErrorPopup(text="Name must be non-empty and contain only alphanumeric characters")
            error_popup.open()
            return False
                
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        
        activity_query = session.query(Activity).filter(Activity.name == name)

        try:
            result = activity_query.one()
        except NoResultFound:
            result = None
            
        if (result is not None) and (result.activity_id != self.record.activity_id):
            # We found a similar record (same name ) but it has a different ID
            # We should not allow such duplicates            
            error_popup = ErrorPopup(text = "Activity %s is already defined in the DB. You must edit that record instead" 
                                                % (name) )
            error_popup.open()
            return False
        
        return True

    def _update_fields_from_record(self):
        self.name_input.value = self.record.name

    def _update_record_from_fields(self):
        self.record.name = self.name_input.value




class ActivityInfoBlock(ListSummaryInfoBlock):
 
    def create_edit_block(self):
        return ActivityDetailEditBlock(self.record)

    def create_list_manage_popup(self):
        return ActivityListManagePopup(self.record, title="Manage Activities")

    def summarize_record(self):
        summary = None
        if (self.record is not None) and (self.record.activity_info is not None):
            for ai in self.record.activity_info:
                if (ai.hours) or (ai.minutes):
                    short_descr = "{} for {:d} hour(s) {:d} minute(s)".format(ai.activity.name, ai.hours, ai.minutes)
                    if (ai.intensity):
                        short_descr += ", intensity: {:n}".format(ai.intensity)
                else:
                    short_descr = "{}: not taken" .format(ai.activity.name)
                    
                if summary is None:
                    summary = short_descr
                else:
                    summary += ", " + short_descr
        return summary
                   

class ActivityDetailEditBlock(EditBlock):
    activities_block = ObjectProperty()
    ai_panels = []
    

    def fill_in(self):
        '''Fill in the fields from the current record'''
        self._create_activity_info()
        prev_ai_panel = None
                
        for ai in self.record.activity_info:
            self.activities_block.add_widget(Label(text=ai.activity.name, size_hint_x=0.2))
            ai_panel = SingleActivityDetailEditPanel(ai)
            if (prev_ai_panel is not None):
                prev_ai_panel.last_editable_field.next = ai_panel.first_editable_field
            prev_ai_panel = ai_panel
            self.ai_panels.append(ai_panel)
            self.activities_block.add_widget(ai_panel)
            
        if (self.ai_panels):
            self.ai_panels[0].first_editable_field.focus = True

    def update_record(self):
        '''Update the record with fields from the block'''
        if (self.validate()):
            for ai_panel in self.ai_panels:
                # this will actually update the record
                ai_panel.update_record()
                    
    def _create_activity_info(self):
        if self.record.activity_info is not None:
            known_activity_ids = set(map(operator.attrgetter('activity_id'), self.record.activity_info))
        else:
            known_activity_ids = set()
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        all_activities_found = session.query(Activity).filter(Activity.active == True).all()
        not_known_activities = filter(lambda ac: ac.activity_id not in known_activity_ids, all_activities_found )
        
        for activity in not_known_activities:
            ai = ActivityInfo(record_id=self.record.record_id, 
                               activity_id=activity.activity_id, 
                               hours = 0,
                               minutes = 0
                               )
            session.add(ai)
        session.flush()
        session.refresh(self.record)
    
    def validate(self):
        for ai_panel in self.ai_panels:
            if (not ai_panel.validate()):
                return False
        return True
    
            

class SingleActivityEditLabel(EditPanelLabel):
    pass

class SingleActivityDetailEditPanel(BoxLayout):
    activity_detail = None
    
    def __init__(self, ad_record, **kwargs):
        self.activity_detail = ad_record
        super(SingleActivityDetailEditPanel, self).__init__(**kwargs)
        self.fill_in()

    def fill_in(self):
        self.hours_input.value = self.activity_detail.hours
        self.minutes_input.value = self.activity_detail.minutes
        self.intensity_slider.value = self.activity_detail.intensity

    def update_record(self):
        '''Update the record with fields from the block'''
        self.activity_detail.hours = self.hours_input.value 
        self.activity_detail.minutes = self.minutes_input.value
        self.activity_detail.intensity = self.intensity_slider.value
    
    def validate(self):
        if (self.hours_input.value is None):
            ep = ErrorPopup("Hours must be a number, not empty")
            ep.open()
            return False
        elif (self.minutes_input.value is None):
            ep = ErrorPopup("Minutes must be a number, not empty")
            ep.open()
            return False
        return True