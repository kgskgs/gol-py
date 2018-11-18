# GOL
Game of life built with python and the kivy library

A simple user interface for [Conway's Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life). It explores different ways to achieve functionallity with the library: trough the .kv files, class inheritance, and (admittedly not a good idea) hacking into the source code of one class and substituting the altered functions

## Rquirements
* Python 2.7
* [Kivy](https://kivy.org/#home)

There is a windows binary packaged with all dependencies included (created mainly to try and build the app with pyinstaller)

## Notes
* more than 2000 alive cells will cause lag at faster speeds
* because of that the universe is bounded to 5000x5000 cells
* if you acutally want a real application for running cellular automata use [this](http://golly.sourceforge.net/)
* presented as coursework for the course "Programming with python" at New Bulgarian University
* detailed description of the app is avialable in bulgarian, which could also serve as an introduction to kivy

## License
MIT 
