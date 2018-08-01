'''
Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.

Copyright 2016. UChicago Argonne, LLC. This software was produced
under U.S. Government contract DE-AC02-06CH11357 for Argonne National
Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
U.S. Department of Energy. The U.S. Government has rights to use,
reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should
be clearly marked, so as not to confuse it with the version available
from ANL.

Additionally, redistribution and use in source and binary forms, with
or without modification, are permitted provided that the following
conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in
      the documentation and/or other materials provided with the
      distribution.

    * Neither the name of UChicago Argonne, LLC, Argonne National
      Laboratory, ANL, the U.S. Government, nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

from PyQt5 import QtCore, QtWidgets
from widgets.histogram_widget import HistogramWidget
import pyqtgraph

class ImageAndHistogramWidget(QtWidgets.QWidget):
    def __init__(self):
        super(ImageAndHistogramWidget, self).__init__()

        self.initUI()

    def initUI(self):
        hb3 = QtWidgets.QHBoxLayout()
        self.file_name_title = QtWidgets.QLabel("_")
        lbl1 = QtWidgets.QLabel("x pos")
        self.lbl2 = QtWidgets.QLabel("")
        lbl3 = QtWidgets.QLabel("y pos")
        self.lbl4 = QtWidgets.QLabel("")
        btn1 = QtWidgets.QPushButton("position")
        hb3.addWidget(lbl1)
        hb3.addWidget(self.lbl2)
        hb3.addWidget(lbl3)
        hb3.addWidget(self.lbl4)
        hb3.addWidget(btn1)

        btn1.clicked.connect(self.updatePanel)

        hb2 = QtWidgets.QHBoxLayout()
        hb1 = QtWidgets.QHBoxLayout()
        vb1 = QtWidgets.QVBoxLayout()
        self.view = HistogramWidget()
        self.sld = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.lcd = QtWidgets.QLCDNumber(self)
        self.hist = pyqtgraph.HistogramLUTWidget()
        self.hist.setImageItem(self.view.projView)

        hb2.addWidget(self.lcd)
        hb2.addWidget(self.sld)
        vb1.addWidget(self.file_name_title)
        vb1.addLayout(hb3)
        vb1.addWidget(self.view)
        vb1.addLayout(hb2)
        hb1.addLayout(vb1)
        hb1.addWidget(self.hist, 10)
        self.setLayout(hb1)

    def keyPressEvent(self, ev):
        if ev.key() == QtCore.Qt.Key_N:
            self.sld.setValue(self.sld.value + 1)

    def updatePanel(self):
        self.lbl2.setText(str(self.view.projView.iniX))
        self.lbl4.setText(str(self.view.projView.iniY))
