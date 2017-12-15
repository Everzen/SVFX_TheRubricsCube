
from PySide.QtCore import *
from PySide.QtGui import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from operator import itemgetter




class userTV(QTreeWidget):
		def __init__(self, userList, parent = None):
			QTreeWidget.__init__(self, parent)
			self.setMinimumSize(800,600)
			self.setSelectionBehavior(QAbstractItemView.SelectRows)
			self.setSelectionMode(QAbstractItemView.MultiSelection)
			# self.model = QStandardItemModel()
			self.setColumnCount(5)
			self.totalHeaders = ['ID','Forename', 'Surname', 'Email', 'Course']
			self.activeHeaders = []
			self.setHeaderLabels(self.totalHeaders)
			self.headerMapping = {'ID':'id', 'Forename':'forename', 'Surname':'surname', 'Email':'email', 'Course':'course'}
			self.showHeaders = {'ID':True, 'Forename':True, 'Surname':True, 'Email':True, 'Course':True}
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
			# sort = menu.addAction(self.tr("Sort by " + headerText))
			sortText =  ("Sort by " +  str(headerText))
			sort = menu.addAction(self.tr(sortText))
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



class loanTV(QTreeWidget):
		def __init__(self, userList, parent = None):
			QTreeWidget.__init__(self, parent)
			self.setMinimumSize(800,600)
			self.setSelectionBehavior(QAbstractItemView.SelectRows)
			self.setSelectionMode(QAbstractItemView.MultiSelection)
			# self.model = QStandardItemModel()
			self.setColumnCount(5)
			self.totalHeaders = ['ID','Forename', 'Surname', 'Email', 'Course']
			self.activeHeaders = []
			self.setHeaderLabels(self.totalHeaders)
			self.headerMapping = {'ID':'id', 'Forename':'forename', 'Surname':'surname', 'Email':'email', 'Course':'course'}
			self.showHeaders = {'ID':True, 'Forename':True, 'Surname':True, 'Email':True, 'Course':True}
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
			# sort = menu.addAction(self.tr("Sort by " + headerText))
			sortText =  ("Sort by " +  str(headerText))
			sort = menu.addAction(self.tr(sortText))
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



