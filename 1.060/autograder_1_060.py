#!/usr/local/bin/python3.6
# pip install pycodestyle
# edit $HOME/.config/pycodestyle
# add this
#
#[pycodestyle]
#max-line-length = 120

import os
import re
import subprocess
import delegator

import name_dictionary

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
                rubric_file = name_dictionary.name_dict[key] + ' - Python 1.060 - Rubric'
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
                    cmd = 'pycodestyle ' + filename + ' | wc -l  '
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

                    # Check that asks at least 5 questions
                    cmd = 'grep "input" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    inputs = int(c.out)
                    
                    # sheets API to make edit to file for at least 5 questions
                    if inputs < 5:
                        value = '-5'
                    else:
                        value = '0'

                    range_name = 'Rubric' + '!F4'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)



                    # Check that inputs are named after part of speech
                    cmd = 'grep -E "verb|noun|adjective|adverb|preposition" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    parts_of_speech = int(c.out)
                    
                    # Sheets API to test for parts of speech
                    if parts_of_speech < 5:
                        value = '-5'
                    else:
                        value = '0'

                    range_name = 'Rubric' + '!F5'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
                        
                    # Check for at least 1 print statement
                    cmd = 'grep "print" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    prints = int(c.out)
                    if prints < 1:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F6'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
                        

                    # Check for less than 3 print statement
                    if prints > 3:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F7'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
                        
                    # Check that things are in correct order.  First 5 inputs show up in output)
                    filename_output = filename + '.out'
                    cmd = '/usr/local/bin/python3.6 ' + filename + ' < /users/teacher/PycharmProjects/untitled/1.060/1.060.in > ' \
                        + filename_output
                    c = delegator.run(cmd)
                    if c.err:
                        print('bad! You have an error somewhere in running program 5 inputs show up in output')
                    with open(filename_output, 'r') as myfile:
                        outfile_data = myfile.read()
                            
                    search_object_1 = re.search(r"a1", outfile_data, re.X | re.M | re.S)
                    search_object_2 = re.search(r"a2", outfile_data, re.X | re.M | re.S)
                    search_object_3 = re.search(r"a3", outfile_data, re.X | re.M | re.S)
                    search_object_4 = re.search(r"b1", outfile_data, re.X | re.M | re.S)
                    search_object_5 = re.search(r"b2", outfile_data, re.X | re.M | re.S)
                    if search_object_1 and search_object_2 and search_object_3 and search_object_4 and search_object_5:
                        value = '0'
                    else:
                        value = '-15'
                    range_name = 'Rubric' + '!F8'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # Check for 3 punctuations
                    filename_output = filename + '.out'
                    cmd = '/usr/local/bin/python3.6 ' + filename + ' < /users/teacher/PycharmProjects/untitled/1.060/1.060.in > ' \
                        + filename_output
                    c = delegator.run(cmd)
                    if c.err:
                        print('bad! You have an error somewhere in running program punctuations')
                        print(c.err)
                    with open(filename_output, 'r') as myfile:
                        outfile_data = myfile.read()
                    
                    num_periods = outfile_data.count('.')
                    num_questions = outfile_data.count('?')
                    num_exclamations = outfile_data.count('!')
                    num_punctuations = num_periods + num_questions + num_exclamations
                    if num_punctuations < 3:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F9'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    body = {'valueInputOption': 'USER_ENTERED',
                            'data':datapoints}
                    result = service_sheets.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                                body=body).execute()
                    

                    
                    
                    

