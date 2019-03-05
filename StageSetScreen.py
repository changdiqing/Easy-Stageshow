from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.popup import Popup
import imghdr
import shutil
import os
from FileChooserDialog import LoadDialog
from RV import *

class StageSetScreen(Screen, RVDelegate):

    fileSelected = BooleanProperty(False)
    stageShow = ObjectProperty(None)
    filechooserRoot = StringProperty('')
    touchDown = False

    def __init__(self, **kwargs):
        super(StageSetScreen, self).__init__(**kwargs)

    def on_touch_move(self, touch):
        self.ic.center = touch.pos
        return

    def saveFileToRV(self, selection):
        if len(selection)>0 and self.touchDown:
            filePath = selection[0]
            if self.isImageFile(filePath):
                self.fileSelected = True
                self.rv.clickedFile = filePath
            else:
                print('Not a valid image file!')

        self.filechooser.selection = []

    def isImageFile(self, filePath):
        return imghdr.what(filePath)

    def switchToStageShow(self):
        self.stageShow.rv.data = self.rv.data
        self.stageShow.bindKeyboard(True)
        self.manager.transition.direction = 'right'
        self.manager.transition.mode = 'pop'
        self.manager.current = 'stageshow'

    def setFileSelectedTo(self,bool):
        self.fileSelected = bool

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self):
        self._popup.dismiss()

    def load(self, selections):
        for el in selections:
            if self.isImageFile(el):
                self.copy(el,self.filechooserRoot)
                self.filechooser._update_files()
            else:
                print('File not copied because it it not a image file!')
        #with open(os.path.join(path, filename[0])) as stream:
        #    self.text_input.text = stream.read()

        self.dismiss_popup()

    def copy(self, source, target):
        #source = '/Users/diqingchang/PycharmProjects/StageShowImageSound/img/mini.jpg'
        #target = '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm'

        #assert not os.path.isabs(source)
        #print(os.path.dirname(source))
        #target = os.path.join(target, os.path.dirname(source))

        # create the folders if not already exists
        if not os.path.exists(target):
            os.makedirs(target)

        # adding exception handling
        try:
            shutil.copy(source, target)
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", os.sys.exc_info())

    # Filechooser Methods
    def on_filechoosertouch_up(self, touch):
        self.touchDown = False
        self.fileSelected = False
        self.ic.pos = [-50,-50]

    def on_filechoosertouch_down(self, pos):
        self.touchDown = True
        self.ic.pos = pos
