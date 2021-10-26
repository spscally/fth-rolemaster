import json
import emails
import reports

from calc import RolemasterCalculator


# Get the raw contents of the report files
role_report = reports.getMostRecentReportContents()
table_topics = reports.getTableTopics()

# Create the calculator object, parse the files, and calculate progress and leaders
rolemaster_calculator = RolemasterCalculator(role_report, table_topics)
rolemaster_calculator.parse()
progress = rolemaster_calculator.calculate()
(leaders, leaders_role_count) = rolemaster_calculator.leaders()

# Generate the subject line and the email
subject = reports.getReportSubjectLine()
content = emails.generateEmail(subject, leaders, leaders_role_count, progress)

# Send it
success = emails.sendEmail(subject, content)
if success:
    print("Success!")
else:
    print("Something went wrong :(")
