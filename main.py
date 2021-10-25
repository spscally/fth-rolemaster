from scrapy.http import HtmlResponse

import config
import email
import reports


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
    lines = reports.getTableTopics()
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


role_report_contents = reports.getMostRecentReportContents()
table_topics = reports.getTableTopics()

memberRoles = getMemberRoles(report)
if memberRoles.get('Guest'):
    memberRoles.pop('Guest')
memberRoles = addTableTopics(memberRoles)

for member in memberRoles:
    calculateRolemaster(member, memberRoles[member], {})

progress = addMissing(longest)

title = reports.getReportTitle()
(leaders, leaders_role_count) = getCurrentLeaders(progress)

content = email.generateEmail(title, leaders, leaders_role_count, progress)
email.sendEmail(title, content)
