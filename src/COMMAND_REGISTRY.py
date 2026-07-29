from shellTypes import Command, CommandArgument, CommandFlag, CommandTag
from commands import *

def handle_help(db, kwargs):
	print("\nAvailable commands:")
	for cmd in COMMAND_REGISTRY:
		print(f"  - {cmd.name}")
	print("\nTip: You can append '-help' to any command for more details.\n")


COMMAND_REGISTRY = [
	Command(
		path=["help"],
		callback=handle_help,
		description="Print all commands"
	),


	# ---------------------------------------------------------
	# WORKFLOW COMMANDS
	# ---------------------------------------------------------
	Command(
		path=["workflow", "add"],
		callback=cb_workflow_add,
		arguments=[
			CommandArgument("name", "Name of the status", required=True)
		],
		flags=[
			CommandFlag("-start", "Set as a start status"),
			CommandFlag("-final", "Set as a final status"),
			CommandFlag("-bold", "Print status in bold")
		],
		tags=[
			CommandTag("-desc", str, "Description of the status"),
			CommandTag("-color", str, "Color of the status", choices_func=get_color_choices)
		],
		description="Add a status to the workflow. Raises an error if it already exists."
	),
	Command(
		path=["workflow", "remove"],
		callback=cb_workflow_remove,
		arguments=[
			CommandArgument("name", "Name of the status", required=True, choices_func=get_status_choices)
		],
		flags=[
			CommandFlag("-force", "Force deletion even if events are associated (deletes associated events)")
		],
		description="Remove a status and its transitions. Fails if used by events unless -force is active."
	),
	Command(
		path=["workflow", "style"],
		callback=cb_workflow_style,
		arguments=[
			CommandArgument("name", "Name of the status", required=True, choices_func=get_status_choices)
		],
		tags=[
			CommandTag("-color", str, "Change the color of the status", choices_func=get_color_choices),
			CommandTag("-bold", bool, "Change the bold attribute of the status (true/false)")
		],
		description="Modify the color and/or bold attribute of an existing status."
	),
	Command(
		path=["workflow", "link"],
		callback=cb_workflow_link,
		arguments=[
			CommandArgument("origin", "Origin status", required=True, choices_func=get_status_choices),
			CommandArgument("target", "Target status", required=True, choices_func=get_status_choices)
		],
		flags=[
			CommandFlag("-delete", "Delete the transition if no events use it"),
			CommandFlag("-force", "Delete the transition and all associated events")
		],
		tags=[
			CommandTag("-label", str, "Label of the transition")
		],
		description="Create, rename, or delete a transition between two statuses."
	),
	Command(
		path=["workflow", "show"],
		callback=cb_workflow_show,
		arguments=[
			CommandArgument("status", "Specific status to inspect", required=False, choices_func=get_status_choices)
		],
		description="Show details for a specific status, or list all statuses with their possible targets."
	),

	# ---------------------------------------------------------
	# PROJECT COMMANDS
	# ---------------------------------------------------------
	Command(
		path=["project", "add"],
		callback=cb_project_add,
		arguments=[
			CommandArgument("name", "Name of the new project", required=True)
		],
		description="Create a new project."
	),
	Command(
		path=["project", "remove"],
		callback=cb_project_remove,
		arguments=[
			CommandArgument("name", "Name of the project to remove", required=True, choices_func=get_project_choices)
		],
		flags=[
			CommandFlag("-confirm", "Mandatory confirmation flag to remove a project")
		],
		description="Remove an existing project. Requires -confirm flag."
	),
	Command(
		path=["project", "list"],
		callback=cb_project_list,
		description="list all available projects."
	),
	Command(
		path=["project", "update"],
		callback=cb_project_update,
		flags=[
			CommandFlag("-cleanStart", "Set the defaultStartStatus to null")
		],
		tags=[
			CommandTag("-start", str, "Set the default start status", choices_func=get_status_choices)
		],
		description="Update project settings and print the updated project info."
	),
	Command(
		path=["project", "login"],
		callback=cb_project_login,
		arguments=[
			CommandArgument("projectName", "Name of the project to log into", required=False, choices_func=get_project_choices)
		],
		description="Set the active project context, or display the current one if no name is provided."
	),

	# ---------------------------------------------------------
	# TICKET COMMANDS
	# ---------------------------------------------------------
	Command(
		path=["ticket", "list"],
		callback=cb_ticket_list,
		flags=[
			CommandFlag("-newest", "Filter or sort by newest"),
			CommandFlag("-oldest", "Filter or sort by oldest"),
			CommandFlag("-intersect", "Intersect color and status filters instead of union")
		],
		tags=[
			CommandTag("-project", str, "Override the currently logged-in project", choices_func=get_project_choices),
			CommandTag("-limit", int, "Maximum number of tickets to display"),
			CommandTag("-keep", str, "Comma-separated list of statuses to keep"),
			CommandTag("-color", str, "Comma-separated list of colors to filter by")
		],
		description="list tickets in a tree structure based on specific filters."
	),
	Command(
		path=["ticket", "add"],
		callback=cb_ticket_add,
		tags=[
			CommandTag("-title", str, "Title of the ticket"),
			CommandTag("-desc", str, "Description of the ticket"),
			CommandTag("-status", str, "Initial status of the ticket", choices_func=get_status_choices)
		],
		description="Add a new ticket. Opens vim if title and desc are not provided."
	),
	Command(
		path=["ticket", "delete"],
		callback=cb_ticket_delete,
		arguments=[
			CommandArgument("id", "Hex ID of the ticket to delete", required=True, choices_func=get_ticket_choices)
		],
		description="Delete a specific ticket by its ID."
	),
	Command(
		path=["ticket", "rename"],
		callback=cb_ticket_rename,
		arguments=[
			CommandArgument("id", "Hex ID of the ticket", required=True, choices_func=get_ticket_choices)
		],
		flags=[
			CommandFlag("-emptyVim", "Open an empty vim session instead of populating it with the previous title")
		],
		tags=[
			CommandTag("-title", str, "New title for the ticket")
		],
		description="Rename a ticket. Opens vim if -title is omitted."
	),
	Command(
		path=["ticket", "redesc"],
		callback=cb_ticket_redesc,
		arguments=[
			CommandArgument("id", "Hex ID of the ticket", required=True, choices_func=get_ticket_choices)
		],
		flags=[
			CommandFlag("-emptyVim", "Open an empty vim session instead of populating it with the previous description")
		],
		tags=[
			CommandTag("-desc", str, "New description for the ticket")
		],
		description="Change a ticket's description. Opens vim if -desc is omitted."
	),
	Command(
		path=["ticket", "move"],
		callback=cb_ticket_move,
		arguments=[
			CommandArgument("id", "Hex ID of the ticket", required=True, choices_func=get_ticket_choices),
			CommandArgument("status", "Target status", required=False, choices_func=get_status_choices)
		],
		description="Move a ticket to a new status, creating an Event. Shows available statuses if omitted."
	),
	Command(
		path=["ticket", "history"],
		callback=cb_ticket_history,
		arguments=[
			CommandArgument("id", "Hex ID of the ticket", required=False, choices_func=get_ticket_choices)
		],
		tags=[
			CommandTag("-limit", int, "Limit the number of events displayed")
		],
		description="Display the event history of a specific ticket, or the complete history if no ID is provided."
	)
]