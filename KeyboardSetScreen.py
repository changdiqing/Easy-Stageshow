from kivy.uix.screenmanager import Screen
from kivy.properties import BooleanProperty,ObjectProperty, StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
import sndhdr
import os
import shutil
from SoundDetail import SoundDetail_Delegate
from RVKeyboard import *

class SPDListDelegate():
    def spdlist_data_changed(self, data):
        pass

class SPDTextInputDelegate():
    def spdtextinput_on_focus(self, isFocused,text):
        pass
class LabelDelegate():
    def onSelectChange(self, isSelected = False):
        pass

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    path = StringProperty('')

class KeyboardSetScreen(Screen, LabelDelegate,RVKeyboardDelegate, SPDTextInputDelegate, SPDListDelegate):

    fileSelected = BooleanProperty(False)
    stageShow = ObjectProperty(None)
    filechooserRoot = StringProperty('')
    touchDown = False

    def __init__(self, **kwargs):
        super(KeyboardSetScreen, self).__init__(**kwargs)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')

        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass

        #self.soundPacks = self.createSoundlist(self.rvk.data)

    # MARK: Keyboard interaction methods
    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        #self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        #self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)

        thisKey = keycode[1]

        # set keyLabel.selected to false when there is key down
        self.kLabel.setSelected(False)
        self.kLabel.text = str(thisKey)
        if self.rvk.selectedIndex:
            index = self.rvk.selectedIndex
            self.rvk.editElementByIndex(index=index, key = thisKey, name = None, soundlist = None)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        return True

    def bindKeyboard(self, bool=True):
        if bool:
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        else:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)

    # MARK: Touch Events

    def on_touch_move(self, touch):
        self.ic.center = touch.pos
        return

    def touchUpEvent(self, pos):
        self.touchDown = False
        self.fileSelected = False
        self.ic.pos = [-50, -50]

    def touchDownEvent(self,pos):
        self.touchDown = True
        self.ic.center = pos

    # MARK: Private methods

    def saveFileToRVK(self, selection):
        if len(selection)>0 and self.touchDown:
            filePath = selection[0]
            try:
                self.validate_audio_file(filePath)
                self.fileSelected = True
                self.rvk.clickedFile = filePath
            except ValidationError as ve:
                print(ve)

        self.filechooser.selection = []

    def validate_audio_file(self, filePath):
        if not os.path.splitext(filePath)[1] in ['.ogg', '.wav']:
            raise ValidationError("Sorry, we only support .ogg and .wav, your audio file doesn't have a proper extension.")

    def isSoundFile(self, filePath):
        return sndhdr.what(filePath)

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
        '''
        validate selected files, if are valid audio files (.wav and .ogg) then copy to temp folder
        :param selections:
        :return:
        '''
        for el in selections:
            try:
                self.validate_audio_file(el)
                self.copy(el,self.filechooserRoot)
                self.filechooser._update_files()
            except ValidationError as ve:
                print(ve)
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


    def convertListToDict(self,list, keyword):
        dictList = []
        for el in list:
            dictEl = {keyword: el}
            dictList.append(dictEl)
        return dictList

    def convertDictToList(self, dictList, keyword):
        list = []
        for el in dictList:
            list.append(el[keyword])
        return list

    #MARK: Navigation
    def switchToStageShow(self):

        self.stageShow.rvk.data = self.rvk.data
        self.manager.transition.direction = 'right'
        self.manager.transition.mode = 'pop'
        self.manager.current = 'stageshow'
        self.stageShow.rewindFromKeySetScreen()


    #MARK: RVKeyboard Delegate Methods
    def rvkeyboard_cell_selected(self, index):
        selected = self.rvk.data[index]
        #dictList = self.convertListToDict(fileList, 'filePath')

        # Update the sound pack detail view
        #self.soundPackDetail.disabled = False
        #self.fl.disabled = False
        self.kLabel.setSelected(False)
        print('############ selected sound list')
        print(selected['soundlist'])
        self.fl.data = selected['soundlist']
        self.kLabel.text = selected['key']
        self.name_input.text = selected['name']

    def rvkeyboard_cell_deselected(self, index):
        #self.soundPackDetail.disabled = True
        self.fl.data = []
        self.kLabel.text = ''
        self.name_input.text = 'No selection'

    def rvkeyboard_cell_on_change(self, index):
        soundlist = self.rvk.data[index]['soundlist']
        #dictList = self.convertListToDict(fileList, 'filePath')
        self.fl.data = soundlist

    # Label delegate methods
    def onSelectChange(self, isSelected):
        self.bindKeyboard(isSelected)

    # SPDTextInputDelegate Methos
    def spdtextinput_on_focus(self, isFocused,text):
        index = self.rvk.selectedIndex
        if index is not None:  # if index: will cause False if index=0
            self.rvk.editElementByIndex(index=index, key = None, name = text, soundlist = None)

    # SPDListDelegate Methods
    def spdlist_data_changed(self, data):
        index = self.rvk.selectedIndex
        if index is not None:  # if index: will cause False with index=0
            #dictList = self.convertDictToList(data, 'filePath')
            self.rvk.editElementByIndex(index=index, key = None, name = None, soundlist = data)

class KeyLabel(Label):
    ''' Adds selection support to the Label '''
    selected = BooleanProperty(False)
    delegate = LabelDelegate()

    def on_touch_down(self, touch):
        ''' Adds selection on touch down '''
        if super(KeyLabel,self).on_touch_down(touch):
            self.setSelected(not self.selected)
        if self.collide_point(*touch.pos):
            self.setSelected(not self.selected)
        return

    def setSelected(self, isSelected):
        self.selected = isSelected
        self.delegate.onSelectChange(self.selected)

class SPDName(TextInput):

    delegate = ObjectProperty(SPDTextInputDelegate())

    def __init__(self,**kwargs):
        super(SPDName, self).__init__(**kwargs)
        #self.bind(on_text_validate=self.on_enter)
        #self.bind(focus=self.on_focus)

    def on_focus(self, instance, value):
        self.delegate.spdtextinput_on_focus(value, self.text)
    '''
    def on_enter(instance, value):
        print('User pressed enter in', instance)
    '''

class FileListCell(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    slider = ObjectProperty(None)
    delegate = SoundDetail_Delegate()

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(FileListCell, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(FileListCell,self).on_touch_down(touch):
            if self.selected:
                self.parent.deselect_node(self.index)
            else:
                self.parent.select_with_touch(self.index, touch)
        if self.collide_point(*touch.pos) and self.selectable:
            if self.selected:
                self.parent.deselect_node(self.index)
            else:
                self.parent.select_with_touch(self.index, touch)
            return

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            pass
            # print("selection changed to {0}".format(rv.data[index]))
        else:
            pass
            #print("selection removed for {0}".format(rv.data[index]))
    def deleteClicked(self):
        fl = self.parent.parent
        fl.delete(self.index)

    def getBaseName(self, path):
        return os.path.basename(path)

    # Slider Methods

    def sliderOnTouchUp(self):
        fl = self.parent.parent
        fl.sliderUpdated(self.index, self.slider.value)

    def menubar_on_release(self,itemId):
        print(self.filepath)
        print(self.volume)
        #self.delegate.menubar_on_release(self.index, itemId)

class FileList(RecycleView):

    delegate = ObjectProperty(SPDListDelegate())

    def __init__(self,**kwargs):
        super(FileList, self).__init__(**kwargs)
        self.clickedFile = None
        self.data = [{'filepath': 'bgm/nice-work.wav','volume':1}, {'filepath': 'bgm/nice-work.wav','volume':1}, {'filepath': 'bgm/nice-work.wav', 'volume':1}, {'filepath': 'bgm/nice-work.wav', 'volume':1}]
        #self.data = {'filePath': ['bgm/nice-work.wav', 'bgm/nice-work.wav', 'bgm/okay-come-on.wav', 'bgm/nice-work.wav', 'bgm/okay-come-on.wav']}
        #self.data = [{'key':'a','filePath': 'bgm/nice-work.wav'}, {'key':'s','filePath': 'bgm/nice-work.wav'}, {'key':'d','filePath': 'bgm/nice-work.wav'}, {'key':'f','filePath': '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm/okay-come-on.wav'}]

        #self.data = [{'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm/okay-come-on.wav'}]

    def delete(self, index):
        self.data.pop(index)
        self.delegate.spdlist_data_changed(self.data)

    def add(self):
        pass
        #self.data.insert(-1, {'filePath': 'img/stage.png'})
        #self.data.add({'filePath': 'img/stage.png'})

    def sliderUpdated(self, index, slider_value):
        self.data[index]['volume'] = slider_value
        print(self.data[index]['volume'])
        self.delegate.spdlist_data_changed(self.data)

# MARK: Error types

class ValidationError(Exception):
    pass

