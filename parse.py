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

        inThrough = False

        with open('txts/' + file[0:-4] + '.txt') as txt:
            lines = txt.readlines()

            for line in lines:
                if twp_search := re.search('^\s*T([0-9]+)[A-Z]R([0-9]+)([A-Z])\s*[-–—]?\s*sections?\s*(.*)\s*$', line, flags=re.IGNORECASE):
                    data['TOWN'] = twp_search.group(1)
                    data['RANG'] = twp_search.group(2)
                    data['DIR'] = twp_search.group(3)

                    if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION', 'COUN_UC']):
                        print("Parsing Error in " + file + ": Township entry found without all prerequisite data: " + line)

                    if len(rest := twp_search.group(4)) > 0:
                        if any (word in rest for word in ['except', 'excluding', 'but', 'not', 'all', '-']):
                            print("Parsing Error in " + file + ": special case, not parseable: " + line)
                        else:
                            parts = [x for x in re.split('\s+|,', rest)]
                            for part in parts:
                                if part.isdigit():
                                    if inThrough:
                                        for i in range(data['SECT'] + 1, int(part) + 1):
                                            data['SECT'] = i
                                            writer.writerow(data)
                                        
                                        inThrough = False
                                    else:
                                        data['SECT'] = int(part)
                                        writer.writerow(data)
                                elif part.lower() == 'through':
                                    inThrough = True
                    else:
                        for i in range(1, 37):
                            data['SECT'] = i
                            writer.writerow(data)
                
                elif county_search := re.search('^\s*In\s*([A-Z]+(\s*[A-Z]+)*)\s*Co(\.|(unty))?\s*[:;]?\s*$', line, flags=re.IGNORECASE):
                    data['COUN_UC'] = county_search.group(1).upper()
                    if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION']):
                        print("Parsing Error in " + file + ": County entry found without all prerequisite data: " + line)
                    
                elif line[0:17].upper() == "AMBULANCE SERVICE":
                    if 'SERVICE' in data:
                        print("Parsing Error in " + file + ": duplicate ambulance service entries: " + line)

                    service = line.split(':', 1)[1]
                    service = service.strip()
                    data['SERVICE'] = service
                
                elif line[0:4].upper() == "EMS#":
                    if 'EMS' in data:
                        print("Parsing Error in " + file + ": duplicate ems# entries: " + line)

                    ems = line.split(':', 1)[1]
                    ems = ems.strip()
                    data['EMS'] = ems
                
                elif line[0:6].upper() == "REGION":
                    if 'REGION' in data:
                        print("Parsing Error in " + file + ": duplicate region entries: " + line)

                    region = line.split(':', 1)[1]
                    region = region.strip()
                    data['REGION'] = region
                
                elif line[0:13].upper() == "SERVICE LEVEL":
                    if 'LEVEL' in data:
                        print("Parsing Error in " + file + ": duplicate service level entries: " + line)

                    service_level = line.split(':', 1)[1]
                    service_level = service_level.strip()
                    data['LEVEL'] = service_level

                elif not any (char in line for char in ':;/#\\') and any (str(num) in line for num in range(10)):
                    if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION', 'COUN_UC', 'TOWN', 'RANG', 'DIR']):
                        print("Parsing Error in " + file + ": Possible data loss, sections with no prerequisite data: " + line)

                    if any (word in rest for word in ['except', 'excluding', 'but', 'not', 'all', '-']):
                        print("Parsing Error in " + file + ": possible special case, not parseable: " + line)
                    else:
                        parts = [x for x in re.split('\s+|,', line)]
                        for part in parts:
                            if part.isdigit():
                                if inThrough:
                                    for i in range(data['SECT'] + 1, int(part) + 1):
                                        data['SECT'] = i
                                        writer.writerow(data)
                                    
                                    inThrough = False
                                else:
                                    data['SECT'] = int(part)
                                    writer.writerow(data)
                            elif part.lower() == 'through':
                                inThrough = True