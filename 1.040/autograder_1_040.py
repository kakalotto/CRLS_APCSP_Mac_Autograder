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

name_dict = {'liam':'LIAM PACE',}



service_sheets = generate_sheets_credential()
service_drive = generate_drive_credential()

for filename in os.listdir('.'):
    if filename.endswith('.py'):
        for key in name_dict:
            match = re.match('.+' + key + '.+', filename) 
            if match:

                # construct query here
                rubric_file = name_dict[key] + ' - Python 1.040 - Rubric'
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
                        p_body = { 'values': [['-2.5']] }
                   
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
                    side_errors = min(side_errors, 7)
                    side_errors *= -1

                    # sheets API to make edit to file for number of errors
                    p_body = {
                        'values': [[side_errors]]
                        }

                    # Edit Google sheet for PEP8 errors (B9)
                    range_name = 'Rubric' + '!B9'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()

                    # check for 3 questions
                    cmd = 'grep "input" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    inputs = int(c.out)
                    if inputs < 3:
                        # sheets API to make edit to file for helps
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }
                    
                    # Sheets API to make edit for 3 questions (F4)
                    range_name = 'Rubric' + '!F4'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()

                    # Check for 3 questions output in correct order
                    filename_output = filename + '.out'
                    cmd = '/usr/local/bin/python3.6 ' + filename + ' < 1.040\.in > '\
                        + filename_output
                    c = delegator.run(cmd)
                    
                    with open(filename_output, 'r') as myfile:
                        outfile_data = myfile.read()
                    
                    search_object = re.search(r".+ "
                                              r"a1 "
                                              r".+ "
                                              r"a2 "
                                              r".+ "
                                              r"a3 "
                                              r".+ "
                                              , outfile_data, re.X|re.M|re.S)
                    if not search_object or c.err:
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }
                   
                    # Sheets API to make edit for reply for 3 questions (F5)
                    range_name = 'Rubric' + '!F5'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()

                    #  Check for part 2 asks 3 more questions, 6 total
                    cmd = 'grep "input" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    inputs = int(c.out)
                    if inputs < 6:
                        p_body = { 'values': [['-5']] }                                
                    else:
                        p_body = { 'values': [['0']] }                                


                    # Sheets API to make edit for at least 6 inputs (F6)
                    range_name = 'Rubric' + '!F6'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()

                    # Check for asking variable questions
                    process_grep1 = subprocess.Popen(['grep', "input([\"']", filename], stdout=subprocess.PIPE)
                    process_wc = subprocess.Popen(['wc', '-l'], stdin=process_grep1.stdout, stdout=subprocess.PIPE)
                    process_grep1.wait()
                    process_grep1.stdout.close()
                    output_string = str(process_wc.communicate()[0])
                    match_object = re.search(r"([0-9]+)", output_string)
                    inputs_variable = int(match_object.group())
                    if inputs_variable > 4  :
                        p_body = { 'values': [['-5']] }                                
                    else:
                        p_body = { 'values': [['0']] }             

                    # Sheets API to make edit for question in variable (F7)
                    range_name = 'Rubric' + '!F7'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()                    

                    # Check for 6 outputs in correct order given 6 inputs
                    cmd = '/usr/local/bin/python3.6 ' + filename + ' < 1.040\.in > '\
                        + filename_output
                    c = delegator.run(cmd)

                    search_object = re.search(r".+ "
                                              r"a1 "
                                              r".+ "
                                              r"a2 "
                                              r".+ "
                                              r"a3 "
                                              r".+ "
                                              r"b2 "
                                              r".+ "
                                              r"b3 "
                                              r".+ "
                                              r"b1"
                                              , outfile_data, re.X|re.M|re.S)
                    if not search_object or c.err:
                        p_body = { 'values': [['-5']] }
                    else:
                        p_body = { 'values': [['0']] }


                    # Sheets API to make edit for at 6 inputs with outputs in correct order (F8)
                    range_name = 'Rubric' + '!F8'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()
                    
                    

