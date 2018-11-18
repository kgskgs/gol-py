# -*- coding: utf-8 -*-
"""
Created on Mon Jun 05 11:48:02 2017

@author: k
"""
import kivy
kivy.require('1.10.0')
from kivy.config import Config

Config.set('input', 'mouse', 'mouse,disable_multitouch') #disable touchscreen emulation
#set initial window location
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'top', '100')
Config.set('graphics', 'left', '100')

from kivy.app import App
from kivy.core.window import Window


import gol_base

class GOL(App):    
    def build(self):
        #set window attributes
        Window.clearcolor = (1, 1, 1,1)
        Window.size=(1045,845)
        Window.minimum_width=1045
        Window.minimum_height=845
        
        base = gol_base.baseClass()
        return base
            
if __name__ == '__main__':
    GOL().run() #main loop
    