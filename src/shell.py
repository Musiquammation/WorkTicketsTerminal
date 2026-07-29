import shlex
from typing import List

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion

from COMMAND_REGISTRY import COMMAND_REGISTRY
from Database import Database
from shellTypes import Command
import COLORS

# --- Error Handling System ---

class ShellError(Exception):
	"""Base class for all shell-related errors."""
	pass

class ShellSyntaxError(ShellError):
	"""Raised when the command line syntax is invalid (e.g., unclosed quotes)."""
	pass

class CommandNotFoundError(ShellError):
	"""Raised when no matching command is found in the registry."""
	pass

class CommandArgumentError(ShellError):
	"""Raised when there is an issue with command arguments or flags."""
	def __init__(self, message: str, command: Command):
		super().__init__(message)
		self.command = command


# --- Completer ---

class RegistryCompleter(Completer):
	def __init__(self, registry: List[Command], db: Database):
		self.registry = registry
		self.db = db

	def get_completions(self, document, complete_event):
		text = document.text_before_cursor

		words = text.split()
		if not text or text[-1].isspace():
			words.append("")

		current_word = words[-1]
		previous_words = words[:-1]

		possible_next_words = set()
		matched_command = None

		# Find the matching command
		for cmd in self.registry:
			path = cmd.path

			if len(previous_words) < len(path):
				match = True
				for i, word in enumerate(previous_words):
					if path[i] != word:
						match = False
						break

				if match:
					possible_next_words.add(path[len(previous_words)])

			elif len(previous_words) >= len(path):
				if previous_words[:len(path)] == path:
					matched_command = cmd
					break

		if not matched_command:
			# Complete the command path
			for word in possible_next_words:
				if word.startswith(current_word):
					yield Completion(word, start_position=-len(current_word))

			if len(previous_words) == 0 and "exit".startswith(current_word):
				yield Completion("exit", start_position=-len(current_word))

		else:
			# Analyze what has already been typed
			typed_tokens = previous_words[len(matched_command.path):]

			positional_index = 0
			i = 0
			expected_tag = None

			while i < len(typed_tokens):
				token = typed_tokens[i]

				tag = next((t for t in matched_command.tags if t.name == token), None)
				flag = next((f for f in matched_command.flags if f.name == token), None)

				if tag:
					expected_tag = tag
					i += 1

					# Consume the tag value if present
					if i < len(typed_tokens):
						expected_tag = None
						i += 1

				elif flag:
					i += 1

				elif token in ("-help", "--help"):
					i += 1

				else:
					positional_index += 1
					i += 1

			completions = []

			# Complete the value of a tag
			if expected_tag:
				completions = expected_tag.get_completions(self.db)

			else:
				# Complete flags/tags
				if current_word.startswith("-"):
					completions = (
						[flag.name for flag in matched_command.flags]
						+ [tag.name for tag in matched_command.tags]
						+ ["-help"]
					)

				# Complete positional argument values
				else:
					if positional_index < len(matched_command.arguments):
						argument = matched_command.arguments[positional_index]
						completions = argument.get_completions(self.db)

			for completion in completions:
				if completion.startswith(current_word):
					yield Completion(
						completion,
						start_position=-len(current_word),
					)


# --- Execution Engine ---

def execute_command(db: Database, line: str, registry: List[Command]):
	try:
		tokens = shlex.split(line)
	except ValueError as e:
		raise ShellSyntaxError(f"Syntax error: {e}")

	if not tokens:
		return

	for cmd in registry:
		path_length = len(cmd.path)

		if len(tokens) >= path_length and tokens[:path_length] == cmd.path:
			command_tokens = tokens[path_length:]

			if "-help" in command_tokens or "--help" in command_tokens:
				cmd.print_help()
				return

			# Initialize default values
			parsed_arguments = {}
			parsed_flags = {
				flag.name.lstrip("-"): False
				for flag in cmd.flags
			}
			parsed_tags = {
				tag.name.lstrip("-"): None
				for tag in cmd.tags
			}

			positional_tokens = []

			# Parse command line
			i = 0
			while i < len(command_tokens):
				token = command_tokens[i]

				flag = next((f for f in cmd.flags if f.name == token), None)
				if flag:
					parsed_flags[flag.name.lstrip("-")] = True
					i += 1
					continue

				tag = next((t for t in cmd.tags if t.name == token), None)
				if tag:
					if i + 1 >= len(command_tokens):
						raise CommandArgumentError(
							f"Tag '{tag.name}' expects a value "
							f"(type: {tag.type_cast.__name__}).",
							command=cmd
						)

					value = command_tokens[i + 1]

					try:
						parsed_tags[tag.name.lstrip("-")] = tag.type_cast(value)
					except ValueError:
						raise CommandArgumentError(
							f"'{value}' is not a valid value for "
							f"'{tag.name}' (expected type: "
							f"{tag.type_cast.__name__}).",
							command=cmd
						)

					i += 2
					continue

				if token.startswith("-"):
					raise CommandArgumentError(
						f"Unknown option '{token}'.",
						command=cmd
					)

				positional_tokens.append(token)
				i += 1

			# Map positional arguments
			for index, argument in enumerate(cmd.arguments):
				if index < len(positional_tokens):
					parsed_arguments[argument.name] = positional_tokens[index]
				else:
					if argument.required:
						raise CommandArgumentError(
							f"Missing required positional argument "
							f"'{argument.name}'.",
							command=cmd
						)
					parsed_arguments[argument.name] = argument.default

			if len(positional_tokens) > len(cmd.arguments):
				raise CommandArgumentError(
					"Too many positional arguments.",
					command=cmd
				)

			kwargs = {
				**parsed_arguments,
				**parsed_flags,
				**parsed_tags,
			}

			cmd.callback(db, kwargs)
			return

	raise CommandNotFoundError("Unknown command. Type 'help' to list commands or 'exit' to quit.")


# --- Main Shell Loop ---

def shell(db: Database):
	session = PromptSession(
		completer=RegistryCompleter(COMMAND_REGISTRY, db)
	)

	print("CLI started. Type 'help' to list commands or 'exit' to quit.")

	while True:

		try:
			line = session.prompt("> ").strip()

			if not line:
				continue

			if line == "exit":
				break

			execute_command(db, line, COMMAND_REGISTRY)

		# Handle known shell parsing and validation errors
		except CommandArgumentError as e:
			print(f"\n{COLORS.RED}[!] Error: {e}{COLORS.RESET}")
			if e.command:
				print()
				e.command.print_help()
				
		except ShellError as e:
			print(f"{COLORS.RED}[!] Error: {e}{COLORS.RESET}")

		# Catch unexpected runtime errors inside the command callback
	
		except KeyboardInterrupt:
			# Handle Ctrl+C gracefully
			continue
		
		except EOFError:
			# Handle Ctrl+D gracefully
			break
		
		except Exception as e:
			print(f"{COLORS.RED}[!] Unexpected error during command execution: {e}{COLORS.RESET}")

