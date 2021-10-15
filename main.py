import json
import os

from scrapy.http import HtmlResponse
from scrapy.selector import Selector

REPORTS_DIR = "./reports"


def getMostRecentReport():
    reports = os.listdir(REPORTS_DIR)
    reports.sort()
    file = ''
    with open(f'{REPORTS_DIR}/{reports[-1]}') as f:
        file = f.read()
    return file


def getMemberRoles(html):
    response = HtmlResponse(url='', body=html, encoding='utf8')
    rows = response.css('tbody tr')
    memberRoles = {}
    newPerson = False
    name = ''
    for r in rows:
        if len(r.css('hr')) > 0:
            newPerson = True
            continue

        data = r.css('td::text').getall()

        date = None
        role = None

        if newPerson:
            name = data[0]
            memberRoles[name] = []
            newPerson = False
            date = data[1]
            role = data[2]
        else:
            date = data[0]
            role = data[1]

        role = role.strip()
        if role.find("Speaker") != -1:
            role = "Speaker"
        elif role.find("Evaluator") != -1:
            role = "Evaluator"
        elif role == "Presiding Officer":
            continue

        memberRoles[name].append({date: role})

    return memberRoles


report = getMostRecentReport()
memberRoles = getMemberRoles(report)
print(json.dumps(memberRoles, indent=2))
# for m in memberRoles:
# TODO: implement
# construct member's graph
# list all paths from START to END
# get longest path
