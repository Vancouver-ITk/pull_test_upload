# wire_pull_upload
GUI for upload of wire pull test data.

# Dependencies

Depends on the GUI library tkinter, numpy, itkdb and requests.

# Installation

Only the dependencies need to be installed.

Windows:

```
pip install tk numpy itkdb requests
```

MAC:

```
pip3 install tk numpy itkdb requests
```

CENTOS: 

```
yum install python3-tkinter

pip3 install numpy requests itkdb --user
```

# Edits

At the top of the script there are a few variables which may need to be edited for proper upload. These are:

```
# VARIABLES TO EDIT
PULL_TEST_NAME = "Dage Series 4000"
WIRE_BONDER = "Delvoteck G5"
INSTITUTE = 'TRIUMF_SENSORS'
```
The variables will depend on the specfic pull tester, bonder and site using this script.

# Running

To run the file, open a terminal and navigate to the folder containing this program and enter the following command:

Windows:

```
python wire_pull_upload.py
```

Linux/MAC:

```
python3 wire_pull_upload.py
```

The GUI will pop up and request that you find a file, enter the DB serial number, the run number and if problems have occured or not. Then, the file can be uploaded to the database

