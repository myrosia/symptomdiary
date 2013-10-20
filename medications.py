'''
Created on 20 Nov 2013

@author: myrosia
'''
from diary_content import ListManagePopup, EditBlock, ListSummaryInfoBlock, ListManagerEditBlock
from main import SymptomDiaryApp
from diary_widgets import ErrorPopup, NumericInputField
from sqlalchemy.orm.exc import NoResultFound
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import operator
import sys
from kivy.uix.label import Label
from data import Medication, MedicationInfo
from kivy.uix.gridlayout import GridLayout

class MedicationListManagePopup(ListManagePopup): 

    def __init__(self, record, **kwargs):
        self.item_class = Medication
        super(MedicationListManagePopup, self).__init__(record, **kwargs)

    def describe_list_item(self, obj):
        return "{} {:g}{}, {} x {}".format(obj.name, obj.dosage, obj.unit, obj.quantity, obj.frequency)   
                    
    def create_edit_panel(self, record):
        return MedicationEditPanel(record)

    def create_new_record(self):
        return Medication("")


class MedicationEditPanel(GridLayout):
    record = None
    
    def __init__(self, medication_info, **kwargs):
        self.record = medication_info
        super(MedicationEditPanel, self).__init__(**kwargs)
        self._update_fields_from_record()

    def fill_in(self):
        self._update_fields_from_record()
            
    def validate(self):
        name = self.name_input.value
        unit = self.unit_input.value
        dosage = self.dosage_input.value
        
        if (name is None) or (not ListManagerEditBlock.is_alnum_phrase(name) ):
            error_popup = ErrorPopup(text="Name must be non-empty and contain only alphanumeric characters")
            error_popup.open()
            return False
        
        if (unit is None):
            error_popup = ErrorPopup(text="Unit must be non-empty")
            error_popup.open()
            return False
        
        if (dosage is None):
            error_popup = ErrorPopup(text="Dosage must be a number")
            error_popup.open()
            return False
        
        if (self.quantity_input.value is None):
            error_popup = ErrorPopup(text="Quantity must be a number")
            error_popup.open()
            return False


        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        
        medication_query = session.query(Medication).filter(Medication.name == name)\
                                .filter(Medication.unit == unit) \
                                .filter(Medication.dosage == dosage)
        try:
            result = medication_query.one()
        except NoResultFound:
            result = None
            
        if (result is not None) and (result.medication_id != self.record.medication_id):
            # We found a similar record (same medication and dosage ) but it has a different ID
            # We should not allow such duplicates            
            error_popup = ErrorPopup(text = "Medication %s with dosage %s %s is already defined in the DB. You must edit that record instead" 
                                                % (name, dosage, unit) )
            error_popup.open()
            return False
        
        return True

    def _update_fields_from_record(self):
        self.name_input.value = self.record.name
        self.unit_input.value = self.record.unit
        self.dosage_input.value = self.record.dosage
        self.quantity_input.value = self.record.quantity
        self.frequency_input.value = self.record.frequency

    def _update_record_from_fields(self):
        self.record.name = self.name_input.value
        self.record.unit = self.unit_input.value
        self.record.dosage = self.dosage_input.value
        self.record.quantity = self.quantity_input.value
        self.record.frequency = self.frequency_input.value
        

class MedicationInfoBlock(ListSummaryInfoBlock):
 
    def create_edit_block(self):
        return MedicationDetailEditBlock(self.record)

    def create_list_manage_popup(self):
        return MedicationListManagePopup(self.record, title="Manage Medications");

    def summarize_record(self):
        summary = None
        if (self.record is not None) and (self.record.medication_info is not None):
            for si in self.record.medication_info:
                if (si.quantity is not None):
                    short_descr = "{} {:g}{}: {:d} time(s)".format(si.medication.name, 
                                                                   si.medication.dosage,
                                                                   si.medication.unit,
                                                                   si.quantity)
                else:
                    short_descr = "{}: not taken".format(si.medication.name)
                    
                if summary is None:
                    summary = short_descr
                else:
                    summary += ", " + short_descr
        return summary
                   

class MedicationDetailEditBlock(EditBlock):
    medications_block = ObjectProperty()
    inputs = []

    def fill_in(self):
        '''Fill in the fields from the current record'''
        self._create_medication_info()
        prev_mi = None
                
        for mi in self.record.medication_info:
            self.medications_block.add_widget(
                    Label(text = "{} {:g}{}".format(mi.medication.name, mi.medication.dosage, mi.medication.unit))
                )
            mi_field = NumericInputField(value=mi.quantity);
            if (prev_mi is not None):
                prev_mi.next = mi_field
            prev_mi = mi_field
            self.inputs.append((mi_field, mi))
            self.medications_block.add_widget(mi_field)
            
        if (self.inputs):
            self.inputs[0][0].focus = True

    def update_record(self):
        '''Update the record with fields from the block'''
        for (ni_field,mi) in self.inputs:
            mi.quantity = ni_field.value
        
    def _create_medication_info(self):
        if self.record.medication_info is not None:
            known_medication_ids = set(map(operator.attrgetter('medication_id'), self.record.medication_info))
        else:
            known_medication_ids = set()
        app = SymptomDiaryApp.get_running_app()  
        session = app.getDBSession()
        all_medications_found = session.query(Medication).filter(Medication.active == True).all()
        not_known_medications = filter(lambda med: med.medication_id not in known_medication_ids, all_medications_found )
        
        for medication in not_known_medications:
            mi = MedicationInfo(record_id=self.record.record_id, 
                                medication_id=medication.medication_id, 
                                quantity=medication.quantity)
            session.add(mi)
        session.flush()
        session.refresh(self.record)
    
