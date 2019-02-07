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

quiz_spreadsheet_id ='1R50sZBSdQNeafeRAZ9GjFaNvNeOyC2zPjd5uSxyyvis'
# Read from daily sheet
RANGE_NAME = 'Form Responses 1!B2:C48'
result = service_sheets.spreadsheets().values().get(majorDimension='COLUMNS',
                                                    spreadsheetId=quiz_spreadsheet_id,
                                                    range=RANGE_NAME, ).execute()
columns = result.get('values', [])
emails = columns[0]
scores = columns[1]
#for score in scores:
#    print(score)
#    score_list = score.split('/')
#    percent = float(score_list[0]) / float(score_list[1])
#    print(percent)
#for email in emails:
#    print(email)

completed = []
for index, email in enumerate(emails, 0):

    # Get filename 
    print("trying this email " + str(email) + " " + str(index))
    rubric_file = names_to_emails.names_to_emails[email] + ' - Python 2.020 - Rubric'
    query = 'name=' + "'" + rubric_file + "'"

    # Google drive API to get ID of file
    page_token = None
    response = service_drive.files().list(q=query,
                                          spaces='drive',
                                          fields='nextPageToken, files(id, name)',
                                          pageToken=page_token).execute()
   
    # Found the file
    for file in response.get('files', []):
        print("File is {}  id is {}".format(file.get('name'), file.get('id')))
        completed.append(emails)
        
        # Get the file ID and write to it
        spreadsheet_id = file.get('id')
        score_list = scores[index].split('/')
        percent = float(score_list[0]) / float(score_list[1])
        print(percent)

        score = -20 * (1 - percent)
        print("the score is this " + str(score))

        p_body = { 'values': [[score]] }
        
        # Sheets API to update score (B5)
        range_name = 'Rubric' + '!B5'
        result = service_sheets.spreadsheets().values().update(spreadsheetId=spreadsheet_id,
                                                               range=range_name,
                                                               valueInputOption='USER_ENTERED',
                                                               body=p_body).execute()
        


