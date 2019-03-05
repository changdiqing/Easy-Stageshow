from kivy.properties import BooleanProperty,ObjectProperty, StringProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
import json
import os

class RVKeyboardDelegate():

    def rvkeyboard_cell_selected(self,index):
        pass

    def rvkeyboard_cell_deselected(self, index):
        pass

    def rvkeyboard_cell_on_change(self, index):
        pass

    def rvkeyboard_cell_on_touch_down(self, cell, touch):
        pass

class SelectableRecycleGridLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
    ''' Adds selection and focus behaviour to the view '''

class RVKeyboard(RecycleView):

    delegate = ObjectProperty(RVKeyboardDelegate())
    selectedIndex = None
    rootPath = StringProperty('./source/bgm')

    def __init__(self,**kwargs):
        super(RVKeyboard, self).__init__(**kwargs)
        self.clickedFile = None
        self.data = [{'key':'1','name':'bgm1','isMusic':True,'soundlist': []},
                     {'key':'2','name':'bgm2','isMusic':True,'soundlist': []},
                     {'key':'3','name':'bgm3','isMusic':True,'soundlist': []},
                     {'key':'4','name':'bgm4','isMusic':True,'soundlist': []},
                     {'key':'5','name':'bgm5','isMusic':True,'soundlist': []},
                     {'key':'6','name':'bgm6','isMusic':True,'soundlist': []},
                     {'key':'7','name':'bgm7','isMusic':True,'soundlist': []},
                     {'key':'8','name':'bgm8','isMusic':True,'soundlist': []},
                     {'key':'9','name':'bgm9','isMusic':True,'soundlist': []},
                     {'key':'10','name':'bgm10','isMusic':True,'soundlist': []},
                     {'key':'a','name':'sound1','isMusic':False,'soundlist': []},
                     {'key':'s','name':'sound2','isMusic':False,'soundlist': []},
                     {'key':'d','name':'sound3','isMusic':False,'soundlist': []},
                     {'key':'f','name':'sound4','isMusic':False,'soundlist': []},
                     {'key':'g','name':'sound5','isMusic':False,'soundlist': []},
                     {'key':'y','name':'sound6','isMusic':False,'soundlist': []},
                     {'key':'x','name':'sound7','isMusic':False,'soundlist': []},
                     {'key':'c','name':'sound8','isMusic':False,'soundlist': []},
                     {'key':'v','name':'sound9','isMusic':False,'soundlist': []},
                     {'key':'b','name':'sound10','isMusic':False,'soundlist': []}]
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
            new_sound = {'filepath': self.clickedFile, 'volume': 1}
            newFileList = self.data[index]['soundlist'].append(new_sound)
            self.editElementByIndex(index = index, key = None, name = None, soundlist=newFileList)
            self.delegate.rvkeyboard_cell_on_change(index)
            rvCell.selected = True
    def rewindRvCellTouchDown(self, rvCell, touch):
        index = rvCell.index

        if rvCell.selected:
            self.selectedIndex = index  #rvCell.index
            self.delegate.rvkeyboard_cell_selected(index)
        else:
            self.selectedIndex = None
            self.delegate.rvkeyboard_cell_deselected(index)

        self.delegate.rvkeyboard_cell_on_touch_down(rvCell, touch)

    def editElementByIndex(self, index=0, key = None, name = None, soundlist = None):

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

        if soundlist:
            thisList = soundlist
        else:
            thisList = self.data[index]['soundlist']

        isMusic = self.data[index]['isMusic']

        self.data[index] = {'key':thisKey,'name':thisName, 'isMusic': isMusic ,'soundlist': thisList}

        self.saveByPath()
        self.clickedFile = None

    def getBaseName(self, path):
        return os.path.basename(path)

    def saveByPath(self):  # This is only for internal use
        bgmDataFile = os.path.join(self.rootPath, 'data.txt')
        with open(bgmDataFile, 'w') as outfile:
            json.dump(self.data, outfile)

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