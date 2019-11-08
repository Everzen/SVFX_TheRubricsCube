#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#TO DO:
#       Update folders for sending emails and copying student ID numbers - This is done, but there is a problem with copying large strings to an email, so there is going to have to be a workaround
#       Have a button that opens the correct module folder and also loads the correct page to download the module XML
#       Module marking folders are being generated into the central Module Lists folder at the moment - Need to add the a directory chooser to specify where these folders go

import sys, os, pprint, time
from PySide2.QtCore import *
from PySide2.QtWidgets import QMainWindow, QDialog, QWidget, QVBoxLayout, QLabel, QTabWidget, QHBoxLayout, QComboBox, QListWidget, QListWidgetItem, QPushButton, QLineEdit, QCalendarWidget, QApplication, QAbstractItemView, QSizePolicy, QSpacerItem
from PySide2.QtGui import *
import qdarkstyle
import json
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from operator import itemgetter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import widgets
import googleSheet
from utilities import grabInfo
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = QApplication(sys.argv)
# app.setStyleSheet(qdarkstyle.load_stylesheet())
sshFile = "resources/darkorange.stylesheet"
with open(sshFile,"r") as fh:
    app.setStyleSheet(fh.read())

# app.setStyleSheet(qdarkstyle.load_stylesheet())
# ~~~~~~~~~~~~~~~~~~~~~RESOURCES~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

staffList  = grabInfo("staff")
# courseList = grabInfo("courseList")
yearInfo = grabInfo("academicYears")
yearList  = []
for y in yearInfo:
    yearList.append(y["year"])

#Grab the emails
localResourcesPath = grabInfo("resourcePaths")["localResources"]
emailDict = grabInfo("emails", jsonFile = localResourcesPath)
markingUnlock = grabInfo("rubricPowered", jsonFile = localResourcesPath) == "True"

courseList = grabInfo("courseList", jsonFile = localResourcesPath)


#Find all files in the default SVFX Module folder
moduleFolder = grabInfo("resourcePaths")["moduleListFolder"]
moduleList = []
for f in os.listdir(moduleFolder):
    if f != "resources":
        moduleList.append({"name":f, "fullPath":(moduleFolder + "\\" + f)})

semesterList = grabInfo("semesters")


#Build an empty dictionary that we can build 
rcMenuData = grabInfo("RCMenus")
rcMenuData["administratorContact"] = grabInfo("administratorContact")
rcMenuData["resourcePaths"] = grabInfo("resourcePaths")

class SVFX_AssetTrackerUI(QDialog):
    def __init__(self, parent=None):
        super(SVFX_AssetTrackerUI, self).__init__(parent)
        self.assignmentDetails = {} #A dict to contain information about the assignments, once the marking module sheet is setup.
        self.studentFolders = []

        self.folderLabel = QLabel(" - ")  #Define Folder label early so that it can be passed to the list widget
        # self.folderLabel.setText("moo")

        userLeftLayout = QVBoxLayout()
        self.userListTV = widgets.userTV(courseList, self.folderLabel, emailDict, rcMenuData)
        self.setMinimumWidth(750)
        self.setMaximumWidth(750)
        self.setMinimumHeight(900)
        self.markingSheetTab = QWidget() #This is a holding widget for the marking folder options
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.userListTV, "Student Contact")
        if markingUnlock: self.tabWidget.addTab(self.markingSheetTab, "Module Marking Creation")
        # self.tabWidget.addTab(QWidget(), "Relative")
        # self.tabWidget.addTab(QWidget(), "Questions")
        # self.tabWidget.addTab(QWidget(), "Quest Specific")

        moduleFolderLayout = QHBoxLayout()
        foldernameLabel = QLabel("SPECIFY MODULE:")
        self.chooseModuleCombo = QComboBox(self)
        self.chooseModuleCombo.addItem("Please choose module....")
        for module in moduleList: self.chooseModuleCombo.addItem(module["name"])   
        self.chooseModuleCombo.activated[str].connect(self.moduleComboSel)       
        
        foldernameLabel.setMaximumWidth(95)
        # self.folderLabel = QLabel("Path to be displayed here...")
        
        moduleFolderLayout.addWidget(foldernameLabel)
        moduleFolderLayout.addWidget(self.chooseModuleCombo)
        moduleFolderLayout.addWidget(self.folderLabel)

        #Setup regarding List - This is going to dictate who the message is about
        courseFilterLayout = QHBoxLayout()
        # courseLabel = QLabel("Filter by Courses")
        self.courseListLW =  QListWidget()
        self.courseListLW.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.courseListLW.setMaximumHeight(19*len(courseList))
        for c in courseList:
            newCourse = QListWidgetItem(c["shortName"])
            self.courseListLW.addItem(newCourse)

        courseFilterButton = QPushButton("Apply Course Filter")

        courseFilterButton.clicked.connect(self.filterCourses)
        courseFilterButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        courseFilterButton.setMaximumHeight(self.courseListLW.frameGeometry().height())
        # courseFilterButton.setMinimumHeight(25)

        courseFilterLayout.addWidget(self.courseListLW)
        courseFilterLayout.addWidget(courseFilterButton)

        userLeftLayout.addLayout(moduleFolderLayout)
        userLeftLayout.addLayout(courseFilterLayout)
        userLeftLayout.addWidget(self.tabWidget)


        moduleSettingsLayout = QVBoxLayout()
        moduleSettingsLayout.setAlignment(Qt.AlignTop)

        userColumnWidth = 250
        userTabWidth = 400
        
        #Setup self.markingSheetTab options
        Vlayout = QVBoxLayout()
        Vlayout.setAlignment(Qt.AlignTop)
        self.markingSheetTab.setLayout(Vlayout)
        
        markerHLayout = QHBoxLayout()
        firstMarkerVLayout = QVBoxLayout()
        secondMarkerVLayout = QVBoxLayout()

        self.firstMarkerCombo = QComboBox(self)
        self.firstMarkerCombo.addItem("Choose First Marker...")  
        self.firstMarkerCombo.activated[str].connect(self.firstMarkerComboSel)       
        for s in staffList:
            self.firstMarkerCombo.addItem(s["name"])
        self.firstMarkerEmail = QLineEdit()
        self.firstMarkerEmail.setReadOnly(True)

        firstMarkerVLayout.addWidget(self.firstMarkerCombo)
        firstMarkerVLayout.addWidget(self.firstMarkerEmail)

        self.secondMarkerCombo = QComboBox(self)
        self.secondMarkerCombo.addItem("Choose Second Marker...")
        self.secondMarkerCombo.activated[str].connect(self.secondMarkerComboSel)       
        for s in staffList:
            self.secondMarkerCombo.addItem(s["name"])
        self.secondMarkerEmail = QLineEdit()
        self.secondMarkerEmail.setReadOnly(True)

        secondMarkerVLayout.addWidget(self.secondMarkerCombo)
        secondMarkerVLayout.addWidget(self.secondMarkerEmail)

        markerHLayout.addLayout(firstMarkerVLayout)
        markerHLayout.addLayout(secondMarkerVLayout)
        Vlayout.addLayout(markerHLayout)

        yearLayout = QHBoxLayout()
        yearLayout.setAlignment(Qt.AlignLeft)
        yearLabel = QLabel("Year and Semester:")
        self.yearCombo = QComboBox(self)
        self.yearCombo.addItems(yearList)    #JSON Coded year dates
        self.yearCombo.setMinimumWidth(65)
        self.semesterCombo = QComboBox(self)
        self.semesterCombo.addItems(semesterList)    #JSON Coded year dates
        self.getGoogleFolderID()

        yearLayout.addWidget(yearLabel)
        yearLayout.addWidget(self.yearCombo)
        yearLayout.addWidget(self.semesterCombo)
        Vlayout.addLayout(yearLayout)

        moduleTimingHLayout = QHBoxLayout()
        modulePrepVLayout = QVBoxLayout()
        modulePrepVLayout.setAlignment(Qt.AlignTop)
        moduleReviewVLayout = QVBoxLayout()
        moduleReviewVLayout.setAlignment(Qt.AlignTop)

        prepDateLabel = QLabel("Module Preparation Date:")
        self.prepDate = QCalendarWidget(self)
        self.prepDate.setMaximumHeight(200)
        self.prepDate.setMaximumWidth(400)

        calendarTweak = QTextCharFormat()
        calendarTweak.setForeground(QBrush(QColor(230,230,230)))
        calendarTweak.setBackground(QBrush(QColor(45,45,45)))
        self.prepDate.setHeaderTextFormat(calendarTweak)

        modulePrepVLayout.addWidget(prepDateLabel)
        modulePrepVLayout.addWidget(self.prepDate)

        reviewDateLabel = QLabel("Module Review Date:")
        self.reviewDate = QCalendarWidget(self)
        self.reviewDate.setMaximumHeight(200)

        self.reviewDate.setHeaderTextFormat(calendarTweak)

        moduleReviewVLayout.addWidget(reviewDateLabel)
        moduleReviewVLayout.addWidget(self.reviewDate)

        moduleTimingHLayout.addLayout(modulePrepVLayout)
        moduleTimingHLayout.addLayout(moduleReviewVLayout)
        Vlayout.addLayout(moduleTimingHLayout)

        moduleBoxDocButton = QPushButton("Build Module Box Document")
        moduleBoxDocButton.clicked.connect(self.buildModuleBox)
        moduleBoxDocButton.setMinimumHeight(80)
        Vlayout.addWidget(moduleBoxDocButton)

        verticalSpacer = QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding)
        
        # moduleSettingsLayout.addWidget(courseLabel)
        # moduleSettingsLayout.addWidget(self.courseListLW)
        # moduleSettingsLayout.addWidget(courseFilterButton)
        # moduleSettingsLayout.addWidget(firstMarkerLabel)
        # moduleSettingsLayout.addWidget(self.firstMarkerCombo)
        # moduleSettingsLayout.addWidget(self.firstMarkerEmail)
        # moduleSettingsLayout.addWidget(secondMarkerLabel)
        # moduleSettingsLayout.addWidget(self.secondMarkerCombo)
        # moduleSettingsLayout.addWidget(self.secondMarkerEmail)
        # moduleSettingsLayout.addLayout(yearLayout)
        # moduleSettingsLayout.addWidget(prepDateLabel)
        # moduleSettingsLayout.addWidget(self.prepDate)
        # moduleSettingsLayout.addWidget(reviewDateLabel)
        # moduleSettingsLayout.addWidget(self.reviewDate)

        extrasLayout = QHBoxLayout()
        
        self.markingFolderButton = QPushButton("Create Marking Folders")
        self.markingFolderButton.clicked.connect(self.createMarkingFolders)
        self.markingFolderButton.setEnabled(False)
        self.markingFolderButton.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.markingFolderButton.setMaximumWidth(300)
        extrasLayout.addWidget(self.markingFolderButton)

        sortAssignmentsVLayout = QVBoxLayout()
        self.sortAssignmentsLabel = QLabel("Sort Assignments")
        self.sortAssignmentsLabel.setEnabled(False)
        self.assignmentCombo = QComboBox(self)
        self.assignmentCombo.addItem("No Assignment info")
        self.assignmentCombo.setEnabled(False)
        self.sortAssignmentsButton = QPushButton("Sort Assignments") 
        self.sortAssignmentsButton.clicked.connect(self.sortAssignmentFiles)
        self.sortAssignmentsButton.setEnabled(False)

        sortAssignmentsVLayout.addWidget(self.sortAssignmentsLabel)
        sortAssignmentsVLayout.addWidget(self.assignmentCombo)
        sortAssignmentsVLayout.addWidget(self.sortAssignmentsButton)
        extrasLayout.addLayout(sortAssignmentsVLayout)

        Vlayout.addLayout(extrasLayout)
        Vlayout.addItem(verticalSpacer)
        # exportFeedbackButton = QPushButton("Export Feedback")
        # exportFeedbackButton.setMinimumHeight(215)
        # # exportFeedbackButton.setMinimumWidth(100)
        # exportFeedbackButton.setEnabled(False)



        mainLayout = QHBoxLayout()
        mainLayout.addLayout(userLeftLayout)
        # mainLayout.addLayout(moduleSettingsLayout)
        # mainLayout.addLayout(activationLayout)

        # mainLayout.addWidget(tabWidget)
        # mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("The Rubrics Cube")

    def moduleComboSel(self, text):
        #Find the file name
        fname = None
        for m in moduleList:
            if text == m["name"]: fname = m["fullPath"]
        if fname:
            self.userListTV.loadModule(fname)



    def filterCourses(self):
        #Grab the selection state of the Course List widget
        selCourses = self.courseListLW.selectedItems()
        selCourseArr = []
        if len(selCourses) == 0: selCourseArr = ["SFX", "VFX", "SMUFX", "MMFX"]  #No course is selected, so no filter is applied
        else:
            for c in selCourses: selCourseArr.append(c.text())
        # print("Selected Courses: " + str(selCourseArr))
        self.userListTV.filterbyCourse(selCourseArr)
        print(str(self.prepDate.selectedDate().day()) + "/" + str(self.prepDate.selectedDate().month()) + "/" + str(self.prepDate.selectedDate().year()))
        print(str(self.reviewDate.selectedDate().day()) + "/" + str(self.reviewDate.selectedDate().month()) + "/" + str(self.reviewDate.selectedDate().year()))

    def firstMarkerComboSel(self, text):
        gmail = ""
        for s in staffList:
            if text == s["name"]: gmail = s["gmailID"]
        self.firstMarkerEmail.setText(gmail)

    def secondMarkerComboSel(self, text):
        gmail = ""
        for s in staffList:
            if text == s["name"]: gmail = s["gmailID"]
        self.secondMarkerEmail.setText(gmail)

    def getGoogleFolderID(self):
        # print(self.yearCombo.currentText())
        # print(self.semesterCombo.currentText())
        for year in yearInfo:
            if year["year"] == self.yearCombo.currentText():
                return year[self.semesterCombo.currentText()]


    def getMasterTemplateGoogleID(self):
        # print("MasterTemplate : " + grabInfo("resourcePaths")["masterGoogleTemplate"])
        return grabInfo("resourcePaths")["masterGoogleTemplate"]

    def buildModuleBox(self):
        #We need to build all the data into a dictionary to pass to the relevant function that will build the google sheet
        moduleData={}
        markingUserList = self.userListTV.getUserList()
        markingUserList = sorted(markingUserList, key=lambda k: k['surname']) #Sort the list into alphabetical by surname
        moduleData["students"] = markingUserList
        moduleData["code"] = self.userListTV.getModuleCode()
        moduleData["year"] = self.yearCombo.currentText()
        moduleData["prepDate"] = str(self.prepDate.selectedDate().day()) + "/" + str(self.prepDate.selectedDate().month()) + "/" + str(self.prepDate.selectedDate().year())
        moduleData["reviewDate"] = str(self.reviewDate.selectedDate().day()) + "/" + str(self.reviewDate.selectedDate().month()) + "/" + str(self.reviewDate.selectedDate().year())
        moduleData["firstMarker"] = self.firstMarkerCombo.currentText()
        moduleData["secondMarker"] = self.secondMarkerCombo.currentText()
        moduleData["masterGTemplate"] = self.getMasterTemplateGoogleID()
        moduleData["markingGFolder"] = self.getGoogleFolderID()
        # pprint.pprint(moduleData)
        self.assignmentDetails = googleSheet.buildMarkSheet(moduleData)
        #Now that we have the assessment details, we can add the items to the combo box
        self.assignmentCombo.removeItem(0)
        self.assignmentCombo.addItem("Specify assignment...")
        for i in range(0, self.assignmentDetails["number"]):
            self.assignmentCombo.addItem(self.assignmentDetails["titles"][i])
        #Now activate the rest of the UI
        #self.markingFolderButton.setEnabled(True)


    def buildModuleBoxFolders(self):
    	markingFolder = moduleFolder #Every time you see this line, we need to replace this with an established local Marking Folder that is chosen by a directory Picker
    	modulefolderName = self.userListTV.getModuleCode() + "_" + self.userListTV.getModuleTitle()
    	if(not os.path.exists(markingFolder + "//_ModuleBox")): os.mkdir(markingFolder + "//_ModuleBox")
    	if(not os.path.exists(markingFolder + "//_ModuleBox" + "//" +  modulefolderName)): os.mkdir(markingFolder + "//_ModuleBox" + "//" +  modulefolderName)
    	if(not os.path.exists(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "1.0 Module Guide")): os.mkdir(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "1.0 Module Guide")
    	if(not os.path.exists(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "2.0 Assessments & Assessment Moderation")): os.mkdir(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "2.0 Assessments & Assessment Moderation")
    	if(not os.path.exists(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "3.0 Sample of Work")): os.mkdir(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "3.0 Sample of Work")
    	if(not os.path.exists(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "4.0 Module Evaluation")): os.mkdir(markingFolder + "//_ModuleBox" + "//" +  modulefolderName + "//" + "4.0 Module Evaluation")


    def createMarkingFolders(self):
        self.buildModuleBoxFolders() #Build the standard modulebox Template
        folderStudents = self.userListTV.getUserList()
        markingFolder = moduleFolder
        self.studentFolders = []
        for s in folderStudents:
        	studentFolderDetails = {}
        	folderName = s['surname'] + "_" + s['forename'] + "_ID_" + s['id']
        	studentFolderDetails['id'] = s['id']
        	studentFolderDetails['folder'] = (markingFolder + "//" + folderName)
        	self.studentFolders.append(studentFolderDetails)
        	if(not os.path.exists(markingFolder + "//" + folderName)): os.mkdir(markingFolder + "//" + folderName)
        	for i in range(0, self.assignmentDetails["number"]):
        	    if(not os.path.exists(markingFolder + "//" + folderName + "//" + self.assignmentDetails['titles'][i])): os.mkdir(markingFolder + "//" + folderName + "//" + self.assignmentDetails['titles'][i])
        	self.sortAssignmentsLabel.setEnabled(True)
        	self.assignmentCombo.setEnabled(True)
        	self.sortAssignmentsButton.setEnabled(True)

    def sortAssignmentFiles(self):
    	assignmentFolder = self.assignmentCombo.currentText()
    	markingFolder = moduleFolder
    	if (assignmentFolder == "No Assignment info") or ((assignmentFolder == "Specify assignment...")): 
    		print("Error - No Assignment Names Listed")
    		return 0
    	else:
    		dirFiles = [f for f in os.listdir(markingFolder) if os.path.isfile(os.path.join(markingFolder, f))]
    		# print("Directory Files: " + str(dirFiles))
    		#Now loop through all the student IDs and match up the files
    		for s in self.studentFolders:
    			for f in dirFiles:
    				if s['id'] in f:
    					# print("Found: " + s['id'] + " in " + str(f))
    					filename = os.path.split(f)  #This priduces an arra
    					# print ("Split : " + str(filename))
    					# print("The File: " + str(f))
    					# print("The Location: " + str(s['folder'] + "//" + assignmentFolder + "//" + filename[1]))
    					os.rename((markingFolder + "//" + f), (s['folder'] + "//" + assignmentFolder + "//" + filename[1])) #Renameing is the way that windows moves files from one folder to another




#######################################Load Program#######################################################
reg = SVFX_AssetTrackerUI()
reg.show()
# view.show()
sys.exit(app.exec_())
# ~~~~~~~~~~~~~~~~~~~~~~~~~

