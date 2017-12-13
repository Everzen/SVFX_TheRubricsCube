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



#######################################Load Program#######################################################
reg = widgets.userTV(studentList)
reg.show()
# view.show()
sys.exit(app.exec_())
# ~~~~~~~~~~~~~~~~~~~~~~~~~

