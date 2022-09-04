# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 10:11:54 2022

@author: Fujitsu-A556
"""

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
import pyaudio
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout,
                             QLabel, QPushButton, QSizePolicy, QFileDialog)


class AnalizadorApp(QWidget):
    def __init__(self):
        super().__init__(windowTitle='Analizador de espectro')
        
        
        fuente = self.font()    # obtiene fuente
        fuente.setPointSize(14) # la agranda
        self.setFont(fuente)    # la seteeaaa
        
        self.RATE = 44100
        self.CHUNK = 1024   # BUFFER SIZE
        self.CHANNELS = 1
        self.FORMAT = pyaudio.paInt16
        
        # self.p = pyaudio.PyAudio()
        
        self.fig = Figure(dpi=100)
        axes = self.fig.subplots(2)
        self.linea_t = axes[0].plot([],[], 'b', linewidth=1.5)[0]
        self.linea_f = axes[1].semilogx([],[], 'r', linewidth=2)[0]
        axes[0].grid()
        axes[0].set_xlabel('Tiempo (s)')
        axes[0].set_ylabel('Amplitud')
        axes[0].set_ylim([-1, 1])
        axes[0].set_xlim([0, self.CHUNK/self.RATE])
        axes[1].grid()
        axes[1].set_xlabel('Frecuencia (Hz)')
        axes[1].set_ylabel('Amplitud')
        axes[1].set_ylim([0, 1])
        axes[1].set_xlim([20, 20000])
        self.fig.set_tight_layout(True)  # Para q no se pisen los ejes
        self.canvas = FigureCanvas(self.fig)
        
        start = QPushButton('Start')
        stop = QPushButton('Stop')
        save = QPushButton('Save')
        
        caja = QGridLayout(self)
        caja.addWidget(self.canvas, 0, 0, 6, 3)
        caja.addWidget(start, 0, 3, 2, 1)
        caja.addWidget(save, 2, 3, 2, 1)
        caja.addWidget(stop, 4, 3, 2, 1)
        
        start.clicked.connect(self.start)
        stop.clicked.connect(self.stop)
        save.clicked.connect(self.save)
        
    def start(self):
        self.analizando = True
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(rate=self.RATE,
                        channels=self.CHANNELS,
                        format=self.FORMAT,
                        input=True,     # enables system input
                        output=False,   # system output not required
                        frames_per_buffer=self.CHUNK)
        
        t = np.arange(0, self.CHUNK)/self.RATE
        self.linea_t.set_xdata(t)
        
        freq = np.fft.rfftfreq(self.CHUNK, 1/self.RATE)
        self.linea_f.set_xdata(freq)
        
        while self.analizando:
            datos = self.stream.read(self.CHUNK)
            decode = np.frombuffer(datos, dtype='int16') / 32768
        
            self.linea_t.set_ydata(decode)
            
            espectro = np.abs(np.fft.rfft(decode)) / (self.CHUNK//2)
            
            self.linea_f.set_ydata(2*espectro)
            
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        
        self.stream.close()
        self.p.terminate()
        

    def save(self):
        ruta = QFileDialog.getSaveFileName(directory='figure.png', 
                                           filter='Portable Network Graphics (*png)')[0]
        if ruta != '':
            self.fig.savefig(ruta, format='png')
    def stop(self):
        self.analizando = False


app = QApplication([])
ventana = AnalizadorApp()
ventana.show()
app.exec_()
