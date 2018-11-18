# -*- coding: utf-8 -*-
"""
Created on Thu Jun 08 12:42:25 2017

from kivy version 1.10.0
https://github.com/kivy/kivy/blob/master/kivy/uix/scatter.py
changed the default scatter touch function for mouse imput:
1. drag with the right mouse button 
2. zoom with the mousewheel
changes to the orginal marked with 'KS:'

kivy is liscensed under MIT:
Copyright (c) 2010-2017 Kivy Team and other contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from math import radians
from kivy.vector import Vector
from kivy.uix.scatter import Scatter
from kivy.graphics.transformation import Matrix


def on_touch_down(self, touch):
    x, y = touch.x, touch.y

    # if the touch isnt on the widget we do nothing
    if not self.do_collide_after_children:
        if not self.collide_point(x, y):
            return False

    # let the child widgets handle the event if they want
    touch.push()
    touch.apply_transform_2d(self.to_local)
    if super(Scatter, self).on_touch_down(touch):
        # ensure children don't have to do it themselves
        if 'multitouch_sim' in touch.profile:
            touch.multitouch_sim = True
        touch.pop()
        self._bring_to_front(touch)
        return True
    touch.pop()

    # if our child didn't do anything, and if we don't have any active
    # interaction control, then don't accept the touch.
    if not self.do_translation_x and \
            not self.do_translation_y and \
            not self.do_rotation and \
            not self.do_scale:
        return False

    if self.do_collide_after_children:
        if not self.collide_point(x, y):
            return False
    
    '''KS: call transform method on mousewheel
    the rest is copied from on_touch_move()'''
    if touch.button=="scrolldown" or touch.button=="scrollup":
        if self.transform_with_touch(touch):
            self.dispatch('on_transform_with_touch', touch)
        self._last_touch_pos[touch] = touch.pos
        

    if 'multitouch_sim' in touch.profile:
        touch.multitouch_sim = True
    # grab the touch so we get all it later move events for sure
    self._bring_to_front(touch)
    touch.grab(self)
    self._touches.append(touch)
    self._last_touch_pos[touch] = touch.pos

    return True

def on_touch_move(self, touch):
    x, y = touch.x, touch.y
    # let the child widgets handle the event if they want
    if self.collide_point(x, y) and not touch.grab_current == self: 
        touch.push()
        touch.apply_transform_2d(self.to_local)
        if super(Scatter, self).on_touch_move(touch):
            touch.pop()
            return True
        touch.pop()

    # rotate/scale/translate
    '''KS: only move on right click'''
    if touch in self._touches and touch.grab_current == self and touch.button=="right": 
        if self.transform_with_touch(touch):
            self.dispatch('on_transform_with_touch', touch)
        self._last_touch_pos[touch] = touch.pos

    # stop propagating if its within our bounds
    if self.collide_point(x, y):
        return True
        
def transform_with_touch(self, touch):
      # just do a simple one finger drag
      changed = False
      if len(self._touches) == self.translation_touches:
          # _last_touch_pos has last pos in correct parent space,
          # just like incoming touch
          dx = (touch.x - self._last_touch_pos[touch][0]) \
              * self.do_translation_x
          dy = (touch.y - self._last_touch_pos[touch][1]) \
              * self.do_translation_y
          dx = dx / self.translation_touches
          dy = dy / self.translation_touches
          self.apply_transform(Matrix().translate(dx, dy, 0))
          changed = True

      #if len(self._touches) == 1:
      '''KS: if this was right button drag we are done'''
      if touch.button=="right":
          return changed

      # we have more than one touch... list of last known pos
      #points = [Vector(self._last_touch_pos[t]) for t in self._touches
      #          if t is not touch]
      # add current touch last
      #points.append(Vector(touch.pos))

      # we only want to transform if the touch is part of the two touches
      # farthest apart! So first we find anchor, the point to transform
      # around as another touch farthest away from current touch's pos
      #anchor = max(points[:-1], key=lambda p: p.distance(touch.pos))
      
      '''KS: changing anchor to cursor location'''
      anchor = Vector(touch.pos)

      # now we find the touch farthest away from anchor, if its not the
      # same as touch. Touch is not one of the two touches used to transform
      #farthest = max(points, key=anchor.distance)

      '''
      farthest = (touch.x, touch.y)
      if farthest is not points[-1]:
          return changed
      '''
      # ok, so we have touch, and anchor, so we can actually compute the
      # transformation
      '''KS: Scale by a constant'''
      #old_line = Vector(*touch.ppos) - anchor
      #new_line = Vector(*touch.pos) - anchor
      old_line = anchor
      new_line = Vector(touch.pos[0]+10, touch.pos[1]+10) if touch.button=="scrolldown" else Vector(touch.pos[0]-10, touch.pos[1]-10) 
      
      if not old_line.length():   # div by zero
          return changed

      angle = radians(new_line.angle(old_line)) * self.do_rotation
      self.apply_transform(Matrix().rotate(angle, 0, 0, 1), anchor=anchor)

      if self.do_scale:
          scale = new_line.length() / old_line.length()
          new_scale = scale * self.scale
          if new_scale < self.scale_min:
              scale = self.scale_min / self.scale
          elif new_scale > self.scale_max:
              scale = self.scale_max / self.scale
          self.apply_transform(Matrix().scale(scale, scale, scale),
                               anchor=anchor)
          changed = True
      return changed