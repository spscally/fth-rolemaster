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
        if newPerson:
            name = data[0]
            memberRoles[name] = [
                {data[1]: data[2].strip()}
            ]
            newPerson = False
        else:
            memberRoles[name].append({
                data[0]: data[1].strip()
            })

    print(memberRoles)


# TODO: figure out the algorithm and data structure needed for calcing rolemaster
report = getMostRecentReport()
getMemberRoles(report)
