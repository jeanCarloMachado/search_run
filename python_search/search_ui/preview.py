import json
import logging
from datetime import datetime

from colorama import Fore, Style

from python_search.config import ConfigurationLoader


class Preview:
    """
    Preview the entry in the search ui
    """

    def __init__(self):
        self.configuration = ConfigurationLoader()
        self.logger = logging.getLogger("preview_entry")
        # do not send the errors to stderr, in the future we should send to kibana or a file
        self.logger.disabled = True

    def display(self, entry_text: str):
        """
        Prints the entry in the preview window

        """

        data = self._build_values_to_print(entry_text)
        self._print_values(data)

    def _print_values(self, data):
        print("")
        print(self._color_str(data['value'], self._get_color_for_type(data['type'])))
        print("")
        print(f"Key: {self._color_str(data['key'], Fore.YELLOW)}")
        if 'position' in data:
            print("Position: " + data['position'])

        if 'created_at' in data:
            print("Created at: " + data['created_at'])
            print("Entry Age: " + data['entry_age'])

        if 'tags' in data:
            print("Tags: " + data['tags'])

    def _get_color_for_type(self, type):
        if type == 'cmd':
            return Fore.RED

        if type in ['url', 'file']:
            return Fore.GREEN

        return Fore.BLUE


    def _color_str(self, a_string, a_color) -> str:
        return f"{a_color}{a_string}{Fore.RESET}"

    def _build_values_to_print(self, entry_text):
        print_values = entry_text.split(":")
        key = print_values[0]
        # the entry content is after the key + a ":" character
        serialized_content = entry_text[len(key) + 1:]

        print_values = {}
        print_values['type'] = "Unknown"
        print_values['key'] = key
        entry_data = self._load_key_data(key)
        if "url" in entry_data:
            print_values['value'] = entry_data.get("url")
            print_values['type'] = 'Url'

        if "file" in entry_data:
            print_values['value'] = entry_data.get("file")
            print_values['type'] = 'File'

        if "snippet" in entry_data:
            print_values['value'] = entry_data.get("snippet")
            print_values['type'] = 'Snippet'

        if "cli_cmd" in entry_data or "cmd" in entry_data:
            print_values['value'] = entry_data.get("cli_cmd", entry_data.get("cmd"))
            print_values['type'] = "Cmd"

        if "callable" in entry_data:
            value = entry_data.get("callable")
            import dill
            print_values['value'] = dill.source.getsource(value)

        if "created_at" in entry_data:
            from dateutil import parser
            creation_date = parser.parse(entry_data["created_at"])
            today = datetime.now()
            print_values['created_at'] = str(creation_date)
            print_values["entry_age"] = str(today - creation_date)

        if 'tags' in entry_data:
            print_values['tags'] = " ".join(entry_data['tags'])

        decoded_content = self._decode_serialized_data(serialized_content)
        if 'position' in decoded_content:
            print_values['position'] = str(decoded_content['position'])

        return print_values

    def _decode_serialized_data(self, serialized_content):
        try:
            return json.loads(serialized_content)
        except Exception as e:
            self.logger.error(str(e))
            return []

    def _load_key_data(self, key):
        entries = self.configuration.load_entries()
        if not key in entries:
            print()
            print((f'Key "{self._color_str(key, Fore.RED)}" not found in python search data'))
            import sys
            sys.exit(0)

        return entries[key]