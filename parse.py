import os
import csv
import re
import textract
import tqdm
import sys

files = next(os.walk('docs'))[2]

with open('output.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['TOWN', 'RANG', 'DIR', 'SECT', 'COUN_UC', 'EMS', 'SERVICE', 'LEVEL', 'REGION', 'filename'], extrasaction='ignore', restval=None)
    writer.writeheader()

    for file in tqdm.tqdm(files):
        if (file[-4:] != '.doc'):
            print(file + " is not a .doc file. Skipping!")
            continue

        text = textract.process("docs\\" + file)

        text = text.decode('utf8')

        lines = text.splitlines(True)           

        parsingError = False

        data = {}
        numberpresent = False

        data['filename'] = file

        inThrough = False

        for line in lines:
            twp_search = re.search('^\s*T([0-9]+)[A-Z]\s*R([0-9]+)([A-Z])\s*[-–—]?\s*(?:sec)?\s*(.*)\s*$', line, flags=re.IGNORECASE)
            county_search = re.search('^\s*In\s+([A-Z\.\-]+(\s+[A-Z\.\-]+)*)\s*Co(\.|(unty))?\s*[:;]?\s*$', line, flags=re.IGNORECASE)

            if twp_search:
                data['TOWN'] = twp_search.group(1)
                data['RANG'] = twp_search.group(2)
                data['DIR'] = twp_search.group(3)

                if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION', 'COUN_UC']):
                    print("Parsing Error in " + file + ": Township entry found without all prerequisite data: " + line)
                    parsingError = True


                rest = twp_search.group(4)
                numberpresent = False
                if len(rest) > 0:
                    if any (word in rest for word in ['except', 'excluding', 'but', 'not', 'all']):
                        print("Parsing Error in " + file + ": special case, not parseable: " + line)
                        parsingError = True
                    else:
                        parts = [x for x in re.split('\s+|,', rest)]
                        for part in parts:
                            if part.isdigit():
                                numberpresent = True
                                if inThrough:
                                    for i in range(data['SECT'] + 1, int(part) + 1):
                                        data['SECT'] = i
                                        writer.writerow(data)
                                    
                                    inThrough = False
                                else:
                                    data['SECT'] = int(part)
                                    writer.writerow(data)
                            elif (part.lower() == 'through' or part.lower() == '-') and numberpresent:
                                inThrough = True
                            elif '-' in part and all(c=='-' or c.isdigit() for c in part):
                                start,end = part.split('-', maxsplit=1)
                                if not start.isdigit() or not end.isdigit() or int(start)>36 or int(end)>36:
                                    continue
                                for i in range(int(start), int(end) + 1):
                                    data['SECT'] = i
                                    writer.writerow(data)
                                    
                else:
                    for i in range(1, 37):
                        data['SECT'] = i
                        writer.writerow(data)
            
            elif county_search:
                data['COUN_UC'] = county_search.group(1).upper()
                if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION']):
                    print("Parsing Error in " + file + ": County entry found without all prerequisite data: " + line)
                    parsingError = True
                
            elif line[0:17].upper() == "AMBULANCE SERVICE" and ":" in line:
                if 'SERVICE' in data:
                    print("Parsing Error in " + file + ": duplicate ambulance service entries: " + line)
                    parsingError = True

                service = line.split(':', 1)[1]
                service = service.strip()
                data['SERVICE'] = service
            
            elif line[0:4].upper() == "EMS#" and ":" in line:
                if 'EMS' in data:
                    print("Parsing Error in " + file + ": duplicate ems# entries: " + line)
                    parsingError = True

                ems = line.split(':', 1)[1]
                ems = ems.strip()
                data['EMS'] = ems
            
            elif line[0:6].upper() == "REGION" and ":" in line:
                if 'REGION' in data:
                    print("Parsing Error in " + file + ": duplicate region entries: " + line)
                    parsingError = True

                region = line.split(':', 1)[1]
                region = region.strip()
                data['REGION'] = region
            
            elif line[0:13].upper() == "SERVICE LEVEL" and ":" in line:
                if 'LEVEL' in data:
                    print("Parsing Error in " + file + ": duplicate service level entries: " + line)
                    parsingError = True

                service_level = line.split(':', 1)[1]
                service_level = service_level.strip()
                data['LEVEL'] = service_level

            elif 'The primary service area is the legal primary service area'.lower() in line.lower():
                break

            elif not any (char in line for char in ':;/#\\') and any (str(num) in line for num in range(10)):
                if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION', 'COUN_UC', 'TOWN', 'RANG', 'DIR']):
                    print("Parsing Error in " + file + ": Possible data loss, sections with no prerequisite data: " + line)
                    parsingError = True

                if any (word in line for word in ['except', 'excluding', 'but', 'not', 'all']):
                    print("Parsing Error in " + file + ": possible special case, not parseable: " + line)
                    parsingError = True
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
                        elif (part.lower() == 'through' or part.lower() == '-') and numberpresent:
                            inThrough = True
                        elif '-' in part and all(c=='-' or c.isdigit() for c in part):
                            start,end = part.split('-', maxsplit=1)
                            if not start.isdigit() or not end.isdigit() or int(start)>36 or int(end)>36:
                                continue
                            for i in range(int(start), int(end) + 1):
                                data['SECT'] = i
                                writer.writerow(data)

        if parsingError:
            sys.stdout.flush()
            if not os.path.isdir('txts'):
                os.mkdir('txts')
            with open('txts\\' + file[0:-4] + '.txt', 'w', newline='') as txt:
                txt.writelines(lines)
