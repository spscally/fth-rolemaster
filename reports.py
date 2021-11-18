import os

from datetime import date

import config


def getMostRecentReportFileName():
    """
    Gets most recent Member Role Report HTML file from reports directory.
    Assumes YYYY-MM-DD.htm file name.
    """
    reports = os.listdir(config.REPORTS_DIR)
    reports.sort()
    return reports[-1]


def getMostRecentReportContents():
    """
    Gets the contents of the most recent Member Role Report HTML file.
    """
    file = getMostRecentReportFileName()
    contents = ''
    with open(f'{config.REPORTS_DIR}/{file}') as f:
        contents = f.read()
    return contents


def getReportSubjectLine():
    """
    Generates the report subject line in the following format:
    Rolemaster Report - MM/DD/YYYY
    """
    today = date.today()
    return f'Rolemaster Report - {today.month}/{today.day}/{today.year}'


def getTableTopics():
    """
    Get the contents of the tt/tt.txt file, which contains historical TT data.
    """
    with open(f'{config.TT_DIR}/tt.txt') as f:
        lines = f.readlines()
        return lines
