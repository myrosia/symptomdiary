'''
Created on 11 Jun 2014

@author: myrosia
@note: initially based on http://stackoverflow.com/questions/13714074/kivy-date-picker-widget

'''

import kivy

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from datetime import date, timedelta

from functools import partial
from kivy.app import App
import datetime

class DatePicker(BoxLayout):
    
    background_defined = [1, 0, 0, 0.5]
    background_undefined = [0, 0, 1, 0.5]

    border_default = (2,2,2,2)
    border_today = (20,20,20,20)


    def __init__(self, **kwargs):
        super(DatePicker, self).__init__(**kwargs)
        self.date = date.today()
        self.orientation = "vertical"
        self.month_names = ('January',
                            'February', 
                            'March', 
                            'April', 
                            'May', 
                            'June', 
                            'July', 
                            'August', 
                            'September', 
                            'October',
                            'November',
                            'December')
        if kwargs.has_key("month_names"):
            self.month_names = kwargs['month_names']
        self.header = BoxLayout(orientation = 'horizontal', 
                                size_hint = (1, 0.2))
        self.body = GridLayout(cols = 7)
        self.add_widget(self.header)
        self.add_widget(self.body)

        self.populate_body()
        self.populate_header()

    def populate_header(self, *args, **kwargs):
        self.header.clear_widgets()
        previous_month = Button(text = "<")
        previous_month.bind(on_press=partial(self.move_previous_month))
        next_month = Button(text = ">", on_press = self.move_next_month)
        next_month.bind(on_press=partial(self.move_next_month))
        month_year_text = self.month_names[self.date.month -1] + ' ' + str(self.date.year)
        current_month = Label(text=month_year_text, size_hint = (2, 1))

        self.header.add_widget(previous_month)
        self.header.add_widget(current_month)
        self.header.add_widget(next_month)

    def populate_body(self, *args, **kwargs):
        self.body.clear_widgets()
        date_cursor = date(self.date.year, self.date.month, 1)
        
        application = App.get_running_app()
        
        for filler in range(date_cursor.isoweekday()-1):
            self.body.add_widget(Label(text=""))
        while date_cursor.month == self.date.month:
            date_label = Button(text = str(date_cursor.day))
            date_label.bind(on_press=lambda *args: 
                                self.day_clicked(*args, day=date_cursor.day)
                            )
                            
            if self.date.day == date_cursor.day:
                date_label.border = self.border_today
            else:
                date_label.border = self.border_default
                
            if (application.find_entry_by_date(date_cursor) is not None):
                date_label.background_color = self.background_defined
            else:
                date_label.background_color = self.background_undefined
                                
            self.body.add_widget(date_label)
            date_cursor += timedelta(days = 1)

    def day_clicked(self, *args, **kwargs):        
        self.date = date(self.date.year, self.date.month, kwargs['day'])
        self.date_clicked();
    
    def date_clicked(self):
        ''' Main handler -- what to do once the date is selected '''
        application = App.get_running_app()
        entry = application.find_entry_by_date(self.date)
        if (entry is None):
            application.create_entry_by_date(self.date, 
                            datetime.datetime.now().time(),
                            '')
        application.display_entry_by_date(self.date)
        

    def move_next_month(self, *args, **kwargs):
        if self.date.month == 12:
            self.date = date(self.date.year + 1, 1, self.date.day)
        else:
            self.date = date(self.date.year, self.date.month + 1, self.date.day)
        self.populate_header()
        self.populate_body()

    def move_previous_month(self, *args, **kwargs):
        if self.date.month == 1:
            self.date = date(self.date.year - 1, 12, self.date.day)
        else:
            self.date = date(self.date.year, self.date.month -1, self.date.day)
        self.populate_header()
        self.populate_body()

