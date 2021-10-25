import os

from datetime import date

import config


# Gets most recent Member Role Report HTML file from reports directory.
# Assumes YYYY-MM-DD.html file name.
def getMostRecentReportFileName():
    reports = os.listdir(config.REPORTS_DIR)
    reports.sort()
    return reports[-1]


# Gets the contents of the most recent Member Role Report HTML file.
def getMostRecentReportContents():
    file = getMostRecentReportFileName()
    contents = ''
    with open(f'{config.REPORTS_DIR}/{file}') as f:
        contents = f.read()
    return contents


# Generates the report title in the following format:
# Rolemaster Report - MM/DD/YYYY
def getReportTitle():
    today = date.today()
    return f'Rolemaster Report - {today.month}/{today.day}/{today.year}'


# Get the contents of the tt/tt.txt file, which contains historical TT data.
def getTableTopics():
    with open(f'{config.TT_DIR}/tt.txt') as f:
        lines = f.readlines()
        return lines
