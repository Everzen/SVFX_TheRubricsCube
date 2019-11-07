import json


markingDataJsonFile = "resources/MarkingData.json"

#~~~~~~~~~~~~~~~~~~~~~~FUNCTIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def grabInfo(infoType, jsonFile = markingDataJsonFile):
    with open(jsonFile) as json_file:
            info = json.load(json_file)
            return info[infoType]
