import csv
import json

# root folder //  корневая папка 
root_folder = '/HERE GOES THE PATH TO THE PROJECT MAIN FOLDER'
source_folder = root_folder + '/data/'
target_folder = root_folder + '/data/'

tagset = {}

line_count = 0

try:
    with open(source_folder + 'tagset.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            fulltag = row[0]
            description = row[1]
            base_element = fulltag.split('_')
            if fulltag not in tagset.keys():
                tagset[fulltag] = [base_element[0], fulltag, description]
            line_count += 1
except Exception as ex:
    print(ex)


try:
    with open(target_folder + 'tagset.json', 'w') as outfile:
        json.dump(tagset, outfile, indent=4)
    print(line_count, 'tags processed')
    print('File "tagset.json" successfully created at ', target_folder)
except Exception as ex:
    print(ex)