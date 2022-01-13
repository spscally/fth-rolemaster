# fth-rolemaster

## Overview

I originally wanted to write a fully automated solution for generating the rolemaster report, but FTH uses Captcha. Since no API is available, this solution is quasi-automated. As described below, you must manually pull the Member Role Report from the site and you must also manually track Table Topics (since that is not tracked on the agenda). You must also manually trigger the report to be sent out.

## Dependencies

- Python 3
- Powershell (currently only Windows is supported)
- Make

## Calculation

In order to achieve the rolemaster award in a year, a member must sign up for each of the following roles:
- Toastmaster
- Humorist
- Grammarian
- Ah Counter
- Timer
- Speaker
- Table Topics Master
- General Evaluator
- Evaluator
- Table Topics (speaker)

Only one role is counted towards the rolemaster award per meeting.

This program uses a brute-force approach to find, for each member, a grouping of roles and meeting dates that gives them the most progress towards the award. Since there may be multiple groupings that achieve the same sum of roles, it is possible that a member who is manually tracking their progress will see something slightly different in the report than what they were expecting.

For example, a member has attended two meetings and taken the following roles:
- Meeting #1: Speaker and Table Topics
- Meeting #2: Humorist and Table Topics

The max progress towards the award is 2/10 roles, but there are multiple "paths" of getting there:
- Speaker (Meeting #1) and Humorist (Meeting #2)
- Speaker (Meeting #1) and Table Topics (Meeting #2)
- Table Topics (Meeting #1) and Humorist (Meeting #2)

Note that while the member has taken three different roles across these two meetings, only one role is counted per meeting and thus their max progress is 2.

The generated report might show the first option, while a member might have tracked themselves with one of the other ones, potentially causing a bit of confusion.

## Setup

There are a few things that need to be set up if you are interested in running the report:
- an email address from which you will send the report to your club
- account- and club-specific configuration
- input data

## Program Arguments

- `--test`: generates the report and sends the email to the `SUPPORT_EMAIL` (described below), rather than to the club

### Email Account Setup

I recommend creating a dedicated Google account for the purpose of sending out this report, as you will have to store your password in the secrets.py configuration file.

You will also need to add this account to your club website, so that it is able to send out an email to any of the club email addresses. Make sure to opt-in after adding the rolemaster account to the club site.

The account will need to have "Less Secure App Access" enabled. This can be done from the Google Account settings under the Security section.

### Configuration

- in secrets.py, replace:
  - `FROM_EMAIL` with the email of the account from which you will send the report
    - I recommend an account dedicated for this purpose
    - this also currently only supports Google/Gmail accounts
  - `PASSWORD` with the password of the Google account defined above
    - having to put the password in this file is why I recommend an account only for this purpose
  - `TO_EMAIL` with the email list of your club (i.e. members-#######@toastmastersclubs.org)
  - `SUPPORT_EMAIL` with the email of the member who is managing the report, so other members can reach out with any questions/comments/etc
  - `AGENDA_LINK` with the link to the FTH agenda page (i.e. https://yourClubNameHere.toastmastersclubs.org/agenda.html)

In addition to the configuration above, you can add or remove any custom roles in the config.py `ROLES` list. For example, my club also has a "Guest Ambassador" role for being in charge of welcoming guests to the meeting. Any additional custom roles that are added must also be added to the agendas, so that they are present in the downloaded Member Role Report.

### Input Data

#### Member Role Report

- save the member role report, not as a PDF, but as a Webpage
    - in Chrome, select the "Webpage, HTML Only" option
    - create a directory called "reports" and put the file in there

#### Table Topics Data

- since FTH does not save this data on the agendas, create a directory called "tt"
- in it, put a file called "tt.txt" and list all of the table topics in the following format:
    - `<date in YYYY-MM-DD format> <Member Name>`
  - this file should be updated this manually after each meeting
- for example, a `tt.txt` file might look like:

```
2021-10-01 John Doe
2021-10-01 Jane Doe
2021-10-15 John Doe
```