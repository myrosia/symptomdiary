import sys
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.garden.tickmarker import TickMarker
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
import datetime
import re

class StandardButton(Button):
    pass


class SharedContentProperty(object):
    shared_content = BooleanProperty(True)
    def __init__(self, **kwargs):
        super(SharedContentProperty,self).__init__()
        sc = kwargs.get('shared_content', None)
        if (sc is not None):
            self.shared_content(sc)    

class SharedButton(StandardButton,SharedContentProperty):
    ''' A button used in info and edit blocks, 
    which can be placed in a customized position in the main block rather than in the block content
    '''
    pass


class SharedLabel(Label,SharedContentProperty):
    ''' A label used in info and edit blocks, 
    which can be placed in a customized position in the main block rather than in the block content
    '''
    pass

class NumericLabel(Label):
    value = NumericProperty(None, allownone=True)
    
    def on_value(self, instance, v):
        if (v is not None):
            self.text = "%.1f" % v
        else:
            self.text = "Not defined"


class TabbableTextInput(TextInput):
    next = ObjectProperty()
 
    def __init__(self, **kwargs):
        super(TabbableTextInput, self).__init__(**kwargs)
        self.bind(focus = self.select_all_on_focus)
 
    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 9:  # 9 is the keycode for
            if (self.next is not None): 
                self.next.focus = True
        else:
            super(TabbableTextInput, self)._keyboard_on_key_down(
                    window, keycode, text, modifiers)

    def select_all_on_focus(self, instance, value):
        if value:
            # If we achieve focus, select full text
            Clock.schedule_once(lambda dt: self.select_all())


class NumericInputField(TabbableTextInput):
    value = NumericProperty(None, allownone=True)
    warning_color = (1, 0, 0, 1)
    # A place to save text color
    # Updated after we init from the default foreground color
    normal_color = (1, 1, 1, 1)

    def __init__(self, value=None, **kwargs):
        self.value = value
        super(NumericInputField, self).__init__(**kwargs)
        self._update_text_from_value()
        self.normal_color = self.foreground_color
        self.bind(text = lambda i,v: self._update_value())
        self.bind(value = lambda i,v: self._update_text_from_value())
        
    def _update_value(self):
        if (self.text.isspace()):
            self.value = None
        else:            
            try:
                self.value = int(self.text)
                self.foreground_color = self.normal_color
            except ValueError:
                try:
                    self.value = float(self.text)
                    self.foreground_color = self.normal_color
                except ValueError:
                    self.foreground_color = self.warning_color
                
    def _update_text_from_value(self):
        if (self.value is None):
            self.text = "" 
        else:            
            self.text = "{:n}".format(self.value)


class TimeInputField(TabbableTextInput):
    value = ObjectProperty(None, allownone=True)
    warning_color = (1, 0, 0, 1)
    # A place to save text color
    # Updated after we init from the default foreground color
    normal_color = (1, 1, 1, 1)

    def __init__(self, value=None, **kwargs):
        self.value = value
        super(TimeInputField, self).__init__(**kwargs)
        self._update_text_from_value()
        self.normal_color = self.foreground_color
        self.bind(text = lambda i,v: self._update_value())
        self.bind(value = lambda i,v: self._update_text_from_value())
        
    def _update_value(self):
        if (self.text.isspace()):
            self.value = None
        elif (re.match('\s*\d?\d\s*:\s*\d\d\s*', self.text)):
            try:
                self.value = datetime.datetime.strptime(self.text, "%H:%M").time()
                self.foreground_color = self.normal_color
            except ValueError:
                    self.foreground_color = self.warning_color
        else:
            self.foreground_color = self.warning_color
                
    def _update_text_from_value(self):
        if (self.value is None):
            self.text = "" 
        else:            
            self.text = self.value.strftime("%H:%M")


class NormalizedTextField(TabbableTextInput):
    """ A text field that sets value to None if text is empty, and strips empty space around the text in the value    
    """
    value = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        self.bind(text = lambda i,v: self._update_value())
        self.bind(value = lambda i,v: self._update_text_from_value())
        super(NormalizedTextField, self).__init__(**kwargs)

    def normalize_text(self, tstr):
        # We normalize empty space to None
        if (not tstr.strip()):
            return None
        else:            
            return tstr.strip()
    
    def _update_value(self):
        self.value = self.normalize_text(self.text)
                
    def _update_text_from_value(self):
        if (self.value is not None):
            normalized_value = self.normalize_text(self.value)
            if (normalized_value != self.value):
                self.value = normalized_value;
        # we are guaranteed that the value is normalized at this point
        if (self.value is None) and (not self.text.isspace()):
            self.text = ""
        elif (self.normalize_text(self.text) != self.value):
            self.text = self.value



class DBLowercaseTextField(NormalizedTextField):
    """ Used to input DB fields -- normalizes everything to lower case, on top of the empty-to-none normalization
        that NormalizedTextField does
    """
    
    def normalize_text(self, tstr):
        # We normalize empty space to None
        if (not tstr.strip()):
            return None
        else:            
            return tstr.strip().lower()


class ErrorPopup(Popup):
    message_label = ObjectProperty()
    def __init__(self, text, **kvargs):
        super(ErrorPopup, self).__init__(**kvargs)
        self.message_label.text = text



class SimpleInputPopup(Popup):
    input_field = ObjectProperty()
    def __init__(self, text='', **kwargs):
        super(SimpleInputPopup, self).__init__(**kwargs)
        self.input_field.text = text
        self.register_event_type('on_input_ok')
        
    def on_input_ok(self):
        self.dismiss()



class TickSlider(Slider, TickMarker):
    pass


class SliderWithValue(BoxLayout):
    ''' A class that shows a slider and a label
        Also supports an "undefined" value, which is handled by having the "value" attribute be None
        while setting the actual slider value below minimum so that it is not visible
    '''
    value = NumericProperty(None, allownone=True)
    slider = ObjectProperty()

    
        
    def __init__(self, value=None, **kwargs):
        '''The initialization makes sure that value (which can default to None) does not pass down to kwargs.
           Instead, we set up slider value aver the main init is done'''
        self.value = value
        super(SliderWithValue, self).__init__(**kwargs)
                            
    def on_slider(self, instance, v):
        # If slider changed (typically during init), make sure we bind the value right
        if (self.slider is not None):
            # set the initial property binding
            # FIXME -- we want to be able to support a slider with undefined value
            self._update_slider_from_value()
            # now bind the value property
            self.slider.bind(value=self.update_value_from_slider)
            self.bind(value = self.update_slider_from_value)

    ### A bind handler that requires arguments - but we don't need them because we only have one instance and value possible
    def update_value_from_slider(self, instance, v):
        self._update_value_from_slider()

    def _update_value_from_slider(self):
        if self.slider is not None:
            if (self.slider.value >= self.slider.min):
                self.value = self.slider.value
            else:
                self.value = None

    ### A bind handler that requires arguments - but we don't need them because we only have one instance and value possible
    def update_slider_from_value(self, instance, value):        
        self._update_slider_from_value()
            
    def _update_slider_from_value(self):
        if (self.value is not None):            
            self.slider.value = self.value
        else:
            self.slider.value = self.slider.min - 1


class ObjLinkedSliderWithValue(SliderWithValue):
    linked_object = None
    def __init__(self, linked_object = None, **kwargs):
        self.linked_object = linked_object
        super(ObjLinkedSliderWithValue, self).__init__(self, **kwargs)


class EditPanelLabel(Label):
    pass

class ScrollableTextDisplay(BoxLayout):
    text = StringProperty()

class ColorLabel(Label):
    background_color = ObjectProperty()
