from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, NumericProperty
import pygame
import random

class ShowMode(Screen, Widget):

    stageShow = ObjectProperty(None)
    index = NumericProperty(0)

    soundPackDict = {'key': None}

    pygame.mixer.init()
    soundChannel = pygame.mixer.Channel(0)
    soundChannel.set_volume(0.6)
    pygame.mixer.set_reserved(0)

    data = [{'filePath': 'img/stage.png'} for x in range(10)]


    def __init__(self, **kwargs):
        super(ShowMode, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')

        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass

    # MARK: Keyboard interaction methods

    def init(self):
        self.showImageByIndex(0)

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        #self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        #self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        '''
        print('The key', keycode, 'have been pressed')
        print(' - text is %r' % text)
        print(' - modifiers are %r' % modifiers)

        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard



        soundPack = self.getFileByKey(keycode[1])
        if soundPack:
            if len(soundPack):
                file = random.choice(soundPack)
                sound1 = pygame.mixer.Sound(file)
                self.soundChannel.play(sound1)
        '''

        # Left Right for changing image
        if keycode[1] == 'right':
            self.showImageByIndex(self.index + 1)
            return
        elif keycode[1] == 'left':
            self.showImageByIndex(self.index - 1)
            return
        elif keycode[1] == 'escape':
            self.switchToStageShow()



        self.play_sound_by_keycode(keycode[1])
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

    def play_sound_by_keycode(self, keycode):
        soundPack = self.soundPackDict.get(keycode, None)



        if soundPack and len(soundPack.sounds):
            audio = random.choice(soundPack.sounds)
            if soundPack.isMusic:
                self.soundChannel.play(audio)
            else:
                audio.play()

    def bindKeyboard(self, bool=True):
        if bool:
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
        else:
            self._keyboard.unbind(on_key_down=self._on_keyboard_down)


    def showImageByIndex(self, index=0):  # direction can be 1 or -1

        if index<0:
            print('Failed loading last image, index not allow to be negative!')
            return

        try:
            self.image.source = self.data[index]['filePath']
            self.index = index
            keycode = self.data[index]['enterBGM']
            if len(keycode)>0:
                self.soundChannel.stop()  # if there is keycode given, stop the current BGM no matter if there is
                # next BGM assigned to the given keycode
                self.play_sound_by_keycode(keycode)
        except IndexError:
            print('Failed loading last/next image! ' + str(IndexError))

    # MARK: Navigation Methods
    def switchToStageShow(self):
        # stop keyboard interaction and stop playing sounds
        self.bindKeyboard(False)
        pygame.mixer.stop()

        # activate stageshow keyboard interaction for preview
        self.stageShow.bindKeyboard(True)

        # do the screen switch
        self.manager.transition.direction = 'right'
        self.manager.transition.mode = 'pop'
        self.manager.current = 'stageshow'