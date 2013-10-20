'''
Created on 18 Dec 2013

@author: myrosia
'''

from diary_content import EditBlock, InfoBlock
from kivy.properties import StringProperty




class NotesInfoBlock(InfoBlock):
    notes = StringProperty("Not recorded");
    
    def update_info(self):
        if (self.record.notes is not None):
            self.notes = self.record.notes
        else:
            self.notes = "Not recorded"
            
    def create_edit_block(self):
        return NotesEditBlock(self.record)
    

class NotesEditBlock(EditBlock):

    def __init__(self, record, **kwargs):
        super(NotesEditBlock, self).__init__(record, **kwargs)
        
    def fill_in(self):
        '''Fill in the fields from the current record'''
        if (self.record.notes is not None):
            self.notes_input.value = self.record.notes

    def update_record(self):
        '''Update the record with fields from the block'''
        self.record.notes = self.notes_input.value
        