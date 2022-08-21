# Directory that the Member Role Reports are stored in
REPORTS_DIR = "./reports"

# Boolean indicating if Table Topics speakers are used for the award
TT_IS_USED = True

# Display name for the Table Topics speaker role
TT_DISPLAY_ROLE = "Table Topics Speaker"

# Directory that the tt.txt file is stored in
TT_DIR = "./tt"

# List of agenda roles to count for the award
ROLES = [
    "Toastmaster",
    "Humorist",
    "Grammarian",
    "Ah Counter",
    "Timer",
    "Speaker",
    "General Evaluator",
    "Evaluator",
    "Table Topics",
    "Guest Ambassador"
]

# If Table Topics speakers is enabled/required, adds it to the role list
if (TT_IS_USED):
    ROLES.append(TT_DISPLAY_ROLE)

# Padding of various HTML elements in the generated email
PADDING = '10px'
