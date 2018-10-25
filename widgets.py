
from PySide.QtCore import *
from PySide.QtGui import *
import os
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import xml.etree.ElementTree as ET
from operator import itemgetter




class userTV(QTreeWidget):
		def __init__(self, courseList, dirLabel, parent = None):
			QTreeWidget.__init__(self, parent)
			self.setAcceptDrops(True)
			self.courseList = courseList
			self.dirLabel = dirLabel
			self.xmlFile = ""
			self.markingDirectory = "" 
			self.setMinimumSize(800,600)
			self.setSelectionBehavior(QAbstractItemView.SelectRows)
			self.setSelectionMode(QAbstractItemView.MultiSelection)
			# self.model = QStandardItemModel()
			self.setColumnCount(5)
			self.totalHeaders = ['ID','Forename', 'Surname', 'Email', 'Course']
			self.activeHeaders = []
			self.setHeaderLabels(self.totalHeaders)
			# self.setHeaderLabels(["Student Data Setup"])
			self.headerMapping = {'ID':'id', 'Forename':'forename', 'Surname':'surname', 'Email':'email', 'Course':'course'}
			self.showHeaders = {'ID':True, 'Forename':True, 'Surname':True, 'Email':True, 'Course':True}
			# self.setModel(self.model)
			self.setUniformRowHeights(True)
			self.userList = []
			self.moduleCode = ""
			self.moduleTitle = ""
			# self.reSortList('surname')
			# self.reSortList('forename')
			self.setContextMenuPolicy(Qt.CustomContextMenu) #context menu for user data
			self.customContextMenuRequested.connect(self.userMenu)
			self.header().setContextMenuPolicy(Qt.CustomContextMenu) #context menu for headers
			self.header().customContextMenuRequested.connect(self.headerMenu)
			# self.populateTreeList()
			# userTWItem = QTreeWidgetItem(self,["Please Drag and Drop Module File here...."])    #Initialise with drag and drog instructions
			# self.addTopLevelItem(userTWItem)

		def getUserList(self):
			return self.userList

		def getModuleCode(self):
			return self.moduleCode

		def getModuleTitle(self):
			return self.moduleTitle

		def getMarkingDirectory(self):
			return self.markingDirectory

		def getCourseShortName(self,longName):
		    for c in self.courseList:
		        if longName == c["name"]: return c["shortName"]
		    return "No Course Found"

		def getStudents(self):  
		    tree = ET.parse(self.xmlFile)
		    root = tree.getroot()  
		    self.moduleCode = root.get('Textbox4') #Grab the module code when the file is Dropped
		    self.moduleTitle = root.get('Textbox12') #Grab the module code when the file is Dropped
		    studentList =[]
		    for student in root[0][0]:
		        studentDetail = {'id':student.get('BoltonID'), 
		                        'forename':student.get('forename1'), 
		                        'surname':student.get('surname'), 
		                        'email':student.get('contactEMail'), 
		                        'occurence':student.get('Occurrence'),
		                        'course': self.getCourseShortName(student.get('courseName')), 
		                        'attendence':'A', 'lateness':0}
		        studentList.append(studentDetail)
		    self.userList = studentList

		def filterbyCourse(self,courseList):
			self.getStudents() #First of all grab all the students to update userList
			newUserList = []
			for u in self.userList:
				for c in courseList: 
					if c == u['course']: newUserList.append(u)
			self.userList = newUserList
			self.populateTreeList()

		def collectActiveHeaders(self): 
			"""Collect all the visible columns together"""
			headers = []
			for header in self.totalHeaders:
				if self.showHeaders[header]: headers.append(header)
			return headers

		def populateTreeList(self):
			self.clear()
			self.activeHeaders = self.collectActiveHeaders()
			self.setHeaderLabels(self.activeHeaders)
			for user in self.userList:
				userData = []
				for header in self.activeHeaders: 
					userData.append(user[self.headerMapping[header]])
				userTWItem = QTreeWidgetItem(self,userData)
				# userTWItem.setSizeHint(userTWItem.sizeHint())
				self.addTopLevelItem(userTWItem)

		def reSortList(self, userKey):
			self.clear()
			self.userList = sorted(self.userList, key=itemgetter(userKey))
			self.populateTreeList()

		def userMenu(self, position):
			menu = QMenu()
			menu.addAction(self.tr("Copy Email"))
			menu.addAction(self.tr("Sort"))
			menu.exec_(self.viewport().mapToGlobal(position))

		def headerMenu(self, position):
			menu = QMenu()
			col = self.columnAt(position.x())
			print (col)
			headerText = self.headerItem().text(col)
			# sort = menu.addAction(self.tr("Sort by " + headerText))
			sortText =  ("Sort by " +  str(headerText))
			sort = menu.addAction(self.tr(sortText))
			hide = menu.addAction(self.tr("Hide"))
			menu.addSeparator()
			# badger = menu.addAction(self.tr("badger"))  # Add in the show column list here
			action = menu.exec_(self.viewport().mapToGlobal(position))
			if action == sort: 
				self.reSortList(self.headerMapping[headerText])
				print ("map order" + str(self.headerMapping[headerText]))
			if action == hide: #Turn off the showheader so populateTreeList regenerates the table without that header
				self.showHeaders[headerText] = False
				self.activeHeaders = self.collectActiveHeaders()
				self.setColumnCount(len(self.activeHeaders))
				self.setHeaderLabels(self.activeHeaders)
				self.populateTreeList()

		def loadModule(self, fileName):
			self.xmlFile = fileName
			self.getStudents()
			self.populateTreeList()
			self.dirLabel.setText(" - " + self.moduleTitle)
			self.dirLabel.repaint()

		# The following three methods set up dragging and dropping for the app
		def dragEnterEvent(self, e):
		    if e.mimeData().hasUrls:
		        e.accept()
		    else:
		        e.ignore()

		def dragMoveEvent(self, e):
		    if e.mimeData().hasUrls:
		        e.accept()
		    else:
		        e.ignore()

		def dropEvent(self, e):
		    """
		    Drop files directly onto the widget
		    File locations are stored in fname
		    :param e:
		    :return:
		    """
		    if e.mimeData().hasUrls:
		        e.setDropAction(Qt.CopyAction)
		        e.accept()
		        print "Detected Drop"
		        # Workaround for OSx dragging and dropping
		        for url in e.mimeData().urls():
		                fname = str(url.toLocalFile())

		        self.xmlFile = fname
		        self.markingDirectory = os.path.dirname(self.xmlFile)
		        # print(self.xmlFile)
		        # print(self.markingDirectory)
		        self.dirLabel.setText(self.moduleTitle)
		        # print("Dir Text: " + self.dirLabel.text())
		        self.dirLabel.repaint()
		        print "Got called"
		        # self.setColumnCount(5)
		        self.getStudents()
		        self.populateTreeList()
		        # print(self.xmlFile)
		        # print(self.markingDirectory)
		        # print("Dir Text: " + self.dirLabel.text())		    else:
		    	print "ignored"
		        e.ignore()

