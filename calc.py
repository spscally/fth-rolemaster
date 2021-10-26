import config
import reports

from scrapy.http import HtmlResponse


class RolemasterCalculator:
    """
    Object to perform Rolemaster calculation and to store any needed metadata.
    """

    # Raw contents of the Member Role Report HTML file
    role_report = ''

    # Raw contents of the Table Topics file
    table_topics = ''

    # Stores every role taken for each meeting for each member
    memberRoles = {}

    # Stores one of the optimal collection of roles for each member
    progress = {}

    # Current leader(s)
    leaders = []

    # The number of roles that the leader(s) have taken
    leaders_role_count = 0

    def __init__(self, role_report, table_topics):
        self.role_report = role_report
        self.table_topics = table_topics

    def parse(self):
        """
        Tells the RolemasterCalculator object to parse the reports.
        """

        # Parse the raw HTML file
        self.__parseMemberRoleReport()

        # Parse the Table Topics file
        self.__parseTableTopicsFile()

    def calculate(self):
        """
        Tells the RolemasterCalculator object to calculate members' progress based on the
        computed memberRoles object from the parse method.
        """

        # Calculate rolemaster progress for each member
        for member in self.memberRoles:
            self.__calculateRolemasterForMember(
                member, self.memberRoles[member], {})

        # Add missing role TODO's to the progress object
        self.__addMissingRoles()

        # Return the progress object, so it can be emailed
        return self.progress

    def leaders(self):
        """
        Calculates the current leader(s) and how many roles they have taken. Will also store
        the computed values for future lookup.
        """

        # If the leaders list is not empty and the role count is greater than zero, we have
        # already calculated the leaders, so just return what we have
        if self.leaders != [] and self.leaders_role_count > 0:
            return (self.leaders, self.leaders_role_count)

        # Otherwise, we need to calculate

        # Track current leaders and how many roles they have taken
        leaders = []
        max = -1

        # Loop over all members in the progress object
        for member in self.progress:

            # Count up their roles
            count = 0
            for role in self.progress[member]:

                # Ignore the TODO's
                if self.progress[member][role] != "TODO":
                    count += 1

            # If we have a new max, create a new leaders list with just this member
            if count > max:
                max = count
                leaders = [member]

            # If we match the previous max, add this member to the existing leaders list
            elif count == max:
                leaders.append(member)

        # Store the computer leaders and role count
        self.leaders = leaders
        self.leaders_role_count = max
        return (self.leaders, self.leaders_role_count)

    def __parseMemberRoleReport(self):
        """
        Parses the Member Role HTML file and creates the memberRoles object.
        """

        # Use a CSS selector to get all of the rows in the HTML file
        content = HtmlResponse(url='', body=self.role_report, encoding='utf8')
        rows = content.css('tbody tr')

        # Since the HTML doesn't indicate when we switch people, we have to keep track of that
        # with a bool
        newPerson = False
        name = ''

        # Loop through the rows
        for r in rows:

            # The <hr> tag would indicate the end of this member's role list
            if len(r.css('hr')) > 0:
                newPerson = True
                continue

            # Get the all of the text in this row
            data = r.css('td::text').getall()

            date = None
            role = None

            # Row format differs whether or not this is the first row for a member
            if newPerson:

                # First row for member:
                # data[0] = member name
                # data[1] = meeting date
                # data[2] = meeting role
                name = data[0]

                # Chop off any Toastmaster accolades (i.e. ", DTM"). Makes for easier Table Topics tracking,
                # since you don't have to put the accolade in the tt.txt file
                if name.find(',') != -1:
                    name = name[:name.find(',')]

                # Since this is a newly-encountered member, initialize their dictionary
                self.memberRoles[name] = {}
                newPerson = False
                date = data[1]
                role = data[2]
            else:

                # Other rows for member:
                # data[0] = meeting date
                # data[1] = meeting role
                date = data[0]
                role = data[1]

            # Strip off trailing whitespace
            role = role.strip()

            # Convert "Speaker #1", "Speaker #2", etc. to just "Speaker"
            if role.find("Speaker") != -1:
                role = "Speaker"

            # Do the same with Evaluators
            elif role.find("Evaluator #") != -1:
                role = "Evaluator"

            # Change "Table Topics" to "Table Topics Master" to not confuse with Table Topics participant
            elif role == "Table Topics":
                role = "Table Topics Master"

            # Do not track Presiding Officer
            elif role == "Presiding Officer":
                continue

            # Initialize the role list for this meeting date for this member, if it does not exist
            if self.memberRoles[name].get(date) is None:
                self.memberRoles[name][date] = []

            # Add the role to the member's list of roles for this meeting
            self.memberRoles[name][date].append(role)

        # Remove tracking for "Guest".
        if self.memberRoles.get('Guest'):
            self.memberRoles.pop('Guest')

    def __parseTableTopicsFile(self):
        """
        Adds Table Topics from the tt/tt.txt file to the memberRoles object.
        """

        # Get all of the Table Topics lines and loop through them
        tts = reports.getTableTopics()
        for tt in tts:

            # Trim off trailing newline character
            tt = tt.replace('\n', '')

            # Line is in the following format:
            # <date in YYYY-MM-DD> <member name>

            # Anything before the first space is the date
            date = tt[:tt.find(' ')]

            # Anything after the first space is the member's name
            name = tt[tt.find(' ')+1:]

            # Initialize the member's role dictionary.
            if self.memberRoles.get(name) is None:
                self.memberRoles[name] = {}

            # Initialize the role list for this member for this meeting
            if self.memberRoles[name].get(date) is None:
                self.memberRoles[name][date] = []

            # Add Table Topics to the role list.
            self.memberRoles[name][date].append("Table Topics")

    def __addMissingRoles(self):
        """
        Adds TODO's for each role that each member is missing.
        """

        # Loop over each possible role for each member
        for member in self.memberRoles:
            for role in config.ROLES:

                # If that role is not present for the member already, add "TODO"
                if self.progress[member].get(role) is None:
                    self.progress[member][role] = "TODO"

    def __calculateRolemasterForMember(self, member, remaining, used):
        """
        Recursively calculates valid collections of roles for this member. Members can only
        count one role per meeting towards their progress.

        Parameters:
        - member : member's name
        - remaining : remaining roles to recurse over
        - used : roles counted so far in this branch of the recursion tree
        """

        # Remaining list is empty, so check to see if this is a new best collection
        if len(remaining) == 0:

            # No collection tracked yet, so initialize their progress dictionary
            if self.progress.get(member) is None:
                self.progress[member] = {}

            # Check to see if the length of used is longer than the stored best collection
            if len(used) > len(self.progress[member]):
                self.progress[member] = used

            # Return out to prevent further recursion
            return

        # Get the next meeting date to check
        date = list(remaining.keys())[0]

        # Loop through all roles the member took in that meeting
        for role in remaining[date]:

            # Copy the parameter dictionaries
            newUsed = used.copy()
            newRemaining = remaining.copy()

            # Remove this meeting from the copy of the remaining dictionary
            newRemaining.pop(date)

            # Add role to copy of used dictionary, only if the member has not already filled it
            if used.get(role) is None:
                newUsed[role] = date

            # Recurse
            self.__calculateRolemasterForMember(member, newRemaining, newUsed)
