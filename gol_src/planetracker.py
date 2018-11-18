# -*- coding: utf-8 -*-
"""
Created on Wed Jul 05 22:00:21 2017

@author: k
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color
from kivy.graphics import Rectangle
from math import floor


#this stays within the scatterPlane layout and is used for drawing/erasing cells
class planeTracker(Widget):
    def __init__(self, base, **kwargs):
        super(planeTracker, self).__init__(**kwargs)
        with self.canvas:
            Color(0,0,0)
        self.base = base 
        self.SQ_SIZE = base.SQ_SIZE
        self.HALF_LENGTH = base.HALF_LENGTH

    def on_touch_down(self, touch):
        x, y = touch.x, touch.y
        #print self.parent.parent
        if self.to_window(x,y)[1] <= self.base.menuBoundry: #if the touch is on the menu don't draw
            return super(planeTracker, self).on_touch_down(touch)        
        
        #check that we are inside the bounds
        if touch.button=="left" and \
        x < self.HALF_LENGTH and x > -self.HALF_LENGTH and \
        y < self.HALF_LENGTH and y > -self.HALF_LENGTH:
                    
            gridPos = self.coordsToGrid(touch.pos)
            indexX, indexY = self.gridToArr(gridPos)
            
            #if cell doesn't exist - draw it
            if not (indexX, indexY) in self.base.aliveCells:
                with self.canvas:
                    #add the new cell to the array when drawing it
                    self.base.allCells[indexX][indexY] = Rectangle(pos=gridPos, size=(self.SQ_SIZE, self.SQ_SIZE))
                    self.base.aliveCells.add((indexX, indexY))
            #if cell exists - erase it:
            else:
                self.canvas.remove(self.base.allCells[indexX][indexY])
                self.base.allCells[indexX][indexY] = None
                self.base.aliveCells.remove((indexX, indexY))
            return True
        return super(planeTracker, self).on_touch_down(touch)
        
    def on_touch_move(self, touch): 
        x, y = touch.x, touch.y
        if self.to_window(x,y)[1] <= self.base.menuBoundry:
            return super(planeTracker, self).on_touch_down(touch)   
        
        if touch.button=="left" and \
        x < self.HALF_LENGTH and x > -self.HALF_LENGTH and \
        y < self.HALF_LENGTH and y > -self.HALF_LENGTH:
            gridPos = self.coordsToGrid(touch.pos)        
            indexX, indexY = self.gridToArr(gridPos)
            if not (indexX, indexY) in self.base.aliveCells:
                if self.base.dragDraw:
                    with self.canvas:
                        self.base.allCells[indexX][indexY] = Rectangle(pos = gridPos, size=(self.SQ_SIZE, self.SQ_SIZE))
                        self.base.aliveCells.add((indexX, indexY))
            elif not self.base.dragDraw:
                self.canvas.remove(self.base.allCells[indexX][indexY])
                self.base.allCells[indexX][indexY] = None
                self.base.aliveCells.remove((indexX, indexY))
            return True
        return super(planeTracker, self).on_touch_move(touch)
        
    #takes touch coordiantesreturns bottom left corner of the grid square they lay in
    #returns tuple
    def coordsToGrid(self, pos):
        x, y = pos
        return (floor(x/self.SQ_SIZE)*self.SQ_SIZE, floor(y/self.SQ_SIZE)*self.SQ_SIZE)
    
    #takes square girds coordiantes and returns indeces for cell array
    #returns two values
    def gridToArr(self, pos):
        x,y = pos 
        return int((x + self.HALF_LENGTH)/self.SQ_SIZE), int((y + self.HALF_LENGTH)/self.SQ_SIZE)