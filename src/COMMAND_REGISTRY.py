from shellTypes import Command, CommandArgument
from commands import *

def handle_help(kwargs):
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

    Command(
        path=["workflow", "status", "add"],
        callback=workflow_status_add,
        description="Add status in workflow",
        arguments=[
            CommandArgument(name="name")
        ]
    )
    
]