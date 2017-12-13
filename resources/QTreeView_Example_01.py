#! /usr/bin/env python3
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# In this prototype/example a QTreeView is created. Then it's populated with
# three containers and all containers are populated with three rows, each 
# containing three columns.
# Then the last container is expanded and the last row is selected.
# The container items are spanned through the all columns.
# Note: this requires > python-3.2
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys, os, pprint, time
from PySide.QtCore import *
from PySide.QtGui import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import xml.etree.ElementTree as ET
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from operator import itemgetter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = QApplication(sys.argv)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


tree = ET.parse('SFX6000.xml')
root = tree.getroot()

print ("COURSE DATA")
print ("Course Name : " + root.get('Textbox12'))
print ("Course Code : " + root.get('Textbox4'))
print ("Course Tutor : " + root.get('Textbox16'))
print ("Module Semester 1 : " + root.get('Textbox23'))
print ("Module Year : " + root.get('Textbox20'))


print ("\nSTUDENT LIST\n")
studentList = []

for student in root[0][0]:
	studentDetail = {'id':student.get('BoltonID'), 'forename':student.get('forename1'), 'surname':student.get('surname'), 'email':student.get('contactEMail'), 'occurence':student.get('Occurrence'), 'course':student.get('courseName'), 'attendence':'A', 'lateness':0}
	studentList.append(studentDetail)

# for student in studentList:
# 	print ((student.get('BoltonID')) + " " +  (student.get('contactEMail')) + " " + (student.get('Occurrence')) + " " + (student.get('forename1')) + " " + (student.get('surname')))

# studentList = sorted(studentList, key=itemgetter('surname'))


# init widgets
# view = QTreeView()
# view.setSelectionBehavior(QAbstractItemView.SelectRows)
# view.setSelectionMode(QAbstractItemView.MultiSelection)
# model = QStandardItemModel()
# model.setHorizontalHeaderLabels(['ID','Forename', 'Surname', 'Email', 'Occurrence', 'Course', 'Attendence', 'Late Time'])
# view.setModel(model)
# view.setUniformRowHeights(True)
# view.customContextMenuRequested.connect(openMenu) #Add in context RC menu

# def openMenu(postiion)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# populate data

# studentList = [{'id': 123456, 'forename':'Sam', 'surname': 'Taylor','email':'st6@bolton.ac.uk'},{'id':234567, 'forename':'Matt', 'surname': 'Lilley','email':'mpl2@bolton.ac.uk'},{'id':345678, 'forename':'Mark', 'surname': 'Whyte','email':'maw1@bolton.ac.uk'}]

# for user in studentList:
# 	idTI = QStandardItem(str(user['id']))
# 	forenameTI = QStandardItem(user['forename'])
# 	surnameTI = QStandardItem(user['surname'])
# 	emailTI = QStandardItem(user['email'])
# 	occTI = QStandardItem(user['occurence'])
# 	courseTI = QStandardItem(user['course'])
# 	attendenceTI = QStandardItem(user['attendence'])
# 	lateTI = QStandardItem(str(user['lateTime']))

# 	model.appendRow([idTI, forenameTI, surnameTI, emailTI, occTI, courseTI, attendenceTI, lateTI])
	# span container columns
	# view.setFirstColumnSpanned(i, view.rootIndex(), True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# expand third container
# index = model.indexFromItem(parent1)
# view.expand(index)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# select last row
# selmod = view.selectionModel()
# index2 = model.indexFromItem(child3)
# selmod.select(index2, QItemSelectionModel.Select|QItemSelectionModel.Rows)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class userRegisterTV(QTreeWidget):
		def __init__(self, userList, parent = None):
			QTreeWidget.__init__(self, parent)
			self.setSelectionBehavior(QAbstractItemView.SelectRows)
			self.setSelectionMode(QAbstractItemView.MultiSelection)
			# self.model = QStandardItemModel()
			self.setColumnCount(8)
			self.totalHeaders = ['ID','Forename', 'Surname', 'Email', 'Occurrence', 'Course', 'Attendence', 'Lateness']
			self.activeHeaders = []
			self.setHeaderLabels(self.totalHeaders)
			self.headerMapping = {'ID':'id', 'Forename':'forename', 'Surname':'surname', 'Email':'email', 'Occurrence':'occurence', 'Course':'course', 'Attendence':'attendence', 'Lateness':'lateness'}
			self.showHeaders = {'ID':True, 'Forename':True, 'Surname':True, 'Email':True, 'Occurrence':True, 'Course':True, 'Attendence':True, 'Lateness':True}
			# self.setModel(self.model)
			self.setUniformRowHeights(True)
			self.userList = userList
			# self.reSortList('surname')
			# self.reSortList('forename')
			self.setContextMenuPolicy(Qt.CustomContextMenu) #context menu for user data
			self.customContextMenuRequested.connect(self.userMenu)
			self.header().setContextMenuPolicy(Qt.CustomContextMenu) #context menu for headers
			self.header().customContextMenuRequested.connect(self.headerMenu)
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
			for user in self.userList:
				userData = []
				for header in self.activeHeaders: 
					userData.append(user[self.headerMapping[header]])
				userTWItem = QTreeWidgetItem(self,userData)
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
			sort = menu.addAction(self.tr("Sort by " + headerText))
			hide = menu.addAction(self.tr("Hide"))
			menu.addSeparator()
			badger = menu.addAction(self.tr("badger"))  # Add in the show column list here
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



reg = userRegisterTV(studentList)
reg.show()
# view.show()
sys.exit(app.exec_())
# ~~~~~~~~~~~~~~~~~~~~~~~~~


