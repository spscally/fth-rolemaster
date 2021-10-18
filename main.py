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


def calculateRolemaster(remaining, used):

    # TODO: test that this is correct
    # TODO: check for role already being used
    if len(remaining) == 0:
        print(used)
        return used

    thisMeeting = []

    # TODO: revamp data structure so I don't have to use this atrocity
    date = list(remaining[0].keys())[0]
    while True:
        thisMeeting.append(remaining[0])
        remaining = remaining[1:]
        if len(remaining) == 0 or list(remaining[0].keys())[0] != date:
            break

    for m in thisMeeting:
        newUsed = used
        newUsed.append(m)
        return calculateRolemaster(remaining, newUsed)


report = getMostRecentReport()
memberRoles = getMemberRoles(report)

for member in memberRoles:
    calculateRolemaster(memberRoles[member], [])
