import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config
import secrets


def generateEmail(title, leaders, leaders_role_count, progress):
    """
    Generates the HTML for the email given the title, list of leaders, leaders'
    role count (i.e. how many of the roles they have done) and the progress
    object.

    Uses in-line style attrs since many email clients block script tags.
    """

    # Create string to store HTML
    html = ''

    # Add title
    html += f'<h1>{title}</h1>\n'
    html += '<p>Beep boop boop bop. This email was generated by a robot!</p>\n'

    # Add list of leaders
    html += f'<h2>Current Leader(s)</h2>\n'
    html += '\t<ul>\n'
    for leader in leaders:
        html += f'\t\t<li>{leader} ({leaders_role_count} / {len(config.ROLES)})</li>\n'
    html += '\t</ul>\n'

    # Create progress table + header row
    html += '<h2>Progress</h2>\n'
    html += f'<p>Sign up for your next role <a href="{secrets.AGENDA_LINK}">here</a>!</p>'
    html += '<table style="border: 1px solid black; text-align: center" rules="all">\n'
    html += '\t<tr>\n'
    html += f'\t\t<th style="padding: {config.PADDING}">Name</th>\n'
    html += f'\t\t<th style="padding: {config.PADDING}">Role Count</th>\n'

    # Add all roles to the header role
    for role in config.ROLES:
        html += f'\t\t<th style="padding: {config.PADDING}">{role}</th>\n'
    html += '\t<tr>\n'

    # Add each member's progress to the table
    is_even = True
    for member in progress:

        # Alternate white and gainsboro background color per row for visibility
        if is_even:
            html += '\t<tr style="background-color: gainsboro">\n'
        else:
            html += '\t<tr>\n'

        # Add member's name
        html += f'\t\t<td style="padding: {config.PADDING}">{member}</td>\n'

        # Count up member's role count for the Role Count column
        count = 0
        for date in progress[member]:
            if progress[member][date] != 'TODO':
                count += 1
        html += f'\t\t<td style="padding: {config.PADDING}">{count} / {len(config.ROLES)}</td>\n'

        # Add progress for each member-role cell
        for role in config.ROLES:
            cell = '\t\t<td style="'

            # Not completed --> fill w/ red "TODO"
            if progress[member][role] == 'TODO':
                cell += 'color: crimson; '

            # Completed --> fill w/ green date of completion
            else:
                cell += 'color: mediumseagreen; '

            # Add styling used for both complete and incomplete cells
            cell += f'padding: {config.PADDING}'
            cell += f'"><strong>{progress[member][role]}</strong></td>\n'
            html += cell

        # End member row and switch next row's color
        html += '\t</tr>\n'
        is_even = not is_even

    # End table
    html += '</table>\n'
    html += '<br>\n'

    # Add help message
    html += f'<p>For any questions/comments/concerns/suggestions, please reach out to <a href="mailto:{secrets.SUPPORT_EMAIL}">{secrets.SUPPORT_EMAIL}</a>.</p>\n'
    return html


def sendEmail(subject_line, content, test_run):
    """
    Sends the rolemaster report with the given subject line and HTML content.

    Sends the report to the support email if this is a test_run.
    """

    # Tells email clients to render the content not as plain text but as HTML
    msg = MIMEMultipart('alternative')
    part = MIMEText(content, 'html')
    msg.attach(part)

    # Set subject line, from email, and to email
    msg['Subject'] = subject_line
    msg['From'] = secrets.FROM_EMAIL

    if test_run == True:
        msg['To'] = secrets.SUPPORT_EMAIL
    else:
        msg['To'] = secrets.TO_EMAIL

    # Open connection to Gmail and login
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(secrets.FROM_EMAIL, secrets.PASSWORD)

    # Send the email and close the connection
    smtp.send_message(msg)
    smtp.quit()

    # Indicate success
    return True
