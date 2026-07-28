from typing import Callable, List, Optional, Any, Type

from Database import Database


class CommandArgument:
    """Positional argument (e.g. mainArg0)"""

    def __init__(
        self,
        name: str,
        description: str = "",
        required: bool = True,
        default: Any = None,
        choices_func: Optional[Callable[[Database], List[str]]] = None,
    ):
        self.name = name
        self.description = description
        self.required = required
        self.default = default
        self.choices_func = choices_func

    def get_completions(self, db: Database) -> List[str]:
        if self.choices_func:
            return self.choices_func(db)
        return []


class CommandFlag:
    """Boolean option without an argument (e.g. -bug, -idea)"""

    def __init__(self, name: str, description: str = ""):
        self.name = name  # Must include the dash, e.g. "-bug"
        self.description = description


class CommandTag:
    """Option with a typed value (e.g. -status ongoing)"""

    def __init__(
        self,
        name: str,
        type_cast: Type = str,
        description: str = "",
        choices_func: Optional[Callable[[Database], List[str]]] = None,
    ):
        self.name = name  # Must include the dash, e.g. "-status"
        self.type_cast = type_cast  # Automatically converts the value (int, float, str)
        self.description = description
        self.choices_func = choices_func

    def get_completions(self, db: Database) -> List[str]:
        if self.choices_func:
            return self.choices_func(db)
        return []


class Command:
    def __init__(
        self,
        path: List[str],
        callback: Callable[[Database,dict[str,Any]], None],
        arguments: Optional[List[CommandArgument]] = None,
        flags: Optional[List[CommandFlag]] = None,
        tags: Optional[List[CommandTag]] = None,
        description: str = "",
    ):
        self.path = path
        self.callback = callback
        self.arguments = arguments or []
        self.flags = flags or []
        self.tags = tags or []
        self.description = description

    @property
    def name(self) -> str:
        return " ".join(self.path)

    def print_help(self):
        args_str = " ".join(
            f"<{arg.name}>" if arg.required else f"[{arg.name}]"
            for arg in self.arguments
        )

        options_str = ""
        if self.flags or self.tags:
            options_str = " [OPTIONS]"

        print(f"\nUsage: {self.name} {args_str}{options_str} [-help]")

        if self.description:
            print(f"Description: {self.description}")

        if self.arguments:
            print("\nPositional arguments:")
            for arg in self.arguments:
                requirement = (
                    "Required"
                    if arg.required
                    else f"Optional (Default: {arg.default})"
                )
                print(f"  {arg.name}: {requirement}")
                if arg.description:
                    print(f"      └─ {arg.description}")

        if self.flags:
            print("\nFlags (optional):")
            for flag in self.flags:
                print(f"  {flag.name}")
                if flag.description:
                    print(f"      └─ {flag.description}")

        if self.tags:
            print("\nTags (optional with a value):")
            for tag in self.tags:
                type_name = tag.type_cast.__name__
                print(f"  {tag.name} <{type_name}>")
                if tag.description:
                    print(f"      └─ {tag.description}")

        print()