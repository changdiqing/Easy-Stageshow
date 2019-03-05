from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
import os
import json
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

class RVDelegate():
    def on_rvcelltouch_up(self, rvCell):
        pass
    def on_rvcelltouch_down(self, rvCell):
        pass

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout, BoxLayout):
    ''' Adds selection and focus behaviour to the view '''

class RV(RecycleView):

    rootPath = StringProperty('./source/img')
    delegate = ObjectProperty(RVDelegate())

    def __init__(self,**kwargs):
        super(RV, self).__init__(**kwargs)
        self.clickedFile = None
        self.data = [{'filePath': 'source/img/stage.png', 'enterBGM': ''} for x in range(10)]

    def delete(self, index):
        print(self.data.pop(index))

    def add(self):
        self.data.append({'filePath': 'source/img/stage.png', 'enterBGM': ''})
        #self.data.add({'filePath': 'img/stage.png'})

    def saveByPath(self):  # This is only for internal use
        imgDataFile = os.path.join(self.rootPath, 'data.txt')
        with open(imgDataFile, 'w') as outfile:
            json.dump(self.data, outfile)

    def editElementByIndex(self, index=0, filePath = None, enterBGMKey = None):

        if filePath:
            thisPath = filePath
        else:
            thisPath = self.data[index]['filePath']

        if enterBGMKey:
            enterBGM = enterBGMKey
        else:
            enterBGM = self.data[index]['enterBGM']

        self.data[index] = {'filePath': thisPath, 'enterBGM': enterBGM}

        self.saveByPath()
        self.clickedFile = None

    def rewindRVCellTouchUp(self, rvCell):

        index = rvCell.index

        if self.clickedFile:
            self.editElementByIndex(index = index, filePath=self.clickedFile, enterBGMKey=None)
            #self.delegate.rvkeyboard_cell_on_change(index)
            rvCell.selected = True

        self.delegate.on_rvcelltouch_up(rvCell)

    def rewindRVCellTouchDown(self, rvCell):
        self.delegate.on_rvcelltouch_down(rvCell)

class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Adds selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        super(SelectableLabel, self).refresh_view_attrs(rv, index, data)
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Adds selection on touch down '''

        if super(SelectableLabel,self).on_touch_down(touch):
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

    def on_touch_up(self, touch):
        ''' Adds selection on touch down '''

        if super(SelectableLabel,self).on_touch_up(touch):
            return self.parent.parent.rewindRVCellTouchUp(self)
        if self.collide_point(*touch.pos):
            return self.parent.parent.rewindRVCellTouchUp(self)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            pass#print("selection changed to {0}".format(rv.data[index]))
        else:
            pass
            #print("selection removed for {0}".format(rv.data[index]))
    def remove_selection(self):
        # Remove selection
        if self.selected is not None:
            self.selected.selected = False
            self.selected = None