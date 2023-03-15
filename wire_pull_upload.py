"""GUI for the upload of wire pull tests in Vancouver
   Allows the user to find a csv file with data from a 
   pull test and upload the data to the database. Data is 
   coverted to the following JSON format for upload:
   
   {
  "component": "...",
  "testType": "PULL_TEST",
  "institution": "...",
  "runNumber": "...",
  "date": "2021-11-05T16:16:47.434Z",
  "passed": true,
  "problems": false,
  "properties": {
    "OPERATOR": "QRYCLARQLMZEXZRIXDATWHRYPMMJGO",
    "PULL_TEST_MACHINE": "PAGETVPMGSOMLEETYYUKFNLKVAYGAW",
    "NUMBER_WIRES": 488,
    "WIRE_BOND_MACHINE": "XTWQHCNQGZULUEWZVARSGVJNWCRBOP"
  },
  "results": {
    "MEAN": 127.7964750419729,
    "PULL_STRENGTH": [
      737.8370188295532,
      737.8370188295532
    ],
    "PULL_GRADE": [
      285,
      285
    ],
    "STANDARD_DEVIATION": 68.45168799516404,
    "TOO_LOW": 531,
    "MINIMUM_STRENGTH": 18.99986915174358,
    "MAXIMUM_STRENGTH": 227.65088444746286,
    "HEEL_BREAKS": 164.32832269724784,
    "FILE": null
  }
} 
  
   At this point, the file is defaulted to null and the user
   must decide if the test passes and if there are any problems."""

import numpy as np
import csv
import tkinter as tk
import os
from tkinter import filedialog
import itkdb
from datetime import datetime

# VARIABLES TO EDIT
PULL_TEST_NAME = "Dage Series 4000"
WIRE_BONDER = "Delvotec G5"
INSTITUTE = 'SFU'

# CONSTANTS
DATA_START_ROW = 0
THRESHOLD = 5
SERIES_ROW = 0
DATE_ROW = 1
TIME_ROW = 2
OPERATOR_ROW = 3
HEADER_COL = 1
GRADES_ROW = 2
STRENGTHS_ROW = 3
ENTRY_X = 100
ENTRY_Y = 20
MIN_BONDS = 0
MIN_MEAN = 8.0
MIN_HEELS = 0.9
MAX_ST_DEV = 1.5
MIN_PULL = 5.0
DATA_DICT = dict()


def less_than_threshold(pull_strengths):
    """Compute the number of wire pulls lower than the threshold (5g)"""
    num_pulls = 0
    for pull_strength in pull_strengths:
        if pull_strength < THRESHOLD:
            num_pulls += 1
    return num_pulls
    
    
def get_percent_heel_breaks(pull_grades):
    """Gets the percentage of wire pulls which broke at the heel
    heel breaks are given a grade of 1 or 2 by the Dage 4000 this 
    may need to be modified based on the machine being used."""
    count = 0
    for pull_grade in pull_grades:
        if pull_grade == 1 or pull_grade == 2 or pull_grade == 3:
            count += 1
    return count / len(pull_grades) * 100
    
    
def get_date(filename):
    """Gets the date of a file in ISO8601 format"""
    creation_time = os.path.getctime(filename) 
    creation_time = datetime.utcfromtimestamp(creation_time)
    return creation_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    
def read_file(filename):
    """Extracts the data from the pull test file.
    
       Input: filename - The name of the pull test file
       
       Outputs: series - The name of the wire bonder series (string)
                date - The date of the pull test (string - mm/dd/yyyy)
                time - The time of the pull test (string - hh:mm:ss)
                operator - Name of the operator (string)
                pull_number - Array of the pull index (np.array)
                pull_grade - Array of the pull grade (np.array)
                pull_strength - Array of wire pull results in g (np.array)"""  
    DATA_DICT = dict() #Reset the dictionary.
              
    with open(filename) as data_file:
        file_reader = csv.reader(data_file)
        data_array = list(file_reader)
    #Skip possible whitespace
    while data_array[0] == []:
        data_array = data_array[1:]
        print(data_array)
    
    operator = data_array[OPERATOR_ROW][HEADER_COL]
    date_time = get_date(filename)
    
    pull_grades, pull_strengths = ([] for i in range(2))
    for i in range(9,len(data_array)):
        pull_grades.append(int(data_array[i][GRADES_ROW]))
        pull_strengths.append(float(data_array[i][STRENGTHS_ROW]))
        
    pull_strengths = np.array(pull_strengths)
    
    return date_time, operator, pull_grades, pull_strengths

def get_file_data():
    """Gets the data file from the operator, extracts the data and formats it into 
       a dictionary for upload."""
    file_path = filedialog.askopenfilename(title = 'Select Data File')
    date_time, operator, pull_grades, pull_strengths = read_file(file_path)
    percent_heels = get_percent_heel_breaks(pull_grades)
    mean = np.mean(pull_strengths)
    min_pull = np.min(pull_strengths)
    max_pull = np.max(pull_strengths)
    num_under_threshold = less_than_threshold(pull_strengths)
    num_wires = len(pull_strengths)
    standard_dev = np.sqrt(np.var(pull_strengths))

    #Set the values in the GUI
    operator_display.set(operator)
    wb_machine_display.set(WIRE_BONDER)
    series_display.set(PULL_TEST_NAME)

    num_wires_display.set(num_wires)
    num_under_thresh_display.set(num_under_threshold)
    percent_heels_display.set(f"{percent_heels:0.2f}")

    min_dispaly.set(f"{min_pull:0.2f}")
    max_display.set(f"{max_pull:0.2f}")
    mean_display.set(f"{mean:0.2f}")
    st_dev_display.set(f"{standard_dev:0.2f}")

    properties = dict()
    properties["OPERATOR"] = operator
    properties["PULL_TEST_MACHINE"] = PULL_TEST_NAME
    properties["NUMBER_WIRES"] = num_wires
    properties["WIRE_BOND_MACHINE"] = WIRE_BONDER

    results = dict()
    results["MEAN"] = mean
    results["PULL_STRENGTH"] = pull_strengths.tolist()
    results["PULL_GRADE"] = pull_grades
    results["STANDARD_DEVIATION"] = standard_dev
    results["TOO_LOW"] = num_under_threshold
    results["MINIMUM_STRENGTH"] = min_pull
    results["MAXIMUM_STRENGTH"] = max_pull
    results["HEEL_BREAKS"] = percent_heels
    results["FILE"] = file_path
    # Fill the global data dictionary 
    DATA_DICT["component"] = ""
    DATA_DICT["testType"] = "PULL_TEST"
    DATA_DICT["institution"] = INSTITUTE
    DATA_DICT["runNumber"] = ""
    DATA_DICT["date"] = date_time
    if min_pull >= MIN_PULL and percent_heels >= MIN_HEELS and mean >= MIN_MEAN and standard_dev <= MAX_ST_DEV and num_wires >= MIN_BONDS:
        DATA_DICT["passed"] = True
        output_text.set("Test passed all parameters. Please upload data.")
    else: 
        DATA_DICT["passed"] = False
        output_text.set("Test failed on one or more parameters. Please upload data.")
    DATA_DICT["problems"] = ""
    DATA_DICT["properties"] = properties
    DATA_DICT["results"] = results
    print(DATA_DICT)

def save_data():
    """Saves the data to the database"""

    if serial_number.get() == "" or run_num.get() == "" or problems_box.curselection() == () or DATA_DICT == {}:
        output_text.set('Please ensure all mandatory values have been entered and a data file has been choosen. Then try again.')
        return 
    else:
        if problems_box.get(problems_box.curselection()[0]) == "Yes":
             DATA_DICT["problems"]  = True
        else: 
            DATA_DICT["problems"] = False
    DATA_DICT["component"] = serial_number.get()
    DATA_DICT["runNumber"] = run_num.get()

    db_passcode_1 =  db_pass_1.get()
    db_passcode_2 =  db_pass_2.get()

    try :
        user = itkdb.core.User(accessCode1 = db_passcode_1, accessCode2 = db_passcode_2)
        client = itkdb.Client(user=user)
    except:
        output_text.set("Set passcodes are incorrect. Try again")
        return
    
    print("got passed client init!")

    result= client.post("uploadTestRunResults", json = DATA_DICT)

    if (('uuAppErrorMap')=={}):
        output_text.set('Upload of Test and File Succesful!')
    elif (('uuAppErrorMap'))[0]=='cern-itkpd-main/uploadTestRunResults/':
        output_text.set("Error in Test Upload.")
    elif list(('uuAppErrorMap'))[0]=='cern-itkpd-main/uploadTestRunResults/componentAtDifferentLocation':
        output_text.set('Component cannot be uploaded as is not currently at the given location')
    elif (('uuAppErrorMap'))[0]=='cern-itkpd-main/uploadTestRunResults/unassociatedStageWithTestType':
        output_text.set('Component cannot be uploaded as the current stage does not have this test type. You will need to update the stage of the component on the ITK DB. Note that due to a bug on the ITK DB, you might also get this error if the component is not at your current location.')
    elif (('uuAppErrorMap'))[0]!='cern-itkpd-main/uploadTestRunResults/':
        output_text.set("Upload of Test Succesful!")
    else:
        output_text.set('Error!')
            

    #upload the raw data file
    if (('uuAppErrorMap')[0]!='cern-itkpd-main/uploadTestRunResults/'):
        ###Upload the attached file!
        testRun = result['testRun']['id']
        file_path = DATA_DICT['results']['FILE']
        print(file_path)
        file_name = os.path.basename(file_path)
        print(file_name)
        dataforuploadattachment={
                "testRun": testRun,
                "type": "file",
                "title": file_name, 
                "description": "Automatic Attachment of Original Data File", 
            }
        attachment = {'data': (file_name, open(file_path, 'rb'), 'text')}
        client.post("createTestRunAttachment", data = dataforuploadattachment, files = attachment)
        output_text.set("Upload of test and attachment completed.")
    # try:
    
    #     db_session = ITkPDSession()
    #     db_session.authenticate(db_passcode_1, db_passcode_2)
    # except:
    #     output_text.set("Ensure passwords are correct before attempting to save to the database.")
    #     return
    
    
    # db_session.doSomething("uploadTestRunResults", "POST", DATA_DICT)

    # testing with Halfmoon: 20USES50900418

# GUI Definition
root = tk.Tk()
frame = tk.Frame(root, height = 500, width = 500)
frame.pack()

#Define String Variables of GUI
serial_number = tk.StringVar()
operator_display = tk.StringVar()
wb_machine_display = tk.StringVar()
series_display = tk.StringVar()

num_wires_display = tk.StringVar()
num_under_thresh_display = tk.StringVar()
percent_heels_display = tk.StringVar()

min_dispaly = tk.StringVar()
max_display = tk.StringVar()
mean_display = tk.StringVar()
st_dev_display = tk.StringVar()

pull_strengths_display = tk.StringVar()
pull_grades_display = tk.StringVar()
date_time_display = tk.StringVar()

run_num = tk.StringVar()
output_text = tk.StringVar()

db_pass_1 = tk.StringVar()
db_pass_2 = tk.StringVar()

#Define the boxes to dontain the string variables.
title = tk.Label(frame, text = 'Wire Pull Test Upload GUI', font = ('calibri', 18))
title.place(x = 115, y = 10 )

save_button = tk.Button(frame, text = "Save Data", command = lambda: save_data())
save_button.place(x = ENTRY_X + 115, y = ENTRY_Y + 400)

browser_button = tk.Button(frame, text = "Find File", command = lambda: get_file_data())
browser_button.place(x = ENTRY_X + 300, y = ENTRY_Y + 40)

problems_label = tk.Label(frame, text='Problems?')
problems_label.place(x = ENTRY_X + 50, y = ENTRY_Y + 200)
problems_box = tk.Listbox(frame, width = 5, relief = 'groove', height = '2')
problems_box.place(x = ENTRY_X + 110, y = ENTRY_Y + 200)
problems_box.insert(0,"Yes")
problems_box.insert(1,"No")

id_label = tk.Label(frame, text='SN')
id_label.place(x = ENTRY_X - 70, y = ENTRY_Y + 40)
id_box = tk.Entry(frame, textvariable = serial_number, justify = 'left' , width = 20)
id_box.place(x = ENTRY_X - 50 , y = ENTRY_Y + 40)

run_num_label = tk.Label(frame, text='Run Number')
run_num_label.place(x = ENTRY_X - 70, y = ENTRY_Y + 200)
run_num_box = tk.Entry(frame, textvariable = run_num, justify = 'left' , width = 5)
run_num_box.place(x = ENTRY_X + 5 , y = ENTRY_Y + 200)

operator_label = tk.Label(frame, text='Operator')
operator_label.place(x = ENTRY_X + 80, y = ENTRY_Y + 40)
operator_box = tk.Entry(frame, textvariable = operator_display, justify = 'left', width = 20)
operator_box.place(x = ENTRY_X + 135, y = ENTRY_Y + 40)

bonder_label = tk.Label(frame, text='Bonder')
bonder_label.place(x = ENTRY_X - 95, y = ENTRY_Y + 80)
bonder_box = tk.Entry(frame, textvariable = wb_machine_display, justify = 'left' , width = 20)
bonder_box.place(x = ENTRY_X - 50 , y = ENTRY_Y + 80)

series_label = tk.Label(frame, text='Tester')
series_label.place(x = ENTRY_X + 95, y = ENTRY_Y + 80)
series_box = tk.Entry(frame, textvariable = series_display, justify = 'left', width = 20)
series_box.place(x = ENTRY_X + 135, y = ENTRY_Y + 80)

num_wires_label = tk.Label(frame, text='Number of Wires')
num_wires_label.place(x = ENTRY_X - 70, y = ENTRY_Y + 120)
num_wires_box = tk.Entry(frame, textvariable = num_wires_display, justify = 'left' , width = 5)
num_wires_box.place(x = ENTRY_X + 25, y = ENTRY_Y + 120)

num_under_thresh_label = tk.Label(frame, text='Number under Threshold')
num_under_thresh_label.place(x = ENTRY_X + 70, y = ENTRY_Y + 120)
num_under_thresh_box = tk.Entry(frame, textvariable = num_under_thresh_display, justify = 'left', width = 5)
num_under_thresh_box.place(x = ENTRY_X + 210, y = ENTRY_Y + 120)

percent_heel_label = tk.Label(frame, text='% Heel Breaks')
percent_heel_label.place(x = ENTRY_X + 250, y = ENTRY_Y + 120)
percent_heel_box = tk.Entry(frame, textvariable = percent_heels_display, justify = 'left', width = 5)
percent_heel_box.place(x = ENTRY_X + 330, y = ENTRY_Y + 120)

min_label = tk.Label(frame, text='Min')
min_label.place(x = ENTRY_X - 70, y = ENTRY_Y + 160)
min_box = tk.Entry(frame, textvariable = min_dispaly, justify = 'left' , width = 5)
min_box.place(x = ENTRY_X - 40, y = ENTRY_Y + 160)

mean_label = tk.Label(frame, text='Mean')
mean_label.place(x = ENTRY_X + 20, y = ENTRY_Y + 160)
mean_box = tk.Entry(frame, textvariable = mean_display, justify = 'left', width = 5)
mean_box.place(x = ENTRY_X + 60, y = ENTRY_Y + 160)

max_label = tk.Label(frame, text='Max')
max_label.place(x = ENTRY_X + 120, y = ENTRY_Y + 160)
max_box = tk.Entry(frame, textvariable = max_display, justify = 'left', width = 5)
max_box.place(x = ENTRY_X + 150, y = ENTRY_Y + 160)

st_dev_label = tk.Label(frame, text='St.Dev')
st_dev_label.place(x = ENTRY_X + 210, y = ENTRY_Y + 160)
st_dev_box = tk.Entry(frame, textvariable = st_dev_display, justify = 'left', width = 5)
st_dev_box.place(x = ENTRY_X + 250, y = ENTRY_Y + 160)

db_pass_1_label = tk.Label(frame, text="AccessCode 1")
db_pass_1_label.place(x = ENTRY_X + 170, y = ENTRY_Y + 200)
db_pass_1_box = tk.Entry(frame, textvariable = db_pass_1, show='*', justify = 'left', width = 15)
db_pass_1_box.place(x = ENTRY_X + 250, y = ENTRY_Y + 200)

db_pass_2_label = tk.Label(frame, text="AccessCode 2")
db_pass_2_label.place(x = ENTRY_X + 170, y = ENTRY_Y + 230)
db_pass_2_box = tk.Entry(frame, textvariable = db_pass_2, show='*',  justify = 'left', width = 15)
db_pass_2_box.place(x = ENTRY_X + 250, y = ENTRY_Y + 230)

output_text_box = tk.Message(frame, textvariable = output_text, font = ('calibri', 10), width = 344, relief = 'sunken', justify = 'left')
output_text_box.place(x = ENTRY_X - 30, y = ENTRY_Y + 280)
output_text.set('Please enter the database serial number. Select \'Yes\' or \'No\' for if problems existed during testing and enter the run number.'
' Look for a data file using the \'Find File\' button to import data from an appropriate CSV.' 
'If everything looks correct, enter DB passwords and press  \'Save Data\' to upload to the database.' )

root.mainloop()

