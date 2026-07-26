from shellTypes import Command


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
    )
    
]