##imports
import json
import os
import sys
from flask import (Flask, render_template)
import re
import webbrowser


##CLASSES
class Finding:
    def __init__(self, rating, full_name, creation_time, last_write_time):
        self.rating = rating
        self.full_name = full_name
        self.creation_time = creation_time
        self.last_write_time = last_write_time

    def __str__(self) -> str:
        return self.fullPath


app = Flask(__name__)

### Globals
global filename
global findings


@app.route("/")
def index():
    return render_template("index.html", findings=findings)


def parseSnafflerJSON(inJsonFile):
    findings = []
    for jsonObject in inJsonFile['entries']:
        if jsonObject['level'] == "Warn":
            for eventProperty in jsonObject['eventProperties'].keys():
                for fileProperties in jsonObject['eventProperties'][eventProperty].keys():
                    for moreProperties in jsonObject['eventProperties'][eventProperty][fileProperties]:
                        if moreProperties == "MatchedRule":
                            rating = jsonObject['eventProperties'][eventProperty][fileProperties]['MatchedRule'][
                                'Triage']
                            creation_time = jsonObject['eventProperties'][eventProperty]['FileResult']['FileInfo'][
                                'CreationTime']
                            last_write_time = jsonObject['eventProperties'][eventProperty]['FileResult']['FileInfo'][
                                'LastWriteTime']
                            full_name = jsonObject['eventProperties'][eventProperty]['FileResult']['FileInfo'][
                                'FullName']
                            findings.append(Finding(rating, full_name, creation_time, last_write_time))
    return findings


def populateSharesfromJSON(inJSONFile):
    json_string = ""
    for line in open(inJSONFile, "r"):
        json_string += line
    jsonFileObject = json.loads(json_string)
    return parseSnafflerJSON(jsonFileObject)


def populateSharesfromTXT(inTxtFile):
    findings = []
    fileLineTest = re.compile(r"(\[File\])")
    for line in open(inTxtFile, "r", encoding='cp1252'):
        if fileLineTest.search(line):
            rating = re.search(r"(?<=\{)(.*?)(?=\})", line).group(1)
            full_name = re.search(r"(?<=>\()(.*?)(?=\))", line).group(1)
            creation_time = re.search(r"^.*\|(\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01]) .*?Z)", line).group(1)
            findings.append(Finding(rating, full_name, creation_time, None))
    return findings


def print_banner():
    print(".,:::::: .-:::::'.-:::::' :::      :::.    ::.    :::.  :::::::.. .::::::.:")
    print(";;;;'''' ;;;'''' ;;;''''  ;;;      ;;`;;   ;;;;,  `;;; ;;;;``;;;;;;;`    ``")
    print(" [[cccc  [[[,,== [[[,,==  [[[     ,[[ '[[,  [[[[[. '[[  [[[,/[[[''[==/[[[[,")
    print(" $$      `$$$'`` `$$$'``  $$'    c$$$cc$$$c $$$ 'Y$c$$   $$$$$$c   '''    $")
    print("888oo,__  888     888   o88oo,.__888   888,888    Y88  888b '88bo,88b    dP")
    print("M''''YUM   'MM,    'MM,  ''''YUMM YMM   ''` MMM     YMMMMMMM   'W'  'YMmMY'")


def main(render_html=True):
    print_banner()
    if len(sys.argv) > 1:
        global filename
        filename = sys.argv[1]
        currentPath = os.getcwd()

        global findings
        print("###############################################")
        if '.json' in filename:
            print("Great, looks like you specified a JSON file ...")
            print("Here we go!")
            findings = populateSharesfromJSON(filename)
        elif '.txt' in filename or '.log' in filename:
            print("Great, looks like you specified a standard output file ...")
            print("Here we go!")
            findings = populateSharesfromTXT(filename)
        else:
            print("Ok, so you didn't give me a file with an extension (or one I know about)")
            print("Lets try Snaffler JSON output first!")
            try:
                findings = populateSharesfromJSON(filename)
                print("Yay! That worked!")
            except:
                print("!!!!")
                print("Ok, so it wasn't Snaffler JSON output ...")
                print("Lets try standard Snaffler output!")
                try:
                    findings = populateSharesfromTXT(filename)
                    if not bool(findings):
                        raise Exception('...')
                    print("Yay! That worked!")
                except:
                    print("What kind of garbage input is this!!??")
                    print("Come back when you have Snaffler input to give me.")
                    sys.exit()

        print("###############################################")
        if render_html:
            webbrowser.open('http://127.0.0.1:5000', new=2)
            app.run()
    else:
        print("Please provide a .json or .txt file as a command line argument.")


if __name__ == '__main__':
    main()
