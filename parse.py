import os
import csv
import re

files = next(os.walk('pdfs'))[2]

os.mkdir('txts')

county_match = re.compile('^In\s([A-Z]+)\sCo[\.?,unty]\s?[:,;]?\s$', flags=re.IGNORECASE)
            

with open('output.csv') as f:
    writer = csv.DictWriter(f, fieldnames=['TOWN', 'RANG', 'DIR', 'SECT', 'COUN_UC', 'EMS', 'SERVICE', 'LEVEL', 'REGION'])
    writer.writeheader()

    for file in files:
        os.system('pdf2txt.py -o \"txts/' + file[0:-4] + '.txt\" \"pdfs/' + file + '\"')

        parsingError = False

        data = {}

        counties = []

        with open('\"txts/' + file[0:-4] + '.txt\"') as txt:
            lines = txt.readlines()

            for idx, line in enumerate(lines):
                if line[0:17].upper() == "AMBULANCE SERVICE":
                    if data['SERVICE'] is not None:
                        parsingError = True

                    service = line.split(':', 1)[1]
                    service = service.strip()
                    data['SERVICE'] = service
                elif line[0:4].upper() == "EMS#":
                    if data['EMS'] is not None:
                        parsingError = True

                    ems = line.split(':', 1)[1]
                    ems = service.strip()
                    data['EMS'] = ems
                elif line[0:6].upper() == "REGION":
                    if data['REGION'] is not None:
                        parsingError = True

                    region = line.split(':', 1)[1]
                    region = service.strip()
                    data['REGION'] = region
                elif line[0:13].upper() == "SERVICE LEVEL":
                    if data['LEVEL'] is not None:
                        parsingError = True

                    service_level = line.split(':', 1)[1]
                    service_level = service.strip()
                    data['LEVEL'] = service_level
                else:
                    county_search = re.search('^In\s([A-Z]+)\sCo[\.?,unty]\s?[:,;]?\s$', flags=re.IGNORECASE)

                    if county_search: 
                        county_name = county_search.group(1)
                        if not all (key in data for key in ['EMS', 'SERVICE', 'LEVEL', 'REGION']):
                            parsingError = True
                    
                        break

            idx += 1
            line = lines[idx]

            twp_data = []

            while not county_match.match(line):
                line_data = {}

                twp_search = re.search('^\sT([0-9]+)[A-Z]R([0-9]+)([A-Z])(.*)$', flags=re.IGNORECASE)

                if twp_search:
                    line_data['TOWN'] = twp_search.group(1)
                    line_data['RANG'] = twp_search.group(2)
                    line_data['DIR'] = twp_search.group(3)
                    line_data['COUN_UC'] = county_name.upper()

                    twp_data.append()

                

        writer.writerow(data)

        if parsingError:
            print("Parsing Error in " + file)