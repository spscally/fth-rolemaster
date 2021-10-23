import json
import os
import smtplib

from datetime import date

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from scrapy.http import HtmlResponse

import config
import secrets


def getMostRecentReportFileName():
    reports = os.listdir(config.REPORTS_DIR)
    reports.sort()
    return reports[-1]


# HTML report from FTH
def getMostRecentReport():
    file = getMostRecentReportFileName()
    contents = ''
    with open(f'{config.REPORTS_DIR}/{file}') as f:
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
    with open(f'{config.TT_DIR}/tt.txt') as f:
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
        for role in config.ROLES:
            if progress[member].get(role) is None:
                progress[member][role] = "TODO"
    return progress


def getCurrentLeaders(progress):
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

    return (names, max)


def printRolesByDone(progress):
    roleCounts = {}
    for role in config.ROLES:
        roleCounts[role] = 0
    for member in progress:
        for role in progress[member]:
            if progress[member][role] != "TODO":
                roleCounts[role] += 1

    print("ROLE COUNTS:")
    for role in roleCounts:
        print(f' - {role}: {roleCounts[role]}')


def getReportTitle():
    today = date.today()
    return f'Rolemaster Report - {today.month}/{today.day}/{today.year}'


def generateEmail(progress):
    html = ''
    html += f'<h1>{getReportTitle()}</h1>\n'
    html += '<p>Beep boop boop bop. This email was generated by a robot!</p>\n'

    html += f'<h2>Current Leader(s)</h2>\n'
    (leaders, leader_count) = getCurrentLeaders(progress)
    html += '\t<ul>\n'
    for leader in leaders:
        html += f'\t\t<li>{leader} ({leader_count} / {len(config.ROLES)})</li>\n'
    html += '\t</ul>\n'

    html += '<h2>Progress</h2>\n'
    html += '<table style="border: 1px solid black; text-align: center" rules="all">\n'
    html += '\t<tr>\n'
    html += f'\t\t<th style="padding: {config.PADDING}">Name</th>\n'
    html += f'\t\t<th style="padding: {config.PADDING}">Role Count</th>\n'

    for role in config.ROLES:
        html += f'\t\t<th style="padding: {config.PADDING}">{role}</th>\n'
    html += '\t<tr>\n'

    is_even = True
    for member in progress:
        if is_even:
            html += '\t<tr style="background-color: gainsboro">\n'
        else:
            html += '\t<tr>\n'

        html += f'\t\t<td style="padding: {config.PADDING}">{member}</td>\n'

        count = 0
        for date in progress[member]:
            if progress[member][date] != 'TODO':
                count += 1
        html += f'\t\t<td style="padding: {config.PADDING}">{count} / {len(config.ROLES)}</td>\n'

        for role in config.ROLES:
            cell = '\t\t<td style="'

            if progress[member][role] == 'TODO':
                cell += 'color: crimson; '
            else:
                cell += 'color: mediumseagreen; '
            cell += f'padding: {config.PADDING}'

            cell += f'"><strong>{progress[member][role]}</strong></td>\n'
            html += cell
        html += '\t</tr>\n'
        is_even = not is_even
    html += '</table>\n'
    html += '<br>\n'
    return html


def sendEmail(content):
    msg = MIMEMultipart('alternative')
    part = MIMEText(content, 'html')
    msg.attach(part)

    msg['Subject'] = getReportTitle()
    msg['From'] = secrets.FROM_EMAIL
    msg['To'] = secrets.TO_EMAIL

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(secrets.FROM_EMAIL, secrets.PASSWORD)
    smtp.send_message(msg)
    smtp.quit()


report = getMostRecentReport()
memberRoles = getMemberRoles(report)
if memberRoles.get('Guest'):
    memberRoles.pop('Guest')
memberRoles = addTableTopics(memberRoles)

for member in memberRoles:
    calculateRolemaster(member, memberRoles[member], {})

progress = addMissing(longest)

content = generateEmail(progress)
sendEmail(content)

# TODO: add support message (to contact me)
# TODO: add info about how this was calculated
