#!/usr/local/bin/python3.6
# pip install pycodestyle
# edit $HOME/.config/pycodestyle
# add this
#
#[pycodestyle]
#max-line-length = 120

import names_to_emails
import os
import re
import subprocess
import delegator

def generate_sheets_credential():

    from apiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools

    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
    store = file.Storage('../1.040/credentials_sheets.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../1.040/google_sheets_client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))
    return service

def generate_drive_credential():

    from apiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools

    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('../1.040/credentials_drive.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('../1.040/google_drive_client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    return service    


service_sheets = generate_sheets_credential()
service_drive = generate_drive_credential()

quiz_spreadsheet_id ='1xpK29hu14BwuFDHSStDDj4p4Qhf_2LJYvFogarj8WPI'
for key in name_dictionary.name_dict:
            match = re.match('.+' + key + '.+', filename) 
            if match:

                # construct query here
                rubric_file = name_dictionary.name_dict[key] + ' - Python 1.020 - Rubric'
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


          
                    # sheets API to make edit to file if help_comment is found                              
                    if help_comments > 0:
                        # sheets API to make edit to file for helps
                        p_body = { 'values': [['0']] }
                    else:
                        p_body = { 'values': [['-2.5']] }
                   



                    # Sheets API to update score (B22)
                    range_name = 'Rubric' + '!B22'
                    result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
                                                                           range=range_name,
                                                                           valueInputOption='USER_ENTERED',
                                                                           body=p_body).execute()
                    
                    

