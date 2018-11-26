
from PySide.QtCore import *
from PySide.QtGui import *
import os
import webbrowser
import win32com.client as win32   
import pyperclip
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import xml.etree.ElementTree as ET
from operator import itemgetter




class userTV(QTreeWidget):
		def __init__(self, courseList, dirLabel, rcMenuData,parent = None):
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

			self.rcMenuData = rcMenuData
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
			#Make sure item under selection mouse is selected
			item = self.itemAt(position)
			item.setSelected(True)
			menu = QMenu()

			#Emailing Menu Functionality
			copyEmails = menu.addAction("Copy Email Addresses")
			copyEmails.triggered.connect(self.copyEmailsToClipboard)
			generalEmail = menu.addAction("Send General Email")
			generalEmail.triggered.connect(self.sendGeneralEmail)
			copyEmail = menu.addMenu(self.tr("Send Email"))
			# for email in module
			for m in self.rcMenuData["emails"]:
				emailAction = copyEmail.addAction(str(m["name"]))
				emailAction.triggered[()].connect(lambda item=m["name"]: self.sendContentEmail(item))

			if (len(self.selectedItems()) == 1): #Copying ID numbers only makes sense for an individual
				menu.addSeparator()
				copyStudentID = menu.addAction(self.tr("Copy Student ID"))
				copyStudentID.triggered[()].connect(lambda item=position: self.copyIDToClipboard(item))
				copyStudentID = menu.addMenu(self.tr("Open Student ID"))
				for m in self.rcMenuData["studentIDLinks"]:
					linkData = {"position":position, "text":m["name"]}
					IDAction = copyStudentID.addAction(str(m["name"]))
					IDAction.triggered[()].connect(lambda item=linkData: self.openIDPage(item))
			menu.addSeparator()
			copStudentData = menu.addAction(str("Copy Student Information"))
			copStudentData.triggered.connect(self.copyStudentInfo)
			sendAdminID = menu.addAction(str("Send to " + self.rcMenuData["administratorContact"]["name"]))
			sendAdminID.triggered.connect(self.emailToAdmin)
			menu.addSeparator()
			clearSelection = menu.addAction(self.tr("Clear Selection"))
			clearSelection.triggered.connect(self.clearSelection)
			menu.exec_(self.viewport().mapToGlobal(position))

		def getColumnNumber(self, headerLabel):
			header = self.headerItem()
			for i in range(0,header.columnCount()):
				# print(header.text(i) + " " + headerLabel)
				if header.text(i) == headerLabel:
					return i

		def getEmailStringList(self):
			#cycle through selected items and add emails strings together
			self.getColumnNumber("Email")
			emailString = ""
			for item in self.selectedItems():
				emailString = emailString + item.text(self.getColumnNumber("Email")) + "; "  #This is a hardcoded reference to the email column
			# print("Email String is: " + emailString)
			return emailString

		def copyEmailsToClipboard(self):
			pyperclip.copy(self.getEmailStringList())

		def emailer(self, text, subject, recipient):
			outlook = win32.Dispatch('outlook.application')
			mail = outlook.CreateItem(0)
			mail.To = recipient
			mail.Subject = subject
			mail.HtmlBody = text
			mail.Display(True)

		def sendGeneralEmail(self):
			self.emailer("", "", self.getEmailStringList())

		def sendContentEmail(self, dictText):
			emailList = self.getEmailStringList()
			# print(str(self.rcMenuData["emails"]))
			for email in self.rcMenuData["emails"]:
				if email["name"] == dictText:
					self.emailer(email["body"], email["subject"], self.getEmailStringList())

		def copyIDToClipboard(self, position):
			item = self.itemAt(position)
			IDNo = str(item.text(self.getColumnNumber("ID")))
			pyperclip.copy(IDNo)
			print(IDNo)

		def openIDPage(self, linkData):
			#Copy Studnet ID to clipboard
			self.copyIDToClipboard(linkData["position"])
			#We can only have one selected Item so
			for links in self.rcMenuData["studentIDLinks"]:
				if links["name"] == linkData["text"]: #We know which link it is to open
					chrome_path = self.rcMenuData["resourcePaths"]["chrome"]
					webbrowser.get(chrome_path).open(links["link"])

		def getStudentInfo(self):
			#Builds a string full of the student data and returns it as a string
			studentInfo = ""
			for item in self.selectedItems():
				studentInfo += str(item.text(self.getColumnNumber("ID"))) + " - "
				studentInfo += str(item.text(self.getColumnNumber("Forename"))) + " "
				studentInfo += str(item.text(self.getColumnNumber("Surname"))) + " - "
				studentInfo += str(item.text(self.getColumnNumber("Email"))) + " - "
				studentInfo += str(item.text(self.getColumnNumber("Course"))) + "\n"
			return studentInfo

		def copyStudentInfo(self):
			pyperclip.copy(self.getStudentInfo())

		def emailToAdmin(self):
			# bod = "This  is a string \n that has line \n breaks in it"
			self.emailer(("\n\n" + self.getStudentInfo()), "Student Information", self.rcMenuData["administratorContact"]["email"])
			# self.emailer(bod, "Student Information", self.rcMenuData["administratorContact"]["email"])


		def clearSelection(self):
			for item in self.selectedItems():
				item.setSelected(False)


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

