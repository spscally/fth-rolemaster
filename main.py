import json
import os
import subprocess

from email.message import EmailMessage

from scrapy.http import HtmlResponse

REPORTS_DIR = "reports"
TT_DIR = "./tt"

ROLES = [
    "Toastmaster",
    "Humorist",
    "Grammarian",
    "Ah Counter",
    "Timer",
    "Speaker",
    "Table Topics Master",
    "General Evaluator",
    "Evaluator",
    "Table Topics"
]


def getMostRecentReportFileName():
    reports = os.listdir(REPORTS_DIR)
    reports.sort()
    return reports[-1]


# HTML report from FTH
def getMostRecentReport():
    file = getMostRecentReportFileName()
    contents = ''
    with open(f'{REPORTS_DIR}/{file}') as f:
        contents = f.read()
    return contents


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
            if name.find(',') != -1:
                name = name[:name.find(',')]
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
        elif role.find("Evaluator #") != -1:
            role = "Evaluator"
        elif role == "Table Topics":
            role = "Table Topics Master"
        elif role == "Presiding Officer":
            continue

        if memberRoles[name].get(date) is None:
            memberRoles[name][date] = []
        memberRoles[name][date].append(role)

    return memberRoles


longest = {}


# manually-created txt file
# format per line: YYYY-MM-DD FirstName LastName
def addTableTopics(memberRoles):
    with open(f'{TT_DIR}/tt.txt') as f:
        lines = f.readlines()
        for line in lines:
            line = line.replace('\n', '')
            date = line[:line.find(' ')]
            name = line[line.find(' ')+1:]
            if memberRoles.get(name) is None:
                memberRoles[name] = {}
            if memberRoles[name].get(date) is None:
                memberRoles[name][date] = []
            memberRoles[name][date].append("Table Topics")
    return memberRoles


def calculateRolemaster(name, remaining, used):

    if len(remaining) == 0:
        if longest.get(name) is None:
            longest[name] = {}
        if len(used) > len(longest[name]):
            longest[name] = used
        return used

    date = list(remaining.keys())[0]
    for role in remaining[date]:

        newUsed = used.copy()
        newRemaining = remaining.copy()
        newRemaining.pop(date)

        if used.get(role) is None:
            newUsed[role] = date

        calculateRolemaster(name, newRemaining, newUsed)


def addMissing(progress):
    for member in progress:
        for role in ROLES:
            if progress[member].get(role) is None:
                progress[member][role] = "TODO"
    return progress


def printCurrentLeader(progress):
    names = []
    max = -1
    for member in progress:
        count = 0
        for role in progress[member]:
            if progress[member][role] != "TODO":
                count += 1
        if count > max:
            max = count
            names = [member]
        elif count == max:
            names.append(member)

    print("LEADERS:")
    for name in names:
        print(f' - {name}: {max}')


def printRolesByDone(progress):
    roleCounts = {}
    for role in ROLES:
        roleCounts[role] = 0
    for member in progress:
        for role in progress[member]:
            if progress[member][role] != "TODO":
                roleCounts[role] += 1

    print("ROLE COUNTS:")
    for role in roleCounts:
        print(f' - {role}: {roleCounts[role]}')


report = getMostRecentReport()
memberRoles = getMemberRoles(report)
if memberRoles.get('Guest'):
    memberRoles.pop('Guest')
memberRoles = addTableTopics(memberRoles)

for member in memberRoles:
    calculateRolemaster(member, memberRoles[member], {})

progress = addMissing(longest)

print(json.dumps(longest, indent=2))
print("")
printCurrentLeader(longest)
print("")
printRolesByDone(longest)

# TODO: generate the HTML
# TODO: open the HTML in chrome

# subprocess.run(
# ["Start-Process", "chrome.exe", f'{REPORTS_DIR}/{getMostRecentReportFileName()}'])
