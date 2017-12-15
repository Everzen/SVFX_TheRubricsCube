import sys, os, pprint, time
from PySide.QtCore import *
from PySide.QtGui import *
import qdarkstyle
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import xml.etree.ElementTree as ET
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from operator import itemgetter
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import widgets
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


tree = ET.parse('resources\SFX6000.xml')
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

loanList = [studentList[0], studentList[1]]


class SVFX_AssetTrackerUI(QDialog):
    def __init__(self, parent=None):
        super(SVFX_AssetTrackerUI, self).__init__(parent)

        tabLayout = QVBoxLayout()
        self.userListTV = widgets.userTV(studentList)
        self.setMinimumSize(800,600)
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.userListTV, "Users")
        self.tabWidget.addTab(QWidget(), "Relative")
        self.tabWidget.addTab(QWidget(), "Questions")
        self.tabWidget.addTab(QWidget(), "Quest Specific")

        tabLayout.addWidget(self.tabWidget)


        userMessageLayout = QVBoxLayout()
        userColumnWidth = 150
        userTabWidth = 500
        
        #Setup regarding List - This is going to dictate who the message is about
        regardLabel = QLabel("REGARDING:")
        regardingListLW =  QListWidget()
        regardingListLW.setMaximumWidth(userColumnWidth)

        # regardingListLW.insertItems(0, regardingList)

        #set up Message From List
        voiceListLW =  QListWidget()
        voiceListLW.setMaximumWidth(userColumnWidth)
        voices =[]

        #Grab all the voices
        voiceLabel = QLabel("VOICE ORIGIN:")
        # for text in voiceList:
        #     voices.append(text["name"])

        voiceListLW.insertItems(0, voices)  
        voiceListLW.setCurrentRow(0)
        voiceListLW.setMaximumHeight(19*len(voices))

        #Setup player List
        playerLabel = QLabel("SEND TO PLAYER:")
        playerListLW =  QListWidget()
        playerListLW.setMaximumWidth(userColumnWidth)
        players = []

        #Grab all the Players
        # for text in playerList:
        #     players.append(text["character"] + " (" + text['name'] + ")")

        playerListLW.insertItems(0, players)
        playerListLW.setMaximumHeight(18*len(players))
        playerListLW.setSelectionMode(QAbstractItemView.ExtendedSelection)

        def findActiveStatement():
        	"""This function returns the listwidget and the selected row in a dictionary"""
        	#Find the list Widget in the Current Tab
        	activeList = self.tabWidget.currentWidget().layout().itemAt(0).widget()
        	# print activeList
        	# print type(activeList)
        	if len(activeList.selectedIndexes()) != 0:
        		# print activeList.selectedIndexes()[0].row()
        		return {'activeListWidget':activeList, "activeStatement" : activeList.selectedIndexes()[0].row()}
        	else:
        		return {'activeListWidget':None, "activeStatement" : None}

        def findActiveRegard():
        	if len(regardingListLW.selectedIndexes()) != 0:
        		# print "Active Regard: " + regardingListLW.item(regardingListLW.selectedIndexes()[0].row()).text()
        		return regardingListLW.item(regardingListLW.selectedIndexes()[0].row()).text()
        	else:
        		return None

        def findActiveVoice():
        	# print "Active Voice: " + str(voiceListLW.selectedIndexes()[0].row())
        	return voiceListLW.selectedIndexes()[0].row()

        def findActivePlayers():
        	activePlayerList = []
        	for index in playerListLW.selectedIndexes():
        		activePlayerList.append(index.row())
        	# print activePlayerList
        	return activePlayerList

        def processMessage():
        	activeStatementDict = findActiveStatement()
        	if activeStatementDict["activeListWidget"]:
        		statement = activeStatementDict["activeListWidget"].item(activeStatementDict["activeStatement"]).text()
        		#Now check if the statement splits - if it does then it requires a regard 
        		splitStatement = statement.split("####")
        		if len(splitStatement) > 1:
        			#The statement has split so collect the regard
        			activeRegard = findActiveRegard()
        			if activeRegard:
        				#Awkard check code to see where we insert the name. If both sections of the split string has characters we insert in the middle. If not we insert on the empty string
        				insertTarget = 2 #this represents the name having to be inserted into the middle
        				for i, splitPhrase in enumerate(splitStatement):
        					if len(splitPhrase) == 0: insertTarget = i
        				#Now we hardcode build the string - messy!
        				if insertTarget == 0:
        					statement = "*" + activeRegard + "*" + splitStatement[1]
        				elif insertTarget == 1:
        					statement = splitStatement[0] + "*" + activeRegard + "*"
        				elif insertTarget == 2:
        					statement = splitStatement[0] + "*" + activeRegard + "*" + splitStatement[1]
        			else: return None
        		return statement
        	else: 
        		return None

        def sendMessage():
        	finalVoice = findActiveVoice()
        	# print "Voice: " + str(finalVoice)
        	finalPlayers = findActivePlayers()
        	# print "Players: " + str(findActivePlayers)
        	finalStatement = processMessage()
        	# print "Statement: " + str(findActiveStatement)
        	# print "My final Statement is: " + str(finalStatement)
        	if (len(finalPlayers) != 0) and finalStatement: #If all if these conditions are met then we should be able to send the message
        		voicename = voiceList[finalVoice]["name"]
        		asUser = int(voiceList[finalVoice]["asUser"])
        		print "Message: " + finalStatement
        		for playerNum in finalPlayers:
        			playerID = playerList[playerNum]["slackID"]
        			slack_client.api_call("chat.postMessage", channel=playerID, text=finalStatement, as_user=asUser, username=voicename )    #Using text to add an emoji
        			print "SENDING TO: " + playerList[playerNum]["character"]
        	else:
        		print "Message failed to SEND"


        sendButton = QPushButton("SEND SLACK MESSAGE")
        sendButton.setMinimumHeight(50)
        sendButton.setMaximumWidth(userColumnWidth)
        sendButton.clicked.connect(sendMessage)

        userMessageLayout.addWidget(regardLabel)
        userMessageLayout.addWidget(regardingListLW)
        userMessageLayout.addWidget(voiceLabel)
        userMessageLayout.addWidget(voiceListLW)
        userMessageLayout.addWidget(playerLabel)
        userMessageLayout.addWidget(playerListLW)
        userMessageLayout.addWidget(sendButton)

        mainLayout = QHBoxLayout()
        mainLayout.addLayout(tabLayout)
        mainLayout.addLayout(userMessageLayout)

        # mainLayout.addWidget(tabWidget)
        # mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Dungeon Master - Fast Messenger")



#######################################Load Program#######################################################
reg = SVFX_AssetTrackerUI()
reg.show()
# view.show()
sys.exit(app.exec_())
# ~~~~~~~~~~~~~~~~~~~~~~~~~

