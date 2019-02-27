#!/usr/local/bin/python3.6
# pip install pycodestyle
# edit $HOME/.config/pycodestyle
# add this
#
#[pycodestyle]
#max-line-length = 120


import name_dictionary

import os
import re
import subprocess
import delegator


def generate_drive_credential():

    from apiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools

    SCOPES = 'https://www.googleapis.com/auth/drive.readonly.metadata'
    store = file.Storage('/Users/teacher/PycharmProjects/untitled/1.040/credentials_drive.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = discovery.build('drive', 'v3', http=creds.authorize(Http()))



def generate_sheets_credential():


    from apiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools

    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('/Users/teacher/PycharmProjects/untitled/1.040/credentials_sheets.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/Users/teacher/PycharmProjects/untitled/1.040/google_sheets_client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service

def generate_drive_credential():

    from apiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools

    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('/Users/teacher/PycharmProjects/untitled/1.040/credentials_drive.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('/Users/teacher/PycharmProjects/untitled/1.040/google_drive_client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    return service    




service_sheets = generate_sheets_credential()
service_drive = generate_drive_credential()

for filename in os.listdir('.'):
    if filename.endswith('.py'):
        for key in name_dictionary.name_dict:
            match = re.match('.+' + key + '.+', filename) 
            if match:

                # construct query here
                rubric_file = name_dictionary.name_dict[key] + ' - Python 2.020 - Rubric'
                query = 'name=' + "'" + rubric_file + "'"

                # Google drive API to get ID of file
                page_token = None
                response = service_drive.files().list(q=query,
                                      spaces='drive',
                                      fields='nextPageToken, files(id, name)',
                                     pageToken=page_token).execute()
                for file in response.get('files', []):



                    print("File is {}  id is {}".format(file.get('name'), file.get('id')))
                    spreadsheet_id = file.get('id')
                    
                    datapoints = []
                    value = ''


                    # Find whether or not there is a help
                    cmd = 'grep "#" ' + filename + ' | grep help | wc -l  '
                    c = delegator.run(cmd)
                    help_comments = int(c.out)
                    
                    # sheets API to make edit to file if help_comment is found                              
                    if help_comments > 0:
                        value = '0'
                    else:
                        value = '-5'
                   
                    # Edit Google sheet for helps
                    range_name = 'Rubric' + '!B4'    
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
              
                    # Find number of PEP8 errors
                    cmd = 'pycodestyle  --max-line-length=120  --ignore=E305,E226 ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    side_errors = int(c.out)
                    side_errors = min(side_errors, 14)
                    side_errors *= -1

                    # sheets API to make edit to file for number of errors
                    value =  str(side_errors)
                    # Edit Google sheet for PEP8 errors (B9)
                    range_name = 'Rubric' + '!B9'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # Check that divides by 2 correctly (float)
                    filename_output = filename + '.out'
                    cmd = 'python3 ' + filename + ' < /users/teacher/PycharmProjects/untitled/2.020/2.020-1.in > ' + filename_output
                    c = delegator.run(cmd)
                    with open(filename_output, 'r') as myfile:
                        outfile_data = myfile.read()
               
                    search_object = re.search(r"49.5", outfile_data, re.X | re.M | re.S)

                    
                    # sheets API to make edit to file for dividing by 2 correctly
                    if not search_object:
                        value = '-15'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F5'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
                    
                    # Check that divides by 2 correctly (integer)
                    search_object = re.search(r"49$", outfile_data, re.X | re.M | re.S)
                    
                    # Sheets API to edit to file for divide by 2 correctly (integer)
                    if not search_object:
                        value = '-15'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F6'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
                        
                    # Check that input works for something like 3.5
                    filename_output = filename + '.out'
                    cmd = 'python3 ' + filename + ' <  /users/teacher/PycharmProjects/untitled/2.020/2.020-2.in > ' \
                        + filename_output
                    c = delegator.run(cmd)
                    with open(filename_output, 'r') as myfile:
                        outfile_data = myfile.read()

                    search_object1 = re.search(r"49.75", outfile_data, re.X | re.M | re.S)
                    search_object2 = re.search(r"49", outfile_data, re.X | re.M | re.S)

                    # Sheets API to edit to file for working for 3.5 or not
                    if search_object1 and search_object2:
                        value = '0'
                    else:
                        value = '-6'
                    range_name = 'Rubric' + '!F7'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    body = {'valueInputOption': 'USER_ENTERED',
                            'data':datapoints}
                    result = service_sheets.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                                body=body).execute()
