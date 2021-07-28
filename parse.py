import os
import csv
import re

files = next(os.walk('pdfs'))[2]

if not os.path.isdir('txts'):
    os.mkdir('txts')

with open('output.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['TOWN', 'RANG', 'DIR', 'SECT', 'COUN_UC', 'EMS', 'SERVICE', 'LEVEL', 'REGION'], extrasaction='ignore', restval=None)
    writer.writeheader()

    for file in files:
        os.system('pdf2txt.py -o \"txts/' + file[0:-4] + '.txt\" \"pdfs/' + file + '\"')

        parsingError = False

        data = {}

        with open('txts/' + file[0:-4] + '.txt') as txt:
            lines = txt.readlines()

            for line in lines:
                if twp_search := re.search('^\s*T([0-9]+)[A-Z]R([0-9]+)([A-Z])\s*(.*)$', line, flags=re.IGNORECASE):
                    if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION', 'COUN_UC']):
                        parsingError = True

                    data['TOWN'] = twp_search.group(1)
                    data['RANG'] = twp_search.group(2)
                    data['DIR'] = twp_search.group(3)

                    if len(rest := twp_search.group(4)) > 0:
                        pass
                    else:
                        for i in range(1, 37):
                            data['SECT'] = i
                            writer.writerow(data)
                
                elif county_search := re.search('^\s*In\s*([A-Z]+(\s*[A-Z]+)*)\s*Co(\.|(unty))?\s*[:;]?\s*$', line, flags=re.IGNORECASE):
                    data['COUN_UC'] = county_search.group(1).upper()
                    if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION']):
                        parsingError = True
                    
                elif line[0:17].upper() == "AMBULANCE SERVICE":
                    if 'SERVICE' in data:
                        parsingError = True

                    service = line.split(':', 1)[1]
                    service = service.strip()
                    data['SERVICE'] = service
                
                elif line[0:4].upper() == "EMS#":
                    if 'EMS' in data:
                        parsingError = True

                    ems = line.split(':', 1)[1]
                    ems = ems.strip()
                    data['EMS'] = ems
                
                elif line[0:6].upper() == "REGION":
                    if 'REGION' in data:
                        parsingError = True

                    region = line.split(':', 1)[1]
                    region = region.strip()
                    data['REGION'] = region
                
                elif line[0:13].upper() == "SERVICE LEVEL":
                    if 'LEVEL' in data:
                        parsingError = True

                    service_level = line.split(':', 1)[1]
                    service_level = service_level.strip()
                    data['LEVEL'] = service_level
                

        writer.writerow(data)

        if parsingError:
            print("Parsing Error in " + file)