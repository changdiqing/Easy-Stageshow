from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty
import os

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    path = StringProperty('./')

class LoadTarDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    path = StringProperty('./')

class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    path = StringProperty('./')

    def getFilechooserSelectionName(self):

        path = self.filechooser.selection and self.filechooser.selection[0] or ''
        return os.path.basename(path)