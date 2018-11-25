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
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
import sndhdr
import json
import os
import shutil

class RVKeyboardDelegate():

    def rvkeyboard_cell_selected(self,index):
        pass

    def rvkeyboard_cell_deselected(self, index):
        pass

    def rvkeyboard_cell_on_change(self, index):
        pass

    def rvkeyboard_cell_on_touch_down(self, cell, touch):
        pass

class SPDListDelegate():
    def spdlist_cell_deleted(self, data):
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

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view '''

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
            self.rvk.editElementByIndex(index=index, key = thisKey, name = None, filePath = None)

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
            if self.isSoundFile(filePath):
                self.fileSelected = True
                self.rvk.clickedFile = filePath
            else:
                print('Not a valid image file!')

        self.filechooser.selection = []

    def isSoundFile(self, filePath):
        return sndhdr.what(filePath)

    def switchToStageShow(self):

        self.stageShow.rvk.data = self.rvk.data
        self.manager.transition.direction = 'right'
        self.manager.transition.mode = 'pop'
        self.manager.current = 'stageshow'
        self.stageShow.rewindFromKeySetScreen()

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
            if self.isSoundFile(el):
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

    #RVKeyboard Delegate Methods
    def rvkeyboard_cell_selected(self, index):
        soundPack = self.rvk.data[index]
        fileList = soundPack['filePath']
        key = soundPack['key']
        dictList = self.convertListToDict(fileList, 'filePath')

        # Update the sound pack detail view
        #self.soundPackDetail.disabled = False
        #self.fl.disabled = False
        self.kLabel.setSelected(False)
        self.fl.data = dictList
        self.kLabel.text = key
        self.name_input.text = soundPack['name']

    def rvkeyboard_cell_deselected(self, index):
        #self.soundPackDetail.disabled = True
        self.fl.data = []
        self.kLabel.text = ''
        self.name_input.text = 'No selection'

    def rvkeyboard_cell_on_change(self, index):
        fileList = self.rvk.data[index]['filePath']
        dictList = self.convertListToDict(fileList, 'filePath')
        self.fl.data = dictList

    # Label delegate methods
    def onSelectChange(self, isSelected):
        self.bindKeyboard(isSelected)

    # SPDTextInputDelegate Methos
    def spdtextinput_on_focus(self, isFocused,text):
        index = self.rvk.selectedIndex
        if index is not None:  # if index: will cause False if index=0
            self.rvk.editElementByIndex(index=index, key = None, name = text, filePath = None)

    # SPDListDelegate Methods
    def spdlist_cell_deleted(self, data):
        index = self.rvk.selectedIndex
        if index is not None:  # if index: will cause False with index=0
            dictList = self.convertDictToList(data, 'filePath')
            self.rvk.editElementByIndex(index=index, key = None, name = None, filePath = dictList)

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

class rvkLabel(RecycleDataViewBehavior, Label):
    ''' Adds selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        super(rvkLabel, self).refresh_view_attrs(rv, index, data)
        self.index = index
        return super(rvkLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Adds selection on touch down '''
        if super(rvkLabel,self).on_touch_down(touch):
            if self.selected:
                self.parent.deselect_node(self.index)
            else:
                self.parent.select_with_touch(self.index, touch)
            self.parent.parent.rewindRvCellTouchDown(self, touch)
        if self.collide_point(*touch.pos) and self.selectable:
            if self.selected:
                self.parent.deselect_node(self.index)
            else:
                self.parent.select_with_touch(self.index, touch)
            self.parent.parent.rewindRvCellTouchDown(self, touch)
        return

    def on_touch_up(self, touch):
        ''' Adds selection on touch down '''
        if super(rvkLabel,self).on_touch_up(touch):
            return self.parent.parent.rewindRvCellTouchUp(self, touch)
        if self.collide_point(*touch.pos):
            return self.parent.parent.rewindRvCellTouchUp(self, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            pass
            #print("selection changed to {0}".format(rv.data[index]))
        else:
            pass
            #print("selection removed for {0}".format(rv.data[index]))



class RVKeyboard(RecycleView):

    delegate = ObjectProperty(RVKeyboardDelegate())
    selectedIndex = None
    rootPath = StringProperty('./source/bgm')

    def __init__(self,**kwargs):
        super(RVKeyboard, self).__init__(**kwargs)
        self.clickedFile = None
        self.data = [{'key':'1','name':'bgm1','isMusic':True,'filePath': []},
                     {'key':'2','name':'bgm2','isMusic':True,'filePath': []},
                     {'key':'3','name':'bgm3','isMusic':True,'filePath': []},
                     {'key':'4','name':'bgm4','isMusic':True,'filePath': []},
                     {'key':'5','name':'bgm5','isMusic':True,'filePath': []},
                     {'key':'6','name':'bgm6','isMusic':True,'filePath': []},
                     {'key':'7','name':'bgm7','isMusic':True,'filePath': []},
                     {'key':'8','name':'bgm8','isMusic':True,'filePath': []},
                     {'key':'9','name':'bgm9','isMusic':True,'filePath': []},
                     {'key':'10','name':'bgm10','isMusic':True,'filePath': []},
                     {'key':'a','name':'sound1','isMusic':False,'filePath': []},
                     {'key':'s','name':'sound2','isMusic':False,'filePath': []},
                     {'key':'d','name':'sound3','isMusic':False,'filePath': []},
                     {'key':'f','name':'sound4','isMusic':False,'filePath': []},
                     {'key':'g','name':'sound5','isMusic':False,'filePath': []},
                     {'key':'y','name':'sound6','isMusic':False,'filePath': []},
                     {'key':'x','name':'sound7','isMusic':False,'filePath': []},
                     {'key':'c','name':'sound8','isMusic':False,'filePath': []},
                     {'key':'v','name':'sound9','isMusic':False,'filePath': []},
                     {'key':'b','name':'sound10','isMusic':False,'filePath': []}]
        #self.data = [{'key':'a','filePath': 'bgm/nice-work.wav'}, {'key':'s','filePath': 'bgm/nice-work.wav'}, {'key':'d','filePath': 'bgm/nice-work.wav'}, {'key':'f','filePath': '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm/okay-come-on.wav'}]
        #self.data = [{'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm/okay-come-on.wav'}]

    def delete(self, index):
        pass
        #print(self.data.pop(index))

    def add(self):
        pass
        #self.data.insert(-1, {'filePath': 'img/stage.png'})
        #self.data.add({'filePath': 'img/stage.png'})

    def rewindRvCellTouchUp(self, rvCell, touch):
        index = rvCell.index

        if self.clickedFile:
            newFileList = self.data[index]['filePath'].append(self.clickedFile)
            self.editElementByIndex(index = index, key = None, name = None, filePath=newFileList)
            self.delegate.rvkeyboard_cell_on_change(index)
            rvCell.selected = True
    def rewindRvCellTouchDown(self, rvCell, touch):
        index = rvCell.index

        if rvCell.selected:
            self.selectedIndex = rvCell.index
            self.delegate.rvkeyboard_cell_selected(index)
        else:
            self.selectedIndex = None
            self.delegate.rvkeyboard_cell_deselected(index)

        self.delegate.rvkeyboard_cell_on_touch_down(rvCell, touch)

    def editElementByIndex(self, index=0, key = None, name = None, filePath = None):

        if key:
            thisKey = key
            for el in self.data:
                if el['key'] == key:
                    el['key'] = ''
        else:
            thisKey = self.data[index]['key']

        if name:
            thisName = name
        else:
            thisName = self.data[index]['name']

        if filePath:
            thisPath = filePath
        else:
            thisPath = self.data[index]['filePath']

        isMusic = self.data[index]['isMusic']

        self.data[index] = {'key':thisKey,'name':thisName, 'isMusic': isMusic ,'filePath': thisPath}

        self.saveByPath()
        self.clickedFile = None

    def getBaseName(self, path):
        return os.path.basename(path)

    def saveByPath(self):  # This is only for internal use
        bgmDataFile = os.path.join(self.rootPath, 'data.txt')
        with open(bgmDataFile, 'w') as outfile:
            json.dump(self.data, outfile)


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
        rv = self.parent.parent
        rv.delete(self.index)

    def getBaseName(self, path):
        return os.path.basename(path)

class FileList(RecycleView):

    delegate = ObjectProperty(SPDListDelegate())

    def __init__(self,**kwargs):
        super(FileList, self).__init__(**kwargs)
        self.clickedFile = None
        self.data = [{'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}]
        #self.data = {'filePath': ['bgm/nice-work.wav', 'bgm/nice-work.wav', 'bgm/okay-come-on.wav', 'bgm/nice-work.wav', 'bgm/okay-come-on.wav']}
        #self.data = [{'key':'a','filePath': 'bgm/nice-work.wav'}, {'key':'s','filePath': 'bgm/nice-work.wav'}, {'key':'d','filePath': 'bgm/nice-work.wav'}, {'key':'f','filePath': '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm/okay-come-on.wav'}]

        #self.data = [{'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': 'bgm/nice-work.wav'}, {'filePath': '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm/okay-come-on.wav'}]

    def delete(self, index):
        print(self.data.pop(index))
        self.delegate.spdlist_cell_deleted(self.data)

    def add(self):
        pass
        #self.data.insert(-1, {'filePath': 'img/stage.png'})
        #self.data.add({'filePath': 'img/stage.png'})

