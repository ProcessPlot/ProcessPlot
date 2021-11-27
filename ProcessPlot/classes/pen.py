"""
Copyright (c) 2021 Adam Solchenberger asolchenberger@gmail.com, Jason Engman engmanj@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import logging
import numpy as np

class Pen(object):
  __log = logging.getLogger("ProcessPlot.classes.Pen")
  
  def __init__(self, chart, pen_id, point_id=None) -> None:
    super().__init__()
    self.chart = chart
    self.app = chart.app
    self.id = pen_id
    self.point_id = point_id
    self.buffer = np.ndarray(shape=(2,0xFFFFF), dtype=float)
    self.color = (1.0,1.0,1.0,1.0)
    self.width = 1
    #self.__log.debug(f"Pen {self.id} created on chart {self.chart} for point {self.point_id}")
