from kivy.app import App
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.screenmanager import ScreenManager,Screen, CardTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
import os
import pygame
import random
import json
import shutil
import atexit

from KeyboardSetScreen import KeyboardSetScreen, RVKeyboardDelegate, rvkLabel
from StageSetScreen import StageSetScreen
from ShowMode import ShowMode
from TarfileHandler import TarfileHandler
from FileChooserDialog import SaveDialog, LoadTarDialog

class CustomFileChooser(FileChooserIconView):

    '''
    def on_touch_down(self, touch):

        #return self.parent.parent.parent.saveFileToRV('123')

        if super(CustomFileChooser,self).on_touch_down(touch):
            selectedFiles = self.selection
            if len(selectedFiles)>0:
                return self.parent.parent.parent.saveFileToRV(selectedFiles[0])

        if self.collide_point(*touch.pos):
            selectedFiles = self.selection
            if len(selectedFiles)>0:
                return self.parent.parent.parent.saveFileToRV(selectedFiles[0])
    '''

class showData():
    def __init__(self, tempDir, tarFile, imgData, bgmData):
        self.tempDir = tempDir
        self.tarFile = tarFile
        self.imgData = imgData
        self.bgmData = bgmData

class myGridLayout(GridLayout):
    def __init__(self,**kwargs):
        super(myGridLayout, self).__init__(**kwargs)

class myLabel(Button):
    def __init__(self,**kwargs):
        super(myLabel, self).__init__(**kwargs)

class StageShow(Screen, Widget, RVKeyboardDelegate):

    stageSetScreen = ObjectProperty(None)
    keySetScreen = ObjectProperty(None)
    showModeScreen = ObjectProperty(None)
    keySelected = BooleanProperty(False)
    inTouchDown = BooleanProperty(False)

    tarfileHandler = TarfileHandler()

    soundPackDict = {'key': None}

    soundPacks = [{'key':'a', 'filePath': []},
                  {'key':'a', 'filePath': []},
                  {'key':'a', 'filePath': []},
                  {'key':'a', 'filePath': []}]
    pygame.mixer.init()
    soundChannel = pygame.mixer.Channel(0)
    soundChannel.set_volume(0.4)
    pygame.mixer.set_reserved(0)

    fileName = StringProperty('')


    def __init__(self, **kwargs):
        super(StageShow, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')

        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass

        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        #self.soundPacks = self.createSoundlist(self.rvk.data)
        self.soundPackDict = self.createSoundPackDict(self.rvk.data)

    # MARK: Touch Events
    def touchDownEvent(self, pos):
        self.inTouchDown = True

    def touchUpEvent(self, pos):
        self.inTouchDown = False  # Flag down
        self.keySelected = False
        self.ic.pos = [-200, -200]

    def on_touch_move(self, touch):
        self.ic.center = touch.pos
        return

    # MARK: Keyboard interaction methods

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        #self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        #self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard

        '''

        soundPack = self.getFileByKey(keycode[1])
        if soundPack:
            if len(soundPack):
                file = random.choice(soundPack)
                sound1 = pygame.mixer.Sound(file)
                self.soundChannel.play(sound1)
        '''
        soundPack = self.soundPackDict.get(keycode[1], None)

        if soundPack and len(soundPack.sounds):
            audio = random.choice(soundPack.sounds)
            if soundPack.isMusic:
                self.soundChannel.play(audio)
            else:
                audio.play()
            # if play then stop

            #while True:
            #    #检查音乐流播放，有返回True，没有返回False
            #    #如果没有音乐流则选择播放
            #    if pygame.mixer.music.get_busy()==False:
            #        pygame.mixer.music.play()

            #sounda= pygame.mixer.Sound("nice-work.wav")
            #sound = SoundLoader.load('bgm/nice-work.wav')
            #if sound:
            #    print("Sound found at %s" % sound.source)
            #    print("Sound is %.3f seconds" % sound.length)
            #    sound.play()

        # Stop Keyboard
        #if keycode[1] == 'escape':
        #    keyboard.release()

        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def bindKeyboard(self, bool=True):
        if bool:
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        else:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)

    # MARK: Navigation Methods

    def switchToStageSettings(self):
        self.bindKeyboard(False)
        self.stageSetScreen.rv.data = self.rv.data
        self.manager.transition.direction = 'left'
        self.manager.transition.mode = 'push'
        self.manager.current = 'stagesettings'

    def switchToKeyboardSetScreen(self):
        self.bindKeyboard(False)
        self.keySetScreen.rvk.data = self.rvk.data
        self.manager.transition.direction = 'left'
        self.manager.transition.mode = 'push'
        self.manager.current = 'keyboardset'

    def switchToShowMode(self):
        # stop keyboard interaction
        self.bindKeyboard(False)

        # activate showmode keyboard interaction, pass images and sound data, and show first image
        self.showModeScreen.bindKeyboard(True)
        self.showModeScreen.data = self.rv.data
        self.showModeScreen.soundPackDict = self.soundPackDict
        self.showModeScreen.init()  # show first image

        # do screen switch
        self.manager.transition.direction = 'left'
        self.manager.transition.mode = 'push'
        self.manager.current = 'showmode'

    def createSoundlist(self, soundPacks):
        list = []
        for soundPack in soundPacks:
            sounds = []
            for file in soundPack['filePath']:
                sounds.append(pygame.mixer.Sound(file))
            newDict = {'key': soundPack['key'],'isMusic': soundPack['isMusic'], 'sounds': sounds}
            list.append(newDict)
        return list

    def createSoundPackDict(self, soundLists):
        dict = {}
        for soundList in soundLists:
            sounds = []
            for file in soundList['filePath']:
                sd = pygame.mixer.Sound(file)
                sd.set_volume(1)
                sounds.append(sd)
            soundPack = SoundPack(soundList['isMusic'], sounds)
            dict[soundList['key']] = soundPack
        return dict

    #  Navigation Methods

    def rewindFromKeySetScreen(self):
        self.soundPackDict = self.createSoundPackDict(self.rvk.data)
        self.bindKeyboard(True)

    # FileChooser Methods
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadTarDialog(load=self.loadArchive, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_save(self):
        content = SaveDialog(save=self.createArchive, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def saveAndUnloadCurrentArchive(self):
        # Overwrite the current tarfile with the content of tempDir
        # Delete all loaded data
        self.rvk.data = []
        self.rv.data = []

        self.tarfileHandler.overwriteTarWithTemp()
        self.tarfileHandler.deleteDir(self.tarfileHandler.tempDir)




    def loadArchive(self, filename):
        '''
        fetch data with given file path, if succeeded then clean the last load feed with loaded data, else give up and
        pop up a warning.

        :param filename:
        :return:
        None
        '''

        # Overwrite the current tarfile with the content of tempDir

        fullPath = filename[0]
        showData = self.fetchDataFromArchive(fullPath)

        if showData:
            self.saveAndUnloadCurrentArchive()

            # Feed with fetch data
            imgPath = os.path.join(showData.tempDir, 'img')
            bgmPath = os.path.join(showData.tempDir, 'bgm')

            self.stageSetScreen.filechooserRoot = imgPath
            self.keySetScreen.filechooserRoot = bgmPath
            self.rv.data = showData.imgData
            self.rv.saveByPath()
            self.rvk.data = showData.bgmData
            self.rvk.saveByPath()
            self.soundPackDict = self.createSoundPackDict(self.rvk.data)
            self.tarfileHandler.tempDir = showData.tempDir
            self.tarfileHandler.tarFilePath = showData.tarFile
        else:
            print('Failed loading data from archive!')

        self.dismiss_popup()

    def fetchDataFromArchive(self, filename):
        '''
        :param filename:
        :return:
            None: If fetch was not successful
            showData(): If fetch was successful
        '''

        tempDir = self.tarfileHandler.extractTarToTemp(filename)
        if not tempDir:  # if tempDir is not None then extraction was successful
            print('Invalid file, failed to load!')
            return

        imgPath = os.path.join(tempDir, 'img')
        bgmPath = os.path.join(tempDir, 'bgm')
        imgDataFile = os.path.join(imgPath, 'data.txt')
        bgmDataFile = os.path.join(bgmPath, 'data.txt')
        imgData = self.loadByPath(imgDataFile)
        bgmData = self.loadByPath(bgmDataFile)

        if imgData:
            imgData = self.replaceRootpath(imgPath,imgData)

            # Add enterBGM if missing, data of old version has no enterBGM
            for el in imgData:
                if not 'enterBGM' in el: # this element does not have the key 'enterBGM'
                    el['enterBGM'] = ''
        else:
            imgData = []
            print('Failed loading img data.txt')

        if bgmData:
            bgmData = self.replaceRootpath(bgmPath,bgmData)

            # Add volume if missing, data of old version has no enterBGM
            for el in bgmData:
                if not 'volume' in el: # this element does not have the key 'enterBGM'
                    el['volume'] = 1

        else:
            bgmData = [{'key':'1','name':'bgm1','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'2','name':'bgm2','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'3','name':'bgm3','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'4','name':'bgm4','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'5','name':'bgm5','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'6','name':'bgm6','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'7','name':'bgm7','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'8','name':'bgm8','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'9','name':'bgm9','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'10','name':'bgm10','isMusic':True,'filePath': [], 'volume': 1},
                             {'key':'a','name':'sound1','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'s','name':'sound2','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'d','name':'sound3','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'f','name':'sound4','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'g','name':'sound5','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'y','name':'sound6','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'x','name':'sound7','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'c','name':'sound8','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'v','name':'sound9','isMusic':False,'filePath': [], 'volume': 1},
                             {'key':'b','name':'sound10','isMusic':False,'filePath': [], 'volume': 1}]
            print('Failed loading bgm data.txt')

        return showData(tempDir, filename, imgData, bgmData)


    def loadByPath(self, filePath):
        try:
            with open(filePath) as json_file:
                return json.load(json_file)
        except:
            print('Failed to load file: ' + filePath)
        finally:
            pass

    def replaceRootpath(self,root,data):
        for el in data:
            filePathEle = el['filePath']
            if isinstance(filePathEle, list):
                newFilePathEle = []
                for filePath in filePathEle:
                    baseName = os.path.basename(filePath)
                    newFilePathEle.append(os.path.join(root, baseName))
                    el['filePath'] = newFilePathEle
            else:
                baseName = os.path.basename(filePathEle)
                newFilePathEle = os.path.join(root, baseName)
                el['filePath'] = newFilePathEle
        return data

    def createArchive(self, path, filename):
        '''
        try to copy the template.tar to target filepath, if fail then give up and pop up warning
        if succeeded then load the newly created tar file and start editing

        :param path: current path of filechooser
        :param filename: given filename of filechooser
        :return:
        '''
        # template tar file
        template = 'source/template.tar'

        # If filename does not include tar extension then add one
        file_name, file_ext = os.path.splitext(filename)
        if not file_ext == '.tar':
            filename = filename + '.tar'
        fullPath = os.path.join(path, filename)

        # Try to copy the template to target path
        try:
            shutil.copyfile(template, fullPath)
        except IOError as e:
            print("Unable to copy file. %s" % e)
            return
        except:
            print("Unexpected error:", os.sys.exc_info())
            return

        # If copy suceeded then load the archive, here if loading failed
        self.loadArchive([fullPath])

    def copy(self, source, target):
        #source = '/Users/diqingchang/PycharmProjects/StageShowImageSound/img/mini.jpg'
        #target = '/Users/diqingchang/PycharmProjects/StageShowImageSound/bgm'

        #assert not os.path.isabs(source)
        #print(os.path.dirname(source))
        #target = os.path.join(target, os.path.dirname(source))

        # adding exception handling
        try:
            shutil.copy(source, target)
        except IOError as e:
            print("Unable to copy file. %s" % e)
        except:
            print("Unexpected error:", os.sys.exc_info())


    def cleanup(self):
        self.saveAndUnloadCurrentArchive()

    # RVK Delegate Methods
    def rvkeyboard_cell_on_touch_down(self, rvkCell, touch):

        if self.inTouchDown:  # if cell selected before touch up, cell will be picked and information saved in self.ic
            self.ic.center = touch.pos
            self.ic.key = rvkCell.key
            self.ic.name = rvkCell.name
            self.keySelected = True

    # RV Delegate Methods
    def on_rvcelltouch_up(self, rvCell):
        index = rvCell.index

        if not  self.ic.key == '##':
            self.rv.editElementByIndex(index = index, filePath= None, enterBGMKey=self.ic.key)
            self.ic.key = '##'


class SoundPack():

    def __init__(self, isMusic, sounds):
            self.isMusic = isMusic  # Bool
            self.sounds = sounds  # [pygame.mixer.Sound(file)]

class StageShowApp(App):
    def build(self):

        # Instantiation
        ct = CardTransition()
        sm= ScreenManager(transition = ct)
        stageShow = StageShow(name = 'stageshow')
        stageSetScreen = StageSetScreen(name = 'stagesettings')
        #keyboardScreen = KeyboardSetScreen.kv(name= 'keyboardset')
        keyboardScreen = KeyboardSetScreen(name = 'keyboardset')
        showModeScreen = ShowMode(name = 'showmode')

        # Link the screens
        stageShow.stageSetScreen = stageSetScreen
        stageShow.keySetScreen = keyboardScreen
        stageShow.showModeScreen = showModeScreen
        stageSetScreen.stageShow = stageShow
        keyboardScreen.stageShow = stageShow
        showModeScreen.stageShow = stageShow

        # Add widgets

        sm.add_widget(stageShow)
        sm.add_widget(showModeScreen)
        sm.add_widget(stageSetScreen)
        sm.add_widget(keyboardScreen)

        atexit.register(stageShow.cleanup)

        return sm





if __name__ == '__main__':
    StageShowApp().run()