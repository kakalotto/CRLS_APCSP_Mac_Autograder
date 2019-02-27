#!/usr/local/bin/python3.6
# pip install pycodestyle
# edit $HOME/.config/pycodestyle
# add this
#
#[pycodestyle]
#max-line-length = 120

# NOTE TO SELF - RUBRIC HAD AN EXTRA SPACE IN S2 2019.  THIS WAS FIXED SO NEXT TIME 
# REMOVE EXTRA SPACE FROM LINE 79

import name_dictionary

import os
import re
import subprocess
import delegator
import glob

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

def extract_functions(orig_file):
    import re
    outfile_name = orig_file.replace('.py', '.functions.py')
    outfile = open(outfile_name, 'w')
    with open(orig_file, 'r', encoding='utf8') as infile:
        line = True
        while line:
#            print("starting over looking for function")
#            print('reading this ' + str(line))
            line = infile.readline()
            start_def = re.search("^(def) \s+ .+ " , line,  re.X | re.M | re.S)
            if start_def:
#                print("entering function!")
#                print('writing this' + str(line))
                outfile.write(line)
#                print("reading this" + str(line))
                #                   line = infile.readline()
                #                   inside_function = re.search("^\s+ .+ " , line,  re.X | re.M | re.S)
                inside_function = True
                while inside_function:
#                    print('reading this ' + str(line))
                    line = infile.readline()
                    inside_function = re.search("^(\s+ | \# ) .+ " , line,  re.X | re.M | re.S)
                    if inside_function:
#                        print("writing this inside function " + str(line))
                        outfile.write(line)
                outfile.write(line)

# Clear out old files
for file in glob.glob('*functions*'):
    print(file)
    os.remove(file)

for filename in os.listdir('.'):
    if filename.endswith('.py'):
        for key in name_dictionary.name_dict:
            match = re.match('.+' + key + '.+', filename)
            match2 = re.match('function', filename)
            if match and not match2:
                # construct query here
                print(filename)
                rubric_file = name_dictionary.name_dict[key] + ' - Python 3.020 Birthday and random card - Rubric'
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
                    cmd = 'pycodestyle  --max-line-length=120 --ignore=E305,E226 ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    side_errors = int(c.out)
                    side_errors = min(side_errors, 14)
                    side_errors *= -1

                    # sheets API to make edit to file for number of errors
                    value = str(side_errors)
                    # Edit Google sheet for PEP8 errors (B9)
                    range_name = 'Rubric' + '!B9'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
                    
                    # Check for function birthday_song
                    cmd = 'grep "def birthday_song(" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    birthday_song = int(c.out)
                    if birthday_song == 0:
                        value = '-4'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F4'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # Check that function is called once
                    passme = False
                    with open(filename, 'r',  encoding='utf8') as infile:
                        for line in infile.readlines():
                            found = re.match("(?<!def\s)birthday_song" , line,  re.X | re.M | re.S)
                            if found:
                                passme = True
                    infile.close()
                    if passme == True:
                        value = '0'
                    else:
                        value = '-4'
                    range_name = 'Rubric' + '!F5'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # extract functions and create python test file
                    extract_functions(filename)
                    functions_filename = filename.replace('.py', '.functions.py')
                    cmd = ' cat ' + functions_filename + \
                        ' /Users/teacher/PycharmProjects/untitled/3.020/3.020.test.py > /tmp/3.020.test.py'
                    c = delegator.run(cmd)

                    # test to see happy birthday output spits out 'birthday'
                    cmd = 'python3 /tmp/3.020.test.py testAutograde.test_happy_birthday 2>&1 |grep -i fail |wc -l'
                    c = delegator.run(cmd)
                    failures = int(c.out)
                    if failures > 0:
                        value = '-4'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F6'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # test to see happy birthday output spits out argument
                    cmd = 'python3 /tmp/3.020.test.py testAutograde.test_happy_birthday_output 2>&1 |grep -i fail |wc -l'
                    c = delegator.run(cmd)
                    failures = int(c.out)
                    if failures > 0:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F7'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # Check for function pick_card
                    cmd = 'grep "def pick_card(" ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    pick_card = int(c.out)
                    if pick_card == 0:
                        value = '-4'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F9'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # test for 4+ items list named cards
                    with open(filename, 'r',  encoding='utf8') as myfile:
                        filename_data = myfile.read()
                    search_object = re.search(r"\s* cards \s* = \s* \[ .* , .* , .* \]", filename_data, re.X | re.M | re.S)
                    if not search_object:
                        value = '-2'
                    else:
                        value ='0'
                    range_name = 'Rubric' + '!F10'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
 
                    # test for 4+ items list named suits
                    search_object = re.search(r"\s* suits \s* = .* \[ .* , .* , .* , .* \]", filename_data, re.X | re.M | re.S)
                    if not search_object:
                        value = '-2'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F11'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # test to see pick_card output spits out 1 'of'
                    cmd = 'python3 /tmp/3.020.test.py testAutograde.test_pick_card_output 2>&1 |grep -i fail |wc -l'
                    c = delegator.run(cmd)
                    failures = int(c.out)
                    if failures > 0:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F12'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # Check that pick_card function is called once
                    passme = False
                    with open(filename, 'r', encoding='utf8') as infile:
                        for line in infile.readlines():
                            found = re.match("(?<!def\s)pick_card" , line,  re.X | re.M | re.S)
                            if found:
                                passme = True
                    infile.close()
                    if passme:
                        value = '0'
                    else:
                        value = '-4'
                    range_name = 'Rubric' + '!F13'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # test 2 funs and verify they are different
                    filename_output1 = filename + '.out1'
                    filename_output2 = filename + '.out2'

                    cmd = 'python3 ' + filename + ' < /Users/teacher/PycharmProjects/untitled/3.020/3.020.in > ' \
                        + filename_output1
                    c = delegator.run(cmd)
                    cmd = 'python3 ' + filename + ' < /Users/teacher/PycharmProjects/untitled/3.020/3.020.in > ' \
                        + filename_output2
                    c = delegator.run(cmd)
                    cmd = 'diff ' + filename_output1 + ' ' + filename_output2 + ' | wc -l'
                    c = delegator.run(cmd)
                    different_lines = int(c.out)
                    if different_lines == 0:
                        value = '-4'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F14'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # check that pick_card prints out 10 cards (looks for 'of' 10x)
                    num_ofs = 0
                    with open(filename_output2, 'r', encoding='utf8') as infile:
                        for line in infile.readlines():
                            found = re.search(r"of", line,  re.X | re.M | re.S)
                            if found:
                                num_ofs += 1
                    infile.close()
                    if num_ofs <= 9:
                        value = '-4'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F15'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    




                    body = {'valueInputOption': 'USER_ENTERED',
                            'data':datapoints}
                    result = service_sheets.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                                body=body).execute()
