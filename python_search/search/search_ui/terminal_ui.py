import asyncio
import sys
from typing import Any, List

from getch import getch

from python_search.search.search_ui.bm25_search import Bm25Search
from python_search.search.search_ui.search_actions import Actions
from python_search.search.search_ui.semantic_search import SemanticSearch

from python_search.theme import get_current_theme
from python_search.core_entities.core_entities import Entry


class SearchTerminalUi:
    MAX_LINE_SIZE = 80
    MAX_KEY_SIZE = 45
    MAX_CONTENT_SIZE = 45
    NUMBER_ENTRIES_TO_RETURN = 15

    _documents_future = None
    commands = None
    documents = None
    ENABLE_SEMANTIC_SEARCH = True

    def __init__(self) -> None:
        self.theme = get_current_theme()
        self.cf = self.theme.get_colorful()
        self.cf.update_palette(
            {
                "green": "#97AE5E",
                "yellow": "#DB9D3E",
                "red": "#E56B55",
            }
        )
        self.actions = Actions()
        self.previous_query = ""
        self.tdw = None
        self.reloaded = False
        self.first_run = True

        self.setup_entries()

    def setup_entries(self):
        import subprocess, json

        output = subprocess.getoutput("pys _entries_loader load_entries_as_json ")
        self.commands = json.loads(output)

        self.search_bm25 = Bm25Search(
            self.commands, number_entries_to_return=self.NUMBER_ENTRIES_TO_RETURN
        )
        if self.ENABLE_SEMANTIC_SEARCH:
            self.search_semantic = SemanticSearch(
                self.commands, number_entries_to_return=self.NUMBER_ENTRIES_TO_RETURN
            )

    async def run(self):
        """
        Rrun the application main loop
        """

        self.query = ""
        self.selected_row = 0
        self.selected_query = -1
        # hide cursor
        self.print_first_line()
        self.hide_cursor()

        self.matches = self.search(query="")
        self.print_entries(self.matches)

        while True:
            self.print_first_line()

            if self.query != self.previous_query or self.reloaded:
                self.matches = self.search(query=self.query)
                self.reloaded = False
            self.previous_query = self.query
            self.previous_matches = self.matches
            self.print_entries(self.matches)

            # kept here just to warmup chroma
            if self.ENABLE_SEMANTIC_SEARCH:
                self.search_semantic.search(self.query)
            c = self.get_caracter()
            self.process_chars(self.query, c)

    def search(self, query) -> List[str]:
        """gets 1 from each type of search at a time and merge them to remove duplicates"""

        bm25_results = self.search_bm25.search(query)

        semantic_results = []
        if self.ENABLE_SEMANTIC_SEARCH and not self.first_run:
            semantic_results = self.search_semantic.search(query)

        final_results = []
        for i in range(self.NUMBER_ENTRIES_TO_RETURN):
            if (
                bm25_results[i] not in final_results
                and bm25_results[i] in self.commands
            ):
                final_results.append(bm25_results[i])

            if semantic_results and (
                semantic_results[i] not in final_results
                and semantic_results[i] in self.commands
            ):
                final_results.append(semantic_results[i])

            if len(final_results) >= self.NUMBER_ENTRIES_TO_RETURN:
                break

        self.first_run = False

        return final_results

    def hide_cursor(self):
        print("\033[?25l", end="")

    def get_caracter(self) -> str:
        try:
            return getch()
        except Exception as e:
            return " "

    def print_first_line(self):
        print(
            "\x1b[2J\x1b[H"
            + self.cf.cursor(f"({len(self.commands)})> ")
            + f"{self.cf.bold(self.cf.query(self.query))}"
        )

    def print_entries(self, matches: List[str]):
        # print the matches
        for i, key in enumerate(matches):
            try:
                entry = Entry(key, self.commands[key])
            except Exception as e:
                continue

            if i == self.selected_row:
                self.print_highlighted(key, entry)
            else:
                self.print_normal_row(key, entry)

    def process_chars(self, query: str, c: str):
        ord_c = ord(c)
        # test if the character is a delete (backspace)
        if ord_c == 127:
            # backspace
            self.query = query[:-1]
        elif ord_c == 10:
            # enter
            self.actions.run_key(self.matches[self.selected_row])
            if self.query:
                self._get_data_warehouse().write_event(
                    "python_search_typed_query", {"query": query}
                )
        elif ord_c == 9:
            # tab
            self.actions.edit_key(self.matches[self.selected_row])
        elif c == "'":
            # tab
            self.actions.copy_entry_value_to_clipboard(self.matches[self.selected_row])
        elif ord_c == 47:
            # ?
            self.actions.search_in_google(self.query)
        # handle arrows
        elif ord_c == 66:
            if self.selected_row < len(self.matches) - 1:
                self.selected_row = self.selected_row + 1
        elif ord_c == 65:
            if self.selected_row > 0:
                self.selected_row = self.selected_row - 1
        elif c == ".":
            self.selected_query += 1
            self.query = self.get_query(self.selected_query)
        elif c == ",":
            if self.selected_query >= 0:
                self.selected_query -= 1
            self.query = self.get_query(self.selected_query)
        elif c == "+":
            sys.exit(0)
        elif ord_c == 68 or c == ";":
            # clean query shortcuts
            self.query = ""
        elif ord_c == 67:
            sys.exit(0)
        elif ord_c == 92:
            print("Reloading data...")
            self.setup_entries()
            self.query = ""
            self.reloaded = True
            self.selected_row = 0
        elif c == "-":
            # go up and clear
            self.selected_row = 0
            # remove the last word
            self.query = " ".join(
                list(filter(lambda x: x, self.query.split(" ")))[0:-1]
            )
            self.query += " "
        elif c.isalnum() or c == " ":
            self.query += c
            self.selected_row = 0

    def get_query(self, position):
        # len
        df = self._get_data_warehouse().event("python_search_typed_query")
        if position >= len(df):
            return ""

        return df.sort_values(by="tdw_timestamp", ascending=False).iloc[position][
            "query"
        ]

    def _get_data_warehouse(self):
        if not self.tdw:
            from tiny_data_warehouse import DataWarehouse

            self.tdw = DataWarehouse()

        return self.tdw

    def print_highlighted(self, key: str, entry: Any) -> None:
        key_part = self.cf.bold(
            self.cf.selected(f" {self.control_size(key, self.MAX_KEY_SIZE)}")
        )
        body_part = f" {self.cf.bold(self.color_based_on_type(self.control_size(self.sanitize_content(entry.get_content_str(strip_new_lines=True)), self.MAX_CONTENT_SIZE), entry))} "
        print(key_part + body_part)

    def print_normal_row(self, key, entry):
        key_input = self.control_size(key, self.MAX_KEY_SIZE)
        body_part = self.color_based_on_type(
            self.control_size(
                self.sanitize_content(entry.get_content_str(strip_new_lines=True)),
                self.MAX_CONTENT_SIZE,
            ),
            entry,
        )
        print(f" {key_input} {body_part} ")

    def color_based_on_type(self, content, entry):
        type = entry.get_type_str()
        if type == "snippet":
            return self.cf.yellow(content)
        elif type == "cli_cmd" or type == "cmd":
            return self.cf.red(content)
        elif type == "url":
            return self.cf.green(content)
        elif type == "file":
            return self.cf.green(content)

        return content

    def sanitize_content(self, line) -> str:
        """
        Transform content into suitable to display in terminal row
        """
        line = line.strip()
        line = line.replace("\n", "")
        return line

    def control_size(self, a_string, num_chars):
        """
        Cuts when there is too long string and ads spaces when htere are too few.
        """
        if len(a_string) > num_chars:
            return a_string[0 : num_chars - 3] + "..."
        else:
            return a_string + " " * (num_chars - len(a_string))


async def main_async():
    await SearchTerminalUi().run()


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
