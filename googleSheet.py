
# Make sure that any Sheet that you want to access is shared with "uobmarking@uob-marking.iam.gserviceaccount.com"  - otherwise the API will not be able to access it.
# Finding sheets by the URL key and the "open_by_key" method seems to be a bit more reliable! Also "open_by_url" seems to work well
# Good video series : https://www.youtube.com/watch?v=Z5G0luBohCg&list=PLOU2XLYxmsILOIxBRPPhgYbuSslr50KVq&index=4

##Imports for analysing and saving data
import xml.etree.ElementTree as ET
import json


##Imports for Google API setup and authentica
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import pprint
import time

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
markingDataJsonFile = "resources/MarkingData.json"

#~~~~~~~~~~~~~~~~~~~~~~FUNCTIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def grabInfo(infoType, jsonFile = markingDataJsonFile):
    with open(jsonFile) as json_file:
            info = json.load(json_file)
            return info[infoType]


#Hard Coded statistics 
studentStartRow = grabInfo("spreadSheet")["startRow"]
studentEndRow = grabInfo("spreadSheet")["studentNumber"]

# moduleData = {students: [], "code": "SFX0000", "year": "2017-18"}


def buildMarkSheet(moduleData):
  #First of all setup a connection to google Drive
  SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets']
  CLIENT_SECRET = 'resources/client_secret.json'

  store = file.Storage('resources/storage.json')
  credz = store.get()
  if not credz or credz.invalid:
    flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
    credz = tools.run_flow(flow, store)

  # Build a service, but the type of service that you build will have different methods and properties. In this cause we are building a drive service, so that we can do file operations on the drive
  SERVICE = discovery.build('drive', 'v2', http=credz.authorize(Http()))

  #moduleData["masterGTemplate"] - contains the google ID for the master Template file. moduleData["markingGFolder"] - contains the Google ID for year and semester folder that we are aiming for.
  moduleMarkingTitle = moduleData["code"] + "_" + moduleData["year"]
  moduleMarkingCopiedfile = {'title': moduleMarkingTitle, 'parents': [{'id': moduleData["markingGFolder"]}]}
  # moduleMarkingCopiedfile = {'title': moduleMarkingTitle, 'parents': [{'id': "16FMmH6li_jCHnTWS2VcPSbOAaSd-GrAz"}]}


  #Call the files.cop() method which works for this kind of drive service - the return object has a dictionary that we can reference the id from using ModuleMarkSheet['id']
  ModuleMarkSheet = SERVICE.files().copy(fileId=moduleData["masterGTemplate"], body=moduleMarkingCopiedfile).execute()
  # ModuleMarkSheet = SERVICE.files().copy(fileId="1BWfNFIPcPvinEfaSYvVvun3QfmwwYNoKeprseXU7uh8", body=moduleMarkingCopiedfile).execute()


  studentSheetData = []
  #Build Student Lists
  for student in moduleData["students"]:
    eachStudentList = [student['id'], student["email"], student["forename"], student["surname"]]
    studentSheetData.append(eachStudentList)


  #Now create a new service to operate on the new mark sheet
  sheetService = discovery.build('sheets', 'v4', http=credz.authorize(Http()))
  studentRange = "A" + str(studentStartRow) + ":D" + str(studentStartRow + len(studentSheetData))

  body = {
    "range": studentRange,
    "majorDimension": "ROWS",
    "values": studentSheetData,
  }

  print "Updating Student Details"
  sheetService.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range=studentRange, valueInputOption='USER_ENTERED', body=body).execute()

  #Update Module Code
  body = {
    "values": [[moduleData['code']]]
  }
  print "Module Code"
  sheetService.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!C2", valueInputOption='USER_ENTERED', body=body).execute()

  #Update First Marker
  body = {
    "values": [[moduleData['firstMarker']]]
  }
  sheetService.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!C9", valueInputOption='USER_ENTERED', body=body).execute()

  #Update Second Marker
  body = {
    "values": [[moduleData['secondMarker']]]
  }
  sheetService.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!C10", valueInputOption='USER_ENTERED', body=body).execute()

  #Update Year
  body = {
    "values": [[moduleData['year']]]
  }
  sheetService.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!C5", valueInputOption='USER_ENTERED', body=body).execute()

  #Update Preparation Date
  body = {
    "values": [[moduleData['prepDate']]]
  }
  sheetService.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!C11", valueInputOption='USER_ENTERED', body=body).execute()

  #Update Review Date
  body = {
    "values": [[moduleData['reviewDate']]]
  }
  sheetService.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!C12", valueInputOption='USER_ENTERED', body=body).execute()




  #Now look at deleting out the spare rows
  body =  {"requests": [
      {
      "deleteDimension": {
          "range": {
          "sheetId" : 404434578,
          "dimension": "ROWS",
          "startIndex": (studentStartRow+len(studentSheetData) - 1),
          "endIndex": studentEndRow
          }
        }
      }
      ]
      }

  #Delete out all of the spare rows
  sheetService.spreadsheets().batchUpdate(spreadsheetId=ModuleMarkSheet['id'], body=body).execute()

  #Now we need to get the number of assignments and the names of them and return them in Dictionary
  assignmentInfo = {}

  assNo = sheetService.spreadsheets().values().get(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!C20").execute()['values'][0][0]
  print("Assessment Number: " + str(assNo))
  
  assTitles = []
  assTitles.append(sheetService.spreadsheets().values().get(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!B21").execute()['values'][0][0])
  assTitles.append(sheetService.spreadsheets().values().get(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!B23").execute()['values'][0][0])
  assTitles.append(sheetService.spreadsheets().values().get(spreadsheetId=ModuleMarkSheet['id'], range="Module Specifications!B25").execute()['values'][0][0])
  print("Assessment Titles: " + str(assTitles))

  #ass the information to the assignment dictionary
  assignmentInfo["number"] = int(assNo)
  assignmentInfo["titles"] = assTitles

  return assignmentInfo






# #Now create a new service to operate on the new sheet
# SERVICE = discovery.build('sheets', 'v4', http=credz.authorize(Http()))

# studentRange = "A" + str(studentStartRow) + ":D" + str(studentStartRow + len(SVFXStudentData))
# print "Student Range : " + studentRange 

# body = {
#   "range": studentRange,
#   "majorDimension": "ROWS",
#   "values": SVFXStudentData,

# }


#   # "requests": [
#   #   {
#   #     "deleteDimension": {
#   #       "range": {
#   #         "dimension": "ROWS",
#   #         "startIndex": (7+len(SVFXStudentData)),
#   #         "endIndex": 55
#   #       }
#   #     }
#   #   }
#   #   ],


# # "sheetId": sheetId,

# # body = {
# #   "range": studentRange,
# #   "majorDimension": "ROWS",
# #   "values": [
# #     ["Item", "Cost", "Stocked", "Ship Date"],
# #     ["Wheel", "$20.50", "4", "3/1/2016"],
# #     ["Door", "$15", "2", "3/15/2016"],
# #     ["Engine", "$100", "1", "30/20/2016"],
# #     ["Totals", "=SUM(B2:B4)", "=SUM(C2:C4)", "=MAX(D2:D4)"]
# #   ]
# # }



# print "Trying to update Student Values"
# SERVICE.spreadsheets().values().update(spreadsheetId=ModuleMarkSheet['id'], range=studentRange, valueInputOption='USER_ENTERED', body=body).execute()
# print "Updating Student Values Complete"




# # print "Deleting out spare rows"
# #Some Operations seem to be easier using gspread, so lets get that authenticated and work with that


# body =  {"requests": [
#     {
#     "deleteDimension": {
#         "range": {
#         "sheetId" : 404434578,
#         "dimension": "ROWS",
#         "startIndex": (studentStartRow+len(SVFXStudentData) - 1),
#         "endIndex": studentEndRow
#         }
#       }
#     }
#     ]
#     }

# print ("Trying to Delete Rows)")
# print ("studentStartRow " + str(studentStartRow))
# print ("studentData " + str(len(SVFXStudentData)))


# SERVICE.spreadsheets().batchUpdate(spreadsheetId=ModuleMarkSheet['id'], body = body).execute()



##########################################################Take XML File and extract student and module data######################################################################
# tree = ET.parse('Resources\SFX6000.xml')
# root = tree.getroot()


# print ("COURSE DATA")
# print ("Course Name : " + root.get('Textbox12'))
# print ("Course Code : " + root.get('Textbox4'))
# print ("Course Tutor : " + root.get('Textbox16'))
# print ("Module Semester 1 : " + root.get('Textbox23'))
# print ("Module Year : " + root.get('Textbox20'))

# studentStartRow = 7
# studentEndRow = 98


# print ("\nSTUDENT LIST\n")
# SVFXStudents = []
# SVFXStudentData = []

# for student in root[0][0]:
# 	# if student.get('courseName') == "BSc (Hons) Visual Effects for Film and Television":
# 	# if student.get('courseName') == "BDes(Hons) Special Effects for Film and Television":
# 		SVFXStudents.append(student)

# print "SVFX Students  : " + str(SVFXStudents)
# for student in SVFXStudents:
# 	eachStudentList = [student.get('BoltonID'), student.get('contactEMail'), student.get('forename1'), student.get('surname')]
# 	SVFXStudentData.append(eachStudentList)

# print "Student Count : " + str(len(SVFXStudentData))


# ################################################################# Use creds to create a client to interact with the Google Drive API #########################################################################
# SCOPES = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/spreadsheets']
# CLIENT_SECRET = 'resources/client_secret.json'

# store = file.Storage('storage.json')
# credz = store.get()
# if not credz or credz.invalid:
# 	flow = client.flow_from_clientsecrets(CLIENT_SECRET, SCOPES)
# 	credz = tools.run_flow(flow, store)

# # Build a service, but the type of service that you build will have different methods and properties. In this cause we are building a drive service, so that we can do file operations on the drive
# SERVICE = discovery.build('drive', 'v2', http=credz.authorize(Http()))


# for i in SERVICE.files().list().execute()['items']:
#   print("File: " + str(i["title"]))

# print "Setting up New Mark Sheet"

# #This is the drive ID for Master Spread sheet that we want to copy. Update this ID if we use a new template file 
# masterMarkSheet_ID = "1BWfNFIPcPvinEfaSYvVvun3QfmwwYNoKeprseXU7uh8"

# #Find the Root Folder ID - This returns an JSON (I think) where root['rootFolderId'] will return to ID of the top level folder on the goodgle drive
# root = SERVICE.about().get().execute()  #This will get the root of your Folder
# folderUrlID = "1EFHIP6aSWv5Rmot7a65b9fXi-anWyumc"  #This is the id in the url to make sure that we copy the marksheet to the correct shared folder.... 

# #When creating a new file you can pass it a JSON full of parameters that allow you to control aspects of that file
# # copied_file = {'title': "NewMarkSheet", 'parents': [{'id': root['rootFolderId']}]}
# copied_file = {'title': "NewMarkSheet_badger", 'parents': [{'id': folderUrlID}]}


# print "Trying to Copy Data across to new sheet"

# #Call the files.cop() method which works for this kind of drive service - the return object has a dictionary that we can reference the id from using ModuleMarkSheet['id']
# ModuleMarkSheet = SERVICE.files().copy(fileId=masterMarkSheet_ID, body=copied_file).execute()


# print ("Marking Sheet File ID : " + ModuleMarkSheet['id'])
# pprint.pprint(SERVICE.permissions().list(fileId = ModuleMarkSheet['id']).execute())
# #Adjust the permissions of this new file so that we can edit it later!

# perm = {
#     'type': 'user',
#     'role': 'reader',
#     'value': 'tangotimetable@gmail.com'
#     }

# # SERVICE.permissions().insert(fileId = ModuleMarkSheet['id'], body=perm).execute()
 

# def callback(request_id, response, exception):
#     if exception:
#         # Handle error
#         print exception
#     else:
#         print "Permission Id: %s" % response.get('id')


# from apiclient import errors

# def print_permission_id_for_email(service, email):
#   """Prints the Permission ID for an email address.

#   Args:
#     service: Drive API service instance.
#     email: Email address to retrieve ID for.
#   """
#   try:
#     id_resp = service.permissions().getIdForEmail(email=email).execute()
#     print id_resp['id']
#     return id_resp['id']
#   except errors.HttpError, error:
#     print 'An error occurred: %s' % error


# permId = print_permission_id_for_email(SERVICE, "tangotimetable@gmail.com")



# def retrieve_permissions(service, file_id):
#   """Retrieve a list of permissions.

#   Args:
#     service: Drive API service instance.
#     file_id: ID of the file to retrieve permissions for.
#   Returns:
#     List of permissions.
#   """
#   try:
#     permissions = service.permissions().list(fileId=file_id).execute()
#     print("Persmission: " + str(permissions.get('items', []))) 
#     return permissions.get('items', [])
#   except errors.HttpError, error:
#     print 'An error occurred: %s' % error
#   return None


# # retrieve_permissions(SERVICE,ModuleMarkSheet)


# def insert_permission(service, file_id, value, perm_type, role):
#   """Insert a new permission.

#   Args:
#     service: Drive API service instance.
#     file_id: ID of the file to insert permission for.
#     value: User or group e-mail address, domain name or None for 'default'
#            type.
#     perm_type: The value 'user', 'group', 'domain' or 'default'.
#     role: The value 'owner', 'writer' or 'reader'.
#   Returns:
#     The inserted permission if successful, None otherwise.
#   """
#   new_permission = {
#       'value': value,
#       'type': perm_type,
#       'role': role,
#       'id' : permId
#   }
#   try:
#     return service.permissions().insert(
#         fileId=file_id, body=new_permission).execute()
#   except errors.HttpError, error:
#     print 'An error occurred: %s' % error
#   return None


# # insert_permission(SERVICE,ModuleMarkSheet, "tangotimetable@gmail.com", "user", "organizer")

# batch = SERVICE.new_batch_http_request(callback=callback)
# print("Batch: " + str(batch) )

# user_permission = {
#     'type': 'user',
#     'role': 'writer',
#     'value ': 'tangotimetable@gmail.com',
#     'id' : permId
#     }


# batch.add(SERVICE.permissions().insert(
#         fileId=ModuleMarkSheet,
#         body=user_permission,
#         fields = 'id'
# ))

# batch.execute()


# # help(SERVICE.permissions().create())
# #First get the permission:
# # id_resp = SERVICE.permissions().getIdForEmail(email='uobmarking@uob-marking.iam.gserviceaccount.com').execute()
# # print "Permission ID : " + str(id_resp)
# # SERVICE.permissions().update(fileId= ModuleMarkSheet['id'], body = user_permission, permissionId=id_resp['id'] )

# ############################################################################################# NOW WRITE THE STUDENT DATA OUT TO THE NEW SHEET ##################################################################






# gScope = ['https://spreadsheets.google.com/feeds']
# gCreds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', gScope) 
# client = gspread.authorize(gCreds)

# # help(client)



# # help(client)
# print "New Spread Sheet is : " + str(ModuleMarkSheet['id'])
# gModuleMarkSheet = client.open_by_key(ModuleMarkSheet['id'])
# # gModuleMarkSheet = client.open("NewMarkSheet")


# for r in range((studentStartRow+len(SVFXStudentData)), 55):
# 	gModuleMarkSheet.delete_row(r)


# deleteRange = "A" + str((studentStartRow+len(SVFXStudentData))) + ":D100"
# print "Delete Range : " + deleteRange




#############################################################################################################################CREATING A FOLDER IN GOOGLE DRIVE
# def createRemoteFolder(self, folderName, parentID = None):
#     # Create a folder on Drive, returns the newely created folders ID
#     body = {
#       'name': folderName,
#       'mimeType': "application/vnd.google-apps.folder"
#     }
#     if parentID:
#         body['parents'] = [parentID]
#     root_folder = drive_service.files().insert(body = body).execute()
#     return root_folder['id']