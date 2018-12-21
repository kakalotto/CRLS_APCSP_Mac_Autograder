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

name_dict = {'samyebio':'SIEM YEBIO',}



service_sheets = generate_sheets_credential()
service_drive = generate_drive_credential()

for filename in os.listdir('.'):
    if filename.endswith('.py'):
        for key in name_dict:
            match = re.match('.+' + key + '.+', filename) 
            if match:

                # construct query here
                rubric_file = name_dict[key] + ' - Python 1.060 - Rubric'
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


                    # Find whether or not there is a help
                    cmd = 'grep "#" ' + filename + ' | grep help | wc -l  '
                    c = delegator.run(cmd)
                    help_comments = int(c.out)
                    
                    # sheets API to make edit to file if help_comment is found                              
                    if help_comments > 0:
                        # sheets API to make edit to file for helps
                        p_body = { 'values': [['0']] }
                    else:
                        p_body = { 'values': [['-5']] }
                   
                    # Edit Google sheet for helps
                    range_name = 'Rubric' + '!B4'    
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                               range=range_name,
                                                                               valueInputOption='USER_ENTERED',
                                                                               body=p_body).execute()

                    # Find number of PEP8 errors
                    cmd = 'pycodestyle ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    side_errors = int(c.out)
                    side_errors = min(side_errors, 14)
                    side_errors *= -1

                    # sheets API to make edit to file for number of errors
                    p_body = { 'values': [[side_errors]] }
                    # Edit Google sheet for PEP8 errors (B9)
                    range_name = 'Rubric' + '!B9'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()

                    # Check that asks at least 5 questions
                    cmd = 'grep "input" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    inputs = int(c.out)
                    
                    # sheets API to make edit to file for at least 5 questions
                    if inputs < 5:
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }
                    range_name = 'Rubric' + '!F4'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()

                    # Check that inputs are named after part of speech
                    cmd = 'grep -E "verb|noun|adjective|adverb|preposition" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    parts_of_speech = int(c.out)
                    
                    # Sheets API to test for parts of speech
                    if parts_of_speech < 5:
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }
                    range_name = 'Rubric' + '!F5'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()
                        
                    # Check for at least 1 print statement
                    cmd = 'grep "print" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    prints = int(c.out)
                    if prints < 1:
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }
                    range_name = 'Rubric' + '!F6'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()
                        
                    # Check for less than 3 print statement
                    if prints > 3:
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }
                    range_name = 'Rubric' + '!F7'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()

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
                        p_body = { 'values': [['0']] }
                    else:
                        p_body = { 'values': [['-15']] }
                    range_name = 'Rubric' + '!F8'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()
                    
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
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }
                    range_name = 'Rubric' + '!F9'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()
                        
 
                    
                    
                    

