import os
import textract

files = next(os.walk('docs'))[2]

IMPORTANT_TEXT = "This primary service area is the legal primary service area"

for file in files:
    if (file[-4:] != '.doc'):
        print(file + " is not a .doc file. Skipping!")
        continue

    text = textract.process("docs\\" + file)

    text = text.decode('utf8')

    if IMPORTANT_TEXT not in text:
        print("phrase not found in " + file)