from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, String
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///database\SVFXDataBase.db')
#engine = create_engine(r'sqlite:///C:\path\to\foo.db')


Session = sessionmaker(bind=engine)
session = Session()  

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'

	user_id = Column(Integer, primary_key = True)
	forename = Column(String(50), index=True)
	surname = Column(String(50), index=True)
	bolton_id = Column(Integer())   
	email = Column(String(100), index=True)
	course = Column(String(100), index=True)

class Equipment(Base):
	__tablename__ = 'equipment'

	equipment_id = Column(Integer, primary_key = True)
	equipment_name = Column(String(50), index=True, unique=False)
	equipment_barcode = Column(String(50), index=True)
	equipment_value = Column(Integer())

class Material(Base):
	__tablename__ = 'materials'

	material_id = Column(Integer, primary_key = True)
	material_name = Column(String(50), index=True, unique=True)
	material_barcode = Column(String(50), index=True)
	material_value = Column(Integer())
	material_unitCost = Column(Integer())
	material_createdOn = Column(DateTime(), default=datetime.now)
	material_updatedOn = Column(DateTime(), default=datetime.now, onupdate=datetime.now)

class Loan(Base):
	__tablename__ = 'loans'

	loan_id = Column(Integer, primary_key = True)
	loan_name = Column(String(50), index=True, unique=True)
	user_id = Column(Integer(), ForeignKey('users.user_id'))
	loan_out = Column(DateTime(), default=datetime.now)
	loan_returned = Column(DateTime())
	loan_resolved = Column(Boolean(), default=False)
	user = relationship("User", backref=backref('loans'))

class LoanItem(Base):
	__tablename__ = 'loanItem'
	
	loanItem_id = Column(Integer, primary_key = True)
	loan_id = Column(Integer(), ForeignKey('loans.loan_id'))
	equipment_id = Column(Integer(), ForeignKey('equipment.equipment_id'))
	quantity = Column(Integer(), default = 1)
	loanItem_out = Column(DateTime(), default=datetime.now)
	loanItem_returned = Column(DateTime())	
	loan = relationship("Loan", backref=backref('loanItems'))
	equipment = relationship("Equipment", uselist=False)


Base.metadata.create_all(engine)




#############################################################################LOAD IN USERS###########################################################

import xml.etree.ElementTree as ET
tree = ET.parse('resources\SFX6000.xml')
root = tree.getroot()

print ("COURSE DATA")
print ("Course Name : " + root.get('Textbox12'))
print ("Course Code : " + root.get('Textbox4'))
print ("Course Tutor : " + root.get('Textbox16'))
print ("Module Semester 1 : " + root.get('Textbox23'))
print ("Module Year : " + root.get('Textbox20'))


print ("\nSTUDENT LIST\n")
students = []

for student in root[0][0]:
	# if student.get('courseName') == "BSc (Hons) Visual Effects for Film and Television":
	# if student.get('courseName') == "BDes(Hons) Special Effects for Film and Television":
	students.append(student)

newUsers = []

for student in students:
	print ((student.get('BoltonID')) + " " +  (student.get('contactEMail')) + " " + (student.get('Occurrence')) + " " + (student.get('forename1')) + " " + (student.get('surname')))
	userNew = User(forename = (student.get('forename1')), surname = (student.get('surname')), bolton_id = (student.get('BoltonID')), email = (student.get('contactEMail')), course = (student.get('courseName')))
	newUsers.append(userNew)

userStaff1 = User(forename = 'Richard', surname = 'Jones', bolton_id = 7040227, email = "rpj1@bolton.ac.uk", course = "Visual Effects")
userStaff2 = User(forename = 'Sam', surname = 'Taylor', bolton_id = 7700331, email = "st6@bolton.ac.uk", course = "Visual Effects")
userStaff3 = User(forename = 'Mark', surname = 'Whyte', bolton_id = 7040417, email = "maw1@bolton.ac.uk", course = "Visual Effects")

newUsers.append(userStaff1)
newUsers.append(userStaff2)
newUsers.append(userStaff3)


session.bulk_save_objects(newUsers)
session.commit()


#################################################################Load in Equipment#####################################################################
equipmentList =[]
equip01 = Equipment(equipment_name = "Wacom1", equipment_barcode = "WACOMPEN-C208-001", equipment_value = 73)
equip02 = Equipment(equipment_name = "Wacom2", equipment_barcode = "WACOMPEN-C208-002", equipment_value = 73)
equip03 = Equipment(equipment_name = "Wacom3", equipment_barcode = "WACOMPEN-C208-003", equipment_value = 73)
equip04 = Equipment(equipment_name = "Wacom4", equipment_barcode = "WACOMPEN-C208-004", equipment_value = 73)

equipmentList = [equip01,equip02,equip03,equip04]

session.bulk_save_objects(equipmentList)
session.commit()

######################################################################################################################################


# ourUsers = session.query(User).all() #Pull out all users
# print (ourUsers)

# for user in session.query(User):
# 	print ((user.surname) + " " + str(user.user_id))


for user in session.query(User).order_by(User.surname):
	print ((user.surname) + " " + str(user.user_id))

record = session.query(User).filter_by(bolton_id='7040227').first()
print (record.email)


record = session.query(Equipment).filter_by(equipment_name='Wacom1').first()
print (record.equipment_name)


#################################################################Load in Loans#####################################################################

recordUser = session.query(User).filter_by(bolton_id='1502570').first()
print (recordUser.forename + " " + recordUser.surname )

loan01 = Loan()
loan01.user = recordUser
session.add(loan01)

loanItem01 = LoanItem(loan = loan01, equipment=equip01)
loanItem02 = LoanItem(loan = loan01, equipment=equip03)
loanItem03 = LoanItem(loan = loan01, equipment=equip02)

loan01.loanItems.append(loanItem01)
loan01.loanItems.append(loanItem02)
loan01.loanItems.append(loanItem03)


recordUser = session.query(User).filter_by(bolton_id='7040227').first()
print (recordUser.forename + " " + recordUser.surname )

loan02 = Loan()
loan02.user = recordUser
session.add(loan02)

loan02Item01 = LoanItem(loan = loan02, equipment=equip04)

loan02.loanItems.append(loan02Item01)


session.commit()

#################################################################Load Loan Items#####################################################################

query = session.query(Loan.loan_id).first()
print(query)