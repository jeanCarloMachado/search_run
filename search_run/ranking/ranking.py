from grimoire.decorators import notify_execution
from grimoire.file import write_file
from grimoire.search_run.search_run_config import Configuration
import pandas as pd
import json

from search_run.logger import configure_logger
from search_run.ranking.ciclical import CiclicalPlacement


class Ranking:
    """
    Write to the file all the commands and generates shortcuts
    """

    def __init__(self):
        self.configuration = Configuration
        self.cached_file = Configuration.cached_filename

    @notify_execution()
    def recompute_rank(self):
        """
        Recomputes the rank and saves the results on the file to be read
        """

        entries: dict = self.load_entries()
        commands_performed = self.load_commands_performed_df()

        ml_enabled = False

        if ml_enabled:
            result = self.compute_ml(entries, commands_performed)
        else:
            result = CiclicalPlacement().cyclical_placment(entries, commands_performed)

        return self._export_to_file(result)

    def compute_ml(self, entries, commands_performed):
        pass

    def load_commands_performed_df(self):
        with open("/data/grimoire/message_topics/run_key_command_performed") as f:
            data = []
            for line in f.readlines():
                try:
                    data.append(json.loads(line))
                except Exception as e:
                    print(f"Line broken: {line}")
        df = pd.DataFrame(data)

        # revert the list (latest on top)
        df = df.iloc[::-1]

        return df

    def _export_to_file(self, data):
        fzf_lines = ""
        for name, content in data:
            fzf_lines += f"{name.lower()}: {content}\n"

        write_file(self.configuration.cached_filename, fzf_lines)

    def load_entries(self):
        return self.configuration().commands
