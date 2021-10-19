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
            memberRoles[name] = {}
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

        if memberRoles[name].get(date) is None:
            memberRoles[name][date] = []
        memberRoles[name][date].append(role)

    return memberRoles


def calculateRolemaster(name, remaining, used):

    if len(remaining) == 0:
        print(f'{name} : {used}')
        return used

    date = list(remaining.keys())[0]
    for role in remaining[date]:

        newUsed = used.copy()
        newRemaining = remaining.copy()
        newRemaining.pop(date)

        if used.get(role) is None:
            newUsed[role] = date

        calculateRolemaster(name, newRemaining, newUsed)


report = getMostRecentReport()
memberRoles = getMemberRoles(report)

# TODO: figure out how to get the longest list of roles
for member in memberRoles:
    calculateRolemaster(member, memberRoles[member], {})
