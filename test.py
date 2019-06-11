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
		self.width  = 1560
		self.height = 680
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
		
		self.top_layer_hdf = lsh5(self.data.fh5,top_only=True)
		#print(self.top_layer_hdf)
		self.prefix = self.top_layer_hdf[0]
		
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
		self.title = self.prefix + "_%d" %self.fig_num
		self.setWindowTitle(self.title)
		self.title_timestamps()	
		self.plotSAXS()
		self.plotWAXS2()
		self.plotWAXS1()
		self.show()
	
	def plotSAXS(self):
		self.maxlbl = QLabel("max:",self)
		self.maxlbl.resize(30,20)
		self.maxlbl.move(930,70)
		self.setsmax = QLineEdit(self)
		self.setsmax.move(970,70)
		self.setsmax.resize(60,20)
		self.setsmax.textChanged[str].connect(self.SAXSset_max)
		
		self.minlbl = QLabel("min:",self)
		self.minlbl.resize(30,20)
		self.minlbl.move(930,100)
		self.setsmin = QLineEdit(self)
		self.setsmin.move(970,100)
		self.setsmin.resize(60,20)
		self.setsmin.textChanged[str].connect(self.SAXSset_min)
		
		self.slogb = QPushButton('logscale',self)
		self.slogb.move(930,10)
		self.slogb.resize(80,20)
		self.slogb.setCheckable(True)
		self.slogb.clicked[bool].connect(self.SAXSlogCheck)
		self.smaskb = QPushButton('mask',self)
		self.smaskb.move(930,40)
		self.smaskb.resize(80,20)
		self.smaskb.setCheckable(True)
		self.smaskb.clicked[bool].connect(self.SAXSmaskCheck)
		
		self.m = PlotCanvas(self,img=self.SAXS_data,img_type = 'SAXS',
							log=self.log,mask=self.mask,
							vmax=self.vmax,vmin=self.vmin,dexp=self.dexp)
		self.toolbar = NavigationToolbar(self.m,self)
		self.m.move(520,0)
		#self.title_timestamps()	
		self.m.show()#PlotCanvas and NavigationBar are two separate widget		
		self.toolbar.resize(360,30)
		self.toolbar.move(520,300)
		self.toolbar.show()#Thus, it's need two different show funtion
	
	def plotWAXS2(self):
		self.maxlbl = QLabel("max:",self)
		self.maxlbl.resize(30,20)
		self.maxlbl.move(410,70)
		self.setw2max = QLineEdit(self)
		self.setw2max.move(450,70)
		self.setw2max.resize(60,20)
		self.setw2max.textChanged[str].connect(self.WAXS2set_max)
		
		self.minlbl = QLabel("min:",self)
		self.minlbl.resize(30,20)
		self.minlbl.move(410,100)
		self.setw2min = QLineEdit(self)
		self.setw2min.move(450,100)
		self.setw2min.resize(60,20)
		self.setw2min.textChanged[str].connect(self.WAXS2set_min)
		
		self.w2logb = QPushButton('logscale',self)
		self.w2logb.move(410,10)
		self.w2logb.resize(80,20)
		self.w2logb.setCheckable(True)
		self.w2logb.clicked[bool].connect(self.WAXS2logCheck)
		self.w2maskb = QPushButton('mask',self)
		self.w2maskb.move(410,40)
		self.w2maskb.resize(80,20)
		self.w2maskb.setCheckable(True)
		self.w2maskb.clicked[bool].connect(self.WAXS2maskCheck)
		
		self.m = PlotCanvas(self,img=self.WAXS2_data,img_type = 'WAXS2',
							log=self.log,mask=self.mask,
							vmax=self.vmax,vmin=self.vmin,dexp=self.dexp)
		self.toolbar = NavigationToolbar(self.m,self)
		self.m.move(0,0)
		#self.title_timestamps()	
		self.m.show()#PlotCanvas and NavigationBar are two separate widget		
		self.toolbar.resize(360,30)
		self.toolbar.move(0,300)
		self.toolbar.show()#Thus, it's need two different show funtion
	
	def plotWAXS1(self):
		self.maxlbl = QLabel("max:",self)
		self.maxlbl.resize(30,20)
		self.maxlbl.move(1450,70)
		self.setw2max = QLineEdit(self)
		self.setw2max.move(1490,70)
		self.setw2max.resize(60,20)
		self.setw2max.textChanged[str].connect(self.WAXS1set_max)
		
		self.minlbl = QLabel("min:",self)
		self.minlbl.resize(30,20)
		self.minlbl.move(1450,100)
		self.setw2min = QLineEdit(self)
		self.setw2min.move(1490,100)
		self.setw2min.resize(60,20)
		self.setw2min.textChanged[str].connect(self.WAXS1set_min)
		
		self.w2logb = QPushButton('logscale',self)
		self.w2logb.move(1450,10)
		self.w2logb.resize(80,20)
		self.w2logb.setCheckable(True)
		self.w2logb.clicked[bool].connect(self.WAXS1logCheck)
		self.w2maskb = QPushButton('mask',self)
		self.w2maskb.move(1450,40)
		self.w2maskb.resize(80,20)
		self.w2maskb.setCheckable(True)
		self.w2maskb.clicked[bool].connect(self.WAXS1maskCheck)
		
		self.m = PlotCanvas(self,img=self.WAXS1_data,img_type = 'WAXS1',
							log=self.log,mask=self.mask,
							vmax=self.vmax,vmin=self.vmin,dexp=self.dexp)
		self.toolbar = NavigationToolbar(self.m,self)
		self.m.move(1040,0)
		self.title_timestamps()	
		self.m.show()#PlotCanvas and NavigationBar are two separate widget		
		self.toolbar.resize(360,30)
		self.toolbar.move(1040,300)
		self.toolbar.show()#Thus, it's need two different show funtion
	
	def changeValue(self,value):
		self.fig_num = value	
		self.title = self.prefix + "_%d" %self.fig_num
		self.setWindowTitle(self.title)
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
		self.plotSAXS()
		self.plotWAXS2()
		self.plotWAXS1()
		self.title_timestamps()	
		
	def SAXSlogCheck(self,pressed):
		if pressed:
			self.log = True
		else:
			self.log = False
		self.plotSAXS()
		
	def SAXSmaskCheck(self,pressed):
		if pressed:
			self.mask = True
		else:
			self.mask = False
		self.plotSAXS()
	
	def SAXSset_max(self,value):
		if value == "":
			self.vmax = None
		else:
			self.vmax = float(value)
		#print(type(value),value)
		self.plotSAXS()
		
	def SAXSset_min(self,value):
		if value == "":
			self.vmin = None
		else:
			self.vmin = float(value)
		#print(type(value),value)
		self.plotSAXS()

	def WAXS2logCheck(self,pressed):
		if pressed:
			self.log = True
		else:
			self.log = False
		self.plotWAXS2()
		
	def WAXS2maskCheck(self,pressed):
		if pressed:
			self.mask = True
		else:
			self.mask = False
		self.plotWAXS2()
	
	def WAXS2set_max(self,value):
		if value == "":
			self.vmax = None
		else:
			self.vmax = float(value)
		#print(type(value),value)
		self.plotWAXS2()
		
	def WAXS2set_min(self,value):
		if value == "":
			self.vmin = None
		else:
			self.vmin = float(value)
		#print(type(value),value)
		self.plotWAXS2()
	
	def WAXS1logCheck(self,pressed):
		if pressed:
			self.log = True
		else:
			self.log = False
		self.plotWAXS1()
		
	def WAXS1maskCheck(self,pressed):
		if pressed:
			self.mask = True
		else:
			self.mask = False
		self.plotWAXS1()
	
	def WAXS1set_max(self,value):
		if value == "":
			self.vmax = None
		else:
			self.vmax = float(value)
		#print(type(value),value)
		self.plotWAXS1()
		
	def WAXS1set_min(self,value):
		if value == "":
			self.vmin = None
		else:
			self.vmin = float(value)
		#print(type(value),value)
		self.plotWAXS1()
	
	def title_timestamps(self):
		self.tableWidget = QTableWidget(self)
		self.tableWidget.setRowCount(7)
		self.tableWidget.setColumnCount(2)
		em1_sum_all_mean_value = "NaN"
		em2_sum_all_mean_value = "NaN"
		pil1M_ext_image = "NaN"
		pilW1_ext_image = "NaN"
		pilW2_ext_image = "NaN"
		ss2_x = "NaN"
		ss2_y = "NaN"
		
		if ("em1_sum_all_mean_value" in self.data.fh5[self.prefix+"/primary/timestamps/"]): 
			if (self.fig_num < self.data.fh5[self.prefix+"/primary/timestamps/em1_sum_all_mean_value"].shape[0]):
				em1_sum_all_mean_value = self.data.fh5[self.prefix+\
				"/primary/timestamps/em1_sum_all_mean_value"][self.fig_num]
		if ("em2_sum_all_mean_value" in self.data.fh5[self.prefix+"/primary/timestamps/"]):
			if (self.fig_num < self.data.fh5[self.prefix+"/primary/timestamps/em2_sum_all_mean_value"].shape[0]):
				em2_sum_all_mean_value = self.data.fh5[self.prefix+\
				"/primary/timestamps/em2_sum_all_mean_value"][self.fig_num]
		if ("pil1M_ext_image" in self.data.fh5[self.prefix+"/primary/timestamps/"]):
			if (self.fig_num < self.data.fh5[self.prefix+"/primary/timestamps/pil1M_ext_image"].shape[0]):
				pil1M_ext_image = self.data.fh5[self.prefix+\
				"/primary/timestamps/pil1M_ext_image"][self.fig_num]
		if ("pilW1_ext_image" in self.data.fh5[self.prefix+"/primary/timestamps/"]):
			if (self.fig_num < self.data.fh5[self.prefix+"/primary/timestamps/pilW1_ext_image"].shape[0]):
				pilW1_ext_image = self.data.fh5[self.prefix+\
				"/primary/timestamps/pilW1_ext_image"][self.fig_num]
		if ("pilW2_ext_image" in self.data.fh5[self.prefix+"/primary/timestamps/"]):
			if (self.fig_num < self.data.fh5[self.prefix+"/primary/timestamps/pilW2_ext_image"].shape[0]):
				pilW2_ext_image = self.data.fh5[self.prefix+\
				"/primary/timestamps/pilW2_ext_image"][self.fig_num]
		if ("ss2_x" in self.data.fh5[self.prefix+"/primary/timestamps/"]):
			if (self.fig_num < self.data.fh5[self.prefix+"/primary/timestamps/ss2_x"].shape[0]):
				ss2_x = self.data.fh5[self.prefix+\
				"/primary/timestamps/ss2_x"][self.fig_num]
		if ("ss2_y" in self.data.fh5[self.prefix+"/primary/timestamps/"]):
			if (self.fig_num < self.data.fh5[self.prefix+"/primary/timestamps/ss2_y"].shape[0]):
				ss2_y = self.data.fh5[self.prefix+\
				"/primary/timestamps/ss2_y"][self.fig_num]
		
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
		self.tableWidget.move(500,350)


class PlotCanvas(FigureCanvas):
	def __init__(self, parent=None, width=4, height=3, dpi=100, 
				img=None,img_type=None,
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
		
		self.axes = self.fig.add_subplot(111)
		self.img = img
		if img_type == 'SAXS':
			self.exp  = self.dexp.detectors[0].exp_para
			self.mask = self.dexp.detectors[0].exp_para.mask
		elif img_type == 'WAXS1':
			self.exp  = self.dexp.detectors[1].exp_para
			self.mask = self.dexp.detectors[1].exp_para.mask
		elif img_type == 'WAXS2':
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
