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
import glob
import sys

sys.path.insert(0,'/Users/teacher/PycharmProjects/untitled/4.021')

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
def extract_functions(orig_file):
    import re
    outfile_name = orig_file.replace('.py', '.functions.py')
    outfile = open(outfile_name, 'w', encoding='utf8')
    with open(orig_file, 'r', encoding='utf8') as infile:
        line = True
        while line:
            line = infile.readline()
            start_def = re.search("^(def|class) \s+ .+ " , line,  re.X | re.M | re.S)
            if start_def:
                outfile.write(line)
                in_function = True
                while in_function:
                    line = infile.readline()
                    end_of_function = re.search("^[a-zA-Z]", line, re.X | re.M | re.S)
                    new_function = re.search("^(def|class) \s+ .+ " , line,  re.X | re.M | re.S)
                    if end_of_function and not new_function:
                        in_function = False
                        start_def = False
                    elif end_of_function and new_function:
                        in_function = True
                        start_def = True
                        outfile.write(line)
                    else:
                        outfile.write(line)

def extract_single_function(orig_file, function):
    import re
    function_file = orig_file.replace('.py', '.functions.py')
    extracted_function = ''
    with open(function_file, 'r', encoding='utf8') as infile:
        line = True
        while line:
            print("looking for this function : " + function)
            line = infile.readline()
            start_def = re.search("^(def|class) \s+ " + function , line,  re.X | re.M | re.S)
            if start_def:
                print("entering function!")
                print('writing this' + str(line))
                extracted_function += line
                print("reading this" + str(line))
                inside_function = True
                while inside_function:
                    print('reading this ' + str(line))
                    line = infile.readline()
                    inside_function = re.search("^(\s+ | \# ) .+ " , line,  re.X | re.M | re.S)
                    if inside_function:
                        print("writing this inside function " + str(line))
                        extracted_function += line
                extracted_function += line
    return extracted_function


# Clear out old files
for file in glob.glob('*functions*'):
    #print(file)
    os.remove(file)

for filename in os.listdir('.'):
    #print(filename)
    do_this_file = False
    if len(sys.argv) > 1:
        if filename in sys.argv:
            do_this_file = True
    else:
        if filename.endswith('.py'):
            do_this_file = True
    if do_this_file:
        for key in name_dictionary.name_dict:
            print(key)
            match = re.match('.+' + key + '.+', filename)
            match2 = re.match('function', filename)
            if match and not match2:
                # construct query here
                print('matches a file in dictionary ' + filename)
                rubric_file = name_dictionary.name_dict[key] + ' - Python 7.031_7.034_Flaherty_and_Pirates - Rubric'
#                rubric_file = name_dictionary.name_dict[key] + ' - Python 4.025_Serena_Williams_simulator - Rubric'
#                rubric_file = name_dictionary.name_dict[key] + ' - Python 4.021/4.022 - The Rock Says Bad Lossy Compression - Rubric'
            #    print(rubric_file)
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
                        value = '-2.5'
                    # Edit Google sheet for helps
                    range_name = 'Rubric' + '!B4'    
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # Find number of PEP8 errors
                    cmd = 'pycodestyle  --max-line-length=120 --ignore=E305,E226,E241,W504,W293,E126 ' + filename + ' | wc -l  '
                    c = delegator.run(cmd)
                    side_errors = int(c.out)
                    side_errors = min(side_errors, 14)
                    side_errors *= -1

                    # sheets API to make edit to file for number of errors
                    value = str(side_errors)
                    # Edit Google sheet for PEP8 errors (B9)
                    range_name = 'Rubric' + '!B10'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    with open(filename, 'r', encoding='utf8') as myfile:
                        filename_data = myfile.read()

                    # Search for a blank dictionary
                    search_object = re.search(r"{ \s* }", filename_data, re.X | re.M | re.S)
                    if not search_object:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F4'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # Check for function add with 2 inputs
                    search_object = re.search(r"^def \s add\(.+ , .+ \)", filename_data, re.X| re.M | re.S)
                    if not search_object:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F5'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)
 
                    # extract functions and create python test file
                    extract_functions(filename)
                    functions_filename = filename.replace('.py', '.functions.py')
                    cmd = ' cat ' + functions_filename + \
                        ' ./7.031.test.py > /tmp/7.031.test.py'
                    c = delegator.run(cmd)

                    
                    # test1 for flaherty
                    cmd = 'python3 /tmp/7.031.test.py testAutograde.test_flaherty_1 2>&1 |grep -i fail |wc -l'
                    c = delegator.run(cmd)
                    failures = int(c.out)                    
                    if failures > 0:
                        value = '-5'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F4'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # test2 for flaherty
                    cmd = 'python3 /tmp/7.031.test.py testAutograde.test_flaherty_2 2>&1 |grep -i fail |wc -l'
                    c = delegator.run(cmd)
                    failures = int(c.out)
                    if failures > 0:
                        value = '-10'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F5'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)

                    # test3 for flaherty
                    cmd = 'python3 /tmp/7.031.test.py testAutograde.test_flaherty_3 2>&1 |grep -i fail |wc -l'
                    c = delegator.run(cmd)
                    failures = int(c.out)
                    if failures > 0:
                        value = '-10'
                    else:
                        value = '0'
                    range_name = 'Rubric' + '!F6'
                    datapoint = { 'range': range_name,
                                  'values': [[value]]
                                  }
                    datapoints.append(datapoint)


                    body = {'valueInputOption': 'USER_ENTERED',
                            'data':datapoints}
                    print(body)
                    result = service_sheets.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                                body=body).execute()
