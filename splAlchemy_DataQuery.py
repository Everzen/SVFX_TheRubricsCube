from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Numeric, String
from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///database\SVFXDataBase.db')

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


#################################################################Queries#####################################################################



# for user in session.query(User).order_by(User.surname):
# 	print ((user.surname) + " " + str(user.user_id))

# record = session.query(User).filter_by(bolton_id='7040227').first()
# print (record.email)


# record = session.query(Equipment).filter_by(equipment_name='Wacom1').first()
# print (record.equipment_name)


for user in session.query(User).order_by(User.surname):      #Query and return all of the users in an array ordered by surname
	print ((user.surname) + " " + str(user.user_id))


query = session.query(Loan)  #Return all the loads associated with Becky Clayton
print("All Loans: ")
for loan in query: print (loan)
 

userLoans = []
for loan in query: 
	if loan.user.bolton_id == 1502570: userLoans.append(loan)
print ("User Loans : " + str(userLoans))

######################################################################################################################################
