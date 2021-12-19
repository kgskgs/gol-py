# -*- coding: utf-8 -*-
"""
Created on Wed Jul 05 21:59:52 2017

@author: k
"""
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.properties import BooleanProperty
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.graphics import Rectangle
from kivy.graphics import Color
from kivy.graphics import Line

from collections import defaultdict

import planetracker
import scatter_transforms
import types

#this will deal with game logic and loops, also root layout for the .kv file
#holds the functions used by the UI
class baseClass(BoxLayout):
    #these properties will be linked to the .kv file
    #trigger events when changed
    history = ListProperty([])
    generation = ListProperty([0])
    
    dragDraw = BooleanProperty(True)
    running = BooleanProperty(False)
    delClear = BooleanProperty(True)
    
    menuBoundry = NumericProperty(0)
    runDelay = NumericProperty(0.5)
    
    def __init__(self, HALF_LENGTH = 2500, SQ_SIZE = 10,  **kwargs):
        super(baseClass, self).__init__(**kwargs)
        
        self.allCells = [] #keep references to all cells (dead - None) 2d - aligns with grid
        self.aliveCells = set() #references to alive cells only, contains tuples (x-coord, y-coord)
        self.HALF_LENGTH = HALF_LENGTH
        self.SQ_SIZE = SQ_SIZE #multiple of 10
        self.MAX_INDEX = HALF_LENGTH/SQ_SIZE*2
                
        #Scatter Plane Layout where we build the gird, and use for transforms
        #replace touch functions with the modified ones
        #defined only in .kv
        transformPlane = self.ids["layoutS"]  #access .kv element by id
        
        transformPlane.on_touch_down = types.MethodType(scatter_transforms.on_touch_down, transformPlane)
        transformPlane.on_touch_move = types.MethodType(scatter_transforms.on_touch_move, transformPlane)
        transformPlane.transform_with_touch = types.MethodType(scatter_transforms.transform_with_touch, transformPlane)        
        
        self.drawPlane = planetracker.planeTracker(self, pos=transformPlane.pos, size=transformPlane.size)
        transformPlane.add_widget(self.drawPlane)
        
        #draw the grid and populate self.allCells with None
        start = -HALF_LENGTH #(0,0) is the bottom left corner of the visible part of the layout

        with transformPlane.canvas:
            Color(0.4,0.4,0.4)
            for x in range(HALF_LENGTH*2//SQ_SIZE + 1): #draw grid with vertical lines on the main layout
                Line(points=[start, -HALF_LENGTH, start, HALF_LENGTH], width=1)
                Line(points=[-HALF_LENGTH, start, HALF_LENGTH, start], width=1)
                start += int(SQ_SIZE)
                      
        for y in range(HALF_LENGTH*2//SQ_SIZE):
            tmpArr = []
            for x in range(HALF_LENGTH*2//SQ_SIZE):
                tmpArr.append(None)
            self.allCells.append(tmpArr)  
    

    #rules are appliedlied here
    def step(self, delay=0): #delay is used (only) by the clock when running
        #if no history add as first state
        self.generation.append(self.generation[-1]+1)
        if len(self.history) == 0: self.history.append(self.aliveCells.copy())
        
        neighbours = defaultdict(int) #default value 0, so no need to check for membership
        
        for index in self.aliveCells: #increase the count of neightbours of all living cells by 1
            indexX, indexY = index
            neighbours[(indexX + 1, indexY)] += 1
            neighbours[(indexX + 1, indexY + 1)] += 1
            neighbours[(indexX + 1, indexY - 1)] += 1
            neighbours[(indexX - 1, indexY)] += 1
            neighbours[(indexX - 1, indexY + 1)] += 1
            neighbours[(indexX - 1, indexY - 1)] += 1
            neighbours[(indexX, indexY + 1)] += 1
            neighbours[(indexX, indexY - 1)] += 1
                    
        for index in self.aliveCells.union(neighbours): #we need to check both living and dead cells that could change
            nb = neighbours[index]
            indexX, indexY = index
            #apply game rules
            if index in self.aliveCells:
                if nb < 2 or nb > 3:
                    self.aliveCells.remove(index)
                    self.drawPlane.canvas.remove(self.allCells[indexX][indexY])
                    self.allCells[indexX][indexY] = None        
            elif nb == 3:
                if -1 < indexX < self.MAX_INDEX and -1 < indexY < self.MAX_INDEX: #we have to check if we are inside bounds when adding new cells only
                    self.allCells[indexX][indexY] = Rectangle(pos=self.arrToGrid(indexX, indexY), size=(self.SQ_SIZE, self.SQ_SIZE))
                    self.aliveCells.add(index)
                    self.drawPlane.canvas.add(self.allCells[indexX][indexY])
        #add to history            
        if len(self.history) == 100: 
            del self.history[1]
            del self.generation[1]    
        self.history.append(self.aliveCells.copy())
        
    def runToggle(self):
        if self.running:
            self.running = False
            self.runEvent.cancel()
        else:
            self.running = True            
            self.runEvent = Clock.schedule_interval(self.step, self.runDelay)
            if not self.delClear: #only erase history on start
                self.history = []
                self.generation = [0]
            elif len(self.history) > 1: #slice off history after current point
                sliderVal = int(self.ids["hist"].value) + 1
                del self.history[sliderVal:]
                del self.generation[sliderVal:]
            
                
    def updateSpeed(self): #if speed is changed when running we reschedule the event
        if self.running:
            self.runEvent.cancel()
            self.runEvent = Clock.schedule_interval(self.step, self.runDelay)
    
    def dragModeToggle(self):
        if self.dragDraw: self.dragDraw = False
        else: self.dragDraw = True
        
    def clear(self, hard = True): #hard - don't clear history if it's called from browseHistory
        self.drawPlane.canvas.clear() #this erases color as well
        for cell in self.aliveCells:
            indexX, indexY = cell
            self.allCells[indexX][indexY] = None
        self.aliveCells.clear()
        self.drawPlane.canvas.add(Color(0,0,0))
        
        if self.delClear and hard:
            self.history = []
            self.generation = [0]
             
    def eraseToggle(self):
        if self.delClear: self.delClear = False
        else: self.delClear = True 
        
    def browseHistory(self, slider, touch):
        x,y = touch.pos
        target = int(slider.value)
        
        if slider.collide_point(x, y):
            if len(self.history) > target and self.history[target] != self.aliveCells:               
                self.clear(hard=False)
                for indeces in self.history[target]:
                        indexX, indexY = indeces
                        self.allCells[indexX][indexY] = Rectangle(pos=self.arrToGrid(indexX, indexY), size=(self.SQ_SIZE, self.SQ_SIZE))
                        self.aliveCells.add(indeces)
                        self.drawPlane.canvas.add(self.allCells[indexX][indexY])
            return True #stop event bubbling

    def about(self):
        aboutText ="""[size=14]Rules:\n
        1. Any live cell with fewer than two live neighbours dies
        2. Any live cell with two or three live neighbours lives on to the next generation.
        3. Any live cell with more than three live neighbours dies
        4. Any dead cell with exactly three live neighbours becomes a live cell
        (alive = black, dead = white)\n
Controls:\n
        move grid - right mouse
        zoom - mousewheel
        draw cells - left mouse / left mouse drag
_________________
[/size][size=10]Kalin Stoyanov 2017[/size]"""        
        
        ab = Popup(title='Game of Life - a cellular automaton', content=Label(text=aboutText,markup=True), 
                     size_hint=(None,None), size=(535,325))
        ab.open()
        
    #takes array indeces and returns grid coordiantes
    #returns tuple
    def arrToGrid(self, x, y):
        return (x*self.SQ_SIZE - self.HALF_LENGTH, y*self.SQ_SIZE - self.HALF_LENGTH)