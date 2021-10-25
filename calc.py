import config


# Object to perform the Rolemaster calculation and to store any needed metadata.
class RolemasterCalculator:

    # Will store the raw contents of the Member Role Report HTML file
    role_report = ''

    # Will store the raw contents of the Table Topics file
    table_topics = ''

    # Will store an optimal selection of roles for each member
    longest = {}

    # Will store, for each member, every role they have taken and on which date(s)
    progress = {}

    # Initialize the object
    def __init__(self, role_report, table_topics):
        self.role_report = role_report
        self.table_topics = table_topics

        # Parse the raw HTML file
        self.parseMemberRoleReport()

        # Parse the Table Topics file
        self.parseTableTopicsFile()

        # Add missing role TODO's to the progress object
        self.addMissingRoles()

    def __addMissingRoles__(self):
        """
        Adds TODO's for each role that each member is missing.
        """
        for member in self.progress:
            for role in config.ROLES:
                if self.progress[member].get(role) is None:
                    self.progress[member][role] = "TODO"
        return self.progress
