'''
Created on 11 Jun 2014

@author: myrosia
@note: initially based on http://stackoverflow.com/questions/13714074/kivy-date-picker-widget

'''

import kivy

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from datetime import date, timedelta

from kivy.app import App
import datetime
from calendar import monthrange
import sys
from kivy.properties import ObjectProperty, StringProperty;
import calendar

from diary_widgets import ColorLabel
from kivy.uix.popup import Popup

class DatePickerButton(Button):
    pass


class DatePicker(BoxLayout):
    '''
        A date picker linked to the main App.
        The App *must* call "populate" after the initialization is finished
        populate cannot be called from the 
    '''
    background_defined = [1, 0, 0, 0.5]
    background_header = [0, 0.5, 0.5, 0.5]

    background_undefined = [0, 0, 1, 0.5]

    border_default = (2,2,2,2)
    border_today = (20,20,20,20)
    
    ## This is bound to the text of the header label in kv, so if we change it, the label gets set
    current_month_text = StringProperty()

    ## This is the start of the current month, changes as we browse
    month_start = None
    
    body = ObjectProperty()


    
    def __init__(self, **kwargs):
        self.month_start = date.today().replace(day=1) 
        self.set_header()
        super(DatePicker, self).__init__(**kwargs)         
        ### We cannot init the body here, it's not ready
        ### It can be inited dynamically using the on_body method
    
    
    def on_body(self, *args):
        '''
        Initialization of the body. Called once, when the body is set.
        '''
        if (self.body is not None):
            self.populate_body()
        
    def populate(self):
        self.set_header()
        self.populate_body()

    

    def populate_body(self):
        self.body.clear_widgets()    
        application = App.get_running_app()
        
        first_weekday, numdays = monthrange(self.month_start.year, self.month_start.month) 
        today = date.today()

        # first we will put in a header with appropriately initialized weekdays
        for dayname in calendar.day_abbr:
            self.body.add_widget(ColorLabel(text=dayname,
                                       background_color=self.background_header,
                                       size_hint = (0.5, 0.99)
                                       ))
            
        
        # filler fields from previous month, empty
        for filler in range(first_weekday):
            self.body.add_widget(Label(text=""))


        for day in range(1, numdays + 1):
            day_button = DatePickerButton(text = str(day))
            button_date = date(day=day, 
                               month=self.month_start.month,
                               year=self.month_start.year)
            day_button.bind(on_press=lambda instance, bd=button_date: 
                                self.date_clicked(bd)
                                )
                                           
            if (today == button_date):
                day_button.border = self.border_today
            else:
                day_button.border = self.border_default
                
            if (application.find_entry_by_date(button_date) is not None):
                day_button.background_color = self.background_defined
            else:
                day_button.background_color = self.background_undefined
                                
            self.body.add_widget(day_button)


    def date_clicked(self, date):
        ''' Main handler -- what to do once the date is selected '''
        print >> sys.stderr, "Date clicked %s" % date
        application = App.get_running_app()
        entry = application.find_entry_by_date(date)
        if (entry is None):
            self.create_entry_dialog(application, date)
        else:
            application.display_entry_by_date(date)
        

    def create_entry_dialog(self, application, date):
        popup = CreateEntryPopup(application, date)
        popup.open()


    def makeHeaderText(self, date):
        return date.strftime('%B %Y')
        
    def set_header(self):
        self.current_month_text = self.makeHeaderText(self.month_start)
        
    def move_next_month(self):
        self.month_start += timedelta(days = monthrange(self.month_start.year, self.month_start.month)[1])
        self.populate()

    def move_previous_month(self):
        self.month_start += timedelta(days = -1)
        ## we are now at the end of previous month -- move to start
        self.month_start = self.month_start.replace(day=1)
        self.populate()


class CreateEntryPopup(Popup):
    entry_date = ObjectProperty()
    entry_form = ObjectProperty()
    application = None

    def __init__(self, application, date, **kwargs):
        self.entry_date = date;
        self.application = application
        super(CreateEntryPopup, self).__init__(**kwargs)         
    
    def create_entry(self):
        self.application.create_entry_by_date(self.entry_date, 
                                              datetime.datetime.now().time(),
                                              self.entry_form.note_input_box.text)
        self.application.display_entry_by_date(self.entry_date)
        self.dismiss()


class CreateEntryForm(BoxLayout):
    note_input_box = ObjectProperty()
    entry_date = ObjectProperty()    
