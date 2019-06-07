import sys
import os
from py4xs.hdf import h5exp,h5xs,lsh5
from py4xs.data2d import Data2d,Axes2dPlot,DataType
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import *#QMainWindow, QAction, QTextEdit, QFileDialog,\
#      QWidget, QPushButton, QMessageBox, QLineEdit,  QApplication,\
# 	  QSizePolicy
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import *#QIcon
from PyQt5.QtCore import *#pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import h5py

global dexp
global data

class NewSample(QDialog):
	def __init__(self,parent=None):
		super().__init__()
		
		self.setupUI()

	def setupUI(self):

		newfile_button = QPushButton("New Sample",self)
		close_button   = QPushButton("Close",self)
		mainLayout = QVBoxLayout()
		mainLayout.addWidget(newfile_button)
		mainLayout.addWidget(close_button)
		
		newfile_button.clicked.connect(self.button_clicked)
		close_button.clicked.connect(self.close)
		
		self.windows = list()
			
		self.setLayout(mainLayout)
		self.setWindowTitle("Input Window")
		self.show()
	
	@pyqtSlot()	
	def button_clicked(self):
		
		self.name = 'exp'
		self.openFileNameDialog()
		
		self.name = 'data'
		self.openFileNameDialog()
		new_window = Example(self,dexp=dexp,data=data)#need to append to self to show
		self.windows.append(new_window)
		new_window.show()

	def openFileNameDialog(self):
		options  = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		if self.name == 'exp':
			filename, _ = QFileDialog.getOpenFileName(self,"Exp File","",
						"All Files (*);;HDF Files (*.h5)", options = options)
			global dexp
			dexp = h5exp(filename)
		else:
			filename,_ = QFileDialog.getOpenFileName(self,"Data File","",
						"All Files (*);HDF Files (*.h5)", options = options)
			global data
			data = h5xs(filename,[dexp.detectors,dexp.qgrid])

class Example(QMainWindow):
	def __init__(self,parent=None,dexp=None,data=None):
		super().__init__()
		self.dexp   = dexp
		self.data   = data
		self.left   = 10
		self.top    = 10
		self.width  = 720
		self.height = 480
		self.title  = 'Load Scan Exp Img'
		self.fig_num = 0
		self.mask   = False
		self.log	= False
		self.vmax = None
		self.vmin = None
		self.initUI()
	
	def initUI(self):
		self.setGeometry(self.left, self.top, self.width, self.height)
		
		
		#create a buttion in the window
		#self.button = QPushButton('exp_h5',self)
		#self.button.move(20,80)
			
		# connect buttion to function on_click
		#self.button.clicked.connect(self.on_click)
		
		#create textbox for loading exp_para and data
		self.maxlbl = QLabel("max:",self)
		self.maxlbl.resize(30,20)
		self.maxlbl.move(520,70)
		self.setmax = QLineEdit(self)
		self.setmax.move(560,70)
		self.setmax.resize(60,20)
		self.setmax.textChanged[str].connect(self.set_max)
		
		self.minlbl = QLabel("min:",self)
		self.minlbl.resize(30,20)
		self.minlbl.move(520,100)
		self.setmin = QLineEdit(self)
		self.setmin.move(560,100)
		self.setmin.resize(60,20)
		self.setmin.textChanged[str].connect(self.set_min)
		
		self.top_layer_hdf = lsh5(self.data.fh5,top_only=True)
		#print(self.top_layer_hdf)
		self.prefix = self.top_layer_hdf[0]
		
		self.logb = QPushButton('logscale',self)
		self.logb.move(520,10)
		self.logb.resize(80,20)
		self.logb.setCheckable(True)
		self.logb.clicked[bool].connect(self.logCheck)
		self.maskb = QPushButton('mask',self)
		self.maskb.move(520,40)
		self.maskb.resize(80,20)
		self.maskb.setCheckable(True)
		self.maskb.clicked[bool].connect(self.maskCheck)
		
		#print(self.fig_num)
		if len(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"].shape) == 3:	
			scroller_num = self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW1_ext_image"].shape[0]
			self.SAXS_data  = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"]
							[self.fig_num],exp = self.dexp.detectors[0].exp_para)
			self.WAXS1_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW1_ext_image"]
							[self.fig_num],exp = self.dexp.detectors[1].exp_para)
			self.WAXS2_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW2_ext_image"]
							[self.fig_num],exp = self.dexp.detectors[2].exp_para)
		elif len(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"].shape) == 4:
			scroller_num = self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW1_ext_image"].shape[1]
			self.SAXS_data  = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"]
							[0,self.fig_num,],exp = self.dexp.detectors[0].exp_para)
			self.WAXS1_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW1_ext_image"]
							[0,self.fig_num],exp = self.dexp.detectors[1].exp_para)
			self.WAXS2_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW2_ext_image"]
							[0,self.fig_num],exp = self.dexp.detectors[2].exp_para)
		#self.m = PlotCanvas(self,SAXS=self.SAXS_data,log=self.log,mask=self.mask)
		self.sld = QSlider(Qt.Horizontal, self)
		self.sld.setMinimum(0)
		self.sld.setMaximum(scroller_num-1)
		
		self.sld.move(0,450)
		self.sld.resize(360,20)
		self.sld.valueChanged.connect(self.changeValue)
		self.plot()
		self.show()
	
	def plot(self):
		self.m = PlotCanvas(self,SAXS=self.SAXS_data,WAXS1=self.WAXS1_data,
							WAXS2=self.WAXS2_data,log=self.log,mask=self.mask,
							vmax=self.vmax,vmin=self.vmin,dexp=self.dexp)
		self.toolbar = NavigationToolbar(self.m,self)
		self.m.move(0,0)
		self.title_timestamps()	
		self.m.show()#PlotCanvas and NavigationBar are two separate widget		
		self.toolbar.show()#Thus, it's need two different show funtion
	
	def changeValue(self,value):
		self.fig_num = value	
		#print(self.fig_num)	
		#self.maskb.stateChanged.connect(self.maskCheck)
		#self.logb.stateChanged.connect(self.logCheck)
		if len(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"].shape) == 3:	
			self.SAXS_data  = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"]
							[self.fig_num],exp = self.dexp.detectors[0].exp_para)
			self.WAXS1_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW1_ext_image"]
							[self.fig_num],exp = self.dexp.detectors[1].exp_para)
			self.WAXS2_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW2_ext_image"]
							[self.fig_num],exp = self.dexp.detectors[2].exp_para)
		elif len(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"].shape) == 4:
			self.SAXS_data  = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pil1M_ext_image"]
							[0,self.fig_num,],exp = self.dexp.detectors[0].exp_para)
			self.WAXS1_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW1_ext_image"]
							[0,self.fig_num],exp = self.dexp.detectors[1].exp_para)
			self.WAXS2_data = Data2d(self.data.fh5[self.top_layer_hdf[0]+"/primary/data/pilW2_ext_image"]
							[0,self.fig_num],exp = self.dexp.detectors[2].exp_para)
		self.plot()
		
	def logCheck(self,pressed):
		if pressed:
			self.log = True
		else:
			self.log = False
		self.plot()
		
	def maskCheck(self,pressed):
		if pressed:
			self.mask = True
		else:
			self.mask = False
		self.plot()
	
	def set_max(self,value):
		if value == "":
			self.vmax = None
		else:
			self.vmax = float(value)
		#print(type(value),value)
		self.plot()
		
	def set_min(self,value):
		if value == "":
			self.vmin = None
		else:
			self.vmin = float(value)
		#print(type(value),value)
		self.plot()

	def title_timestamps(self):
		self.title = self.prefix + "_%d" %self.fig_num
		self.setWindowTitle(self.title)
		self.tableWidget = QTableWidget(self)
		self.tableWidget.setRowCount(7)
		self.tableWidget.setColumnCount(2)
		if "em1_sum_all_mean_value_monitor" in lsh5(self.data.fh5[self.prefix],top_only=True):
			em1_sum_all_mean_value = 1#data.fh5[self.prefix+\
			#"/em1_sum_all_mean_value_monitor/data/em1_sum_all_mean_value"][self.fig_num]
		else:	
			em1_sum_all_mean_value = self.data.fh5[self.prefix+\
			"/primary/timestamps/em1_sum_all_mean_value"][self.fig_num]
		if "em2_sum_all_mean_value_monitor" in lsh5(self.data.fh5[self.prefix],top_only=True):
			em2_sum_all_mean_value = 1#data.fh5[self.prefix+\
			#"/em2_sum_all_mean_value_monitor/data/em1_sum_all_mean_value"][self.fig_num]
		else:
			em2_sum_all_mean_value = self.data.fh5[self.prefix+\
			"/primary/timestamps/em2_sum_all_mean_value"][self.fig_num]
		pil1M_ext_image = 1.#data.fh5[self.prefix+\
		#"/primary/timestamps/pil1M_ext_image"][self.fig_num]
		pilW1_ext_image = 1.#data.fh5[self.prefix+\
		#"/primary/timestamps/pilW1_ext_image"][self.fig_num]
		pilW2_ext_image = 1.#data.fh5[self.prefix+\
		#"/primary/timestamps/pilW2_ext_image"][self.fig_num]
		ss2_x = 1.#data.fh5[self.prefix+\
		#"/primary/timestamps/ss2_x"][self.fig_num]
		ss2_y = 1.#data.fh5[self.prefix+\
		#"/primary/timestamps/ss2_y"][self.fig_num]
		self.tableWidget.setItem(0,0,QTableWidgetItem("em1"))	
		self.tableWidget.setItem(0,1,QTableWidgetItem(str(em1_sum_all_mean_value)))	
		self.tableWidget.setItem(1,0,QTableWidgetItem("em2"))	
		self.tableWidget.setItem(1,1,QTableWidgetItem(str(em2_sum_all_mean_value)))	
		self.tableWidget.setItem(2,0,QTableWidgetItem("pil1M"))	
		self.tableWidget.setItem(2,1,QTableWidgetItem(str(pil1M_ext_image)))	
		self.tableWidget.setItem(3,0,QTableWidgetItem("pilW1"))	
		self.tableWidget.setItem(3,1,QTableWidgetItem(str(pilW1_ext_image)))	
		self.tableWidget.setItem(4,0,QTableWidgetItem("pilW2"))	
		self.tableWidget.setItem(4,1,QTableWidgetItem(str(pilW2_ext_image)))	
		self.tableWidget.setItem(5,0,QTableWidgetItem("ss2_x"))	
		self.tableWidget.setItem(5,1,QTableWidgetItem(str(ss2_x)))	
		self.tableWidget.setItem(6,0,QTableWidgetItem("ss2_y"))	
		self.tableWidget.setItem(6,1,QTableWidgetItem(str(ss2_y)))	
		self.tableWidget.resize(280,240)
		self.tableWidget.move(520,150)


class PlotCanvas(FigureCanvas):
	def __init__(self, parent=None, width=5, height=4, dpi=100, 
				SAXS=None,WAXS1=None,WAXS2=None,
				log=False,mask=False,vmax=None,vmin=None,dexp=None):
		#super().__init__()
		self.fig = Figure(figsize=(width,height),dpi=dpi)
		self.log = log
		self.mask_check = mask
		self.vmax = vmax
		self.vmin = vmin
		self.dexp =dexp
		FigureCanvas.__init__(self,self.fig)
		self.setParent(parent)
		FigureCanvas.setSizePolicy(self,
						QSizePolicy.Expanding,
						QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)
		#self.toolbar = NavigationToolbar(FigureCanvas(self.fig),self)
		
		self.axes = self.fig.add_subplot(132)
		self.img = SAXS
		self.exp  = self.dexp.detectors[0].exp_para
		self.mask = self.dexp.detectors[0].exp_para.mask
		self.plot()
		self.axes = self.fig.add_subplot(133)
		self.img = WAXS1
		self.exp  = self.dexp.detectors[1].exp_para
		self.mask = self.dexp.detectors[1].exp_para.mask
		self.plot()
		self.axes = self.fig.add_subplot(131)
		self.img = WAXS2
		self.exp  = self.dexp.detectors[2].exp_para
		self.mask = self.dexp.detectors[2].exp_para.mask
		self.plot()
	
	def plot(self):
		im = self.img
		ax = self.axes
		paxr = Axes2dPlot(ax, im.data, exp = self.exp)
		if self.mask_check:
			paxr.plot(log=self.log,mask= self.mask)
		else:
			paxr.plot(log=self.log)
		
		
		if self.vmin != None and self.vmax != None:
			if self.vmin >= self.vmax:
				pass
			else:
				paxr.img.set_clim(self.vmin,self.vmax)
		elif self.vmin != None and self.vmax == None:
			if np.nanmax(im.data.d) > self.min:
				paxr.img.set_clim(self.vmin,np.nanmax(im.data.d))
			else:
				pass
		elif self.vmin == None and self.vmax != None:
			if self.vmax < 2:
				pass
			else:
				paxr.img.set_clim(1,self.vmax)
		else:
			pass
	
		#paxr.img.set_clim(100,1000)
		#paxr.plot(mask=dexp.detectors[0].exp_para.mask)
		self.draw()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex  = NewSample()
	ex.show()
	sys.exit(app.exec_())
