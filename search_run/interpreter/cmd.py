import logging

from grimoire.notification import send_notification
from grimoire.shell import shell
from grimoire.string import remove_special_chars

from search_run.context import Context
from search_run.exceptions import CommandDoNotMatchException
from search_run.interpreter.base import BaseInterpreter
from search_run.terminal import Terminal

WRAP_IN_TERMINAL = "new-window-non-cli"

class CmdInterpreter(BaseInterpreter):
    def __init__(self, cmd, context: Context):
        self.context = context

        if type(cmd) == str:
            self.cmd = {WRAP_IN_TERMINAL: True, "cmd": cmd}
            return

        if WRAP_IN_TERMINAL in cmd and "cmd" in cmd:
            self.cmd = cmd
            return

        if "cli_cmd" in cmd:
            self.cmd = cmd
            self.cmd["cmd"] = cmd["cli_cmd"]
            self.cmd[WRAP_IN_TERMINAL] = True
            return

        if "cmd" in cmd:
            self.cmd = cmd
            return

        raise CommandDoNotMatchException.not_valid_command(self, cmd)

    def interpret_default(self):
        if self.try_to_focus():
            return

        cmd = self.apply_directory(self.cmd["cmd"])

        if "high_priority" in self.cmd:
            cmd = f"nice -19 {cmd}"

        if "directory" in self.cmd:
            cmd = f'cd {self.cmd["directory"]} && {cmd}'

        if "tmux" in self.cmd:
            cmd = f'tmux new -s "{self._get_window_title()}" {cmd} '

        if WRAP_IN_TERMINAL in self.cmd:
            cmd = f"{cmd} ; tail -f /dev/null"

        cmd = self._try_to_wrap_in_terminal(cmd)

        logging.info(f"Command to run: {cmd}")
        result = self._execute(cmd)
        logging.info(f"Result finished: {result}")
        return self.return_result(result)

    def _try_to_wrap_in_terminal(self, cmd):
        if WRAP_IN_TERMINAL in self.cmd:
            logging.info("Running it in a new terminal")

            cmd = Terminal().wrap_cmd_into_terminal(
                cmd,
                title=self._get_window_title(),
                hold_terminal_open_on_end=True,
                return_command=True,
            )
            logging.info(f"Command to run: {cmd}")

        return cmd

    def _get_window_title(self):

        if "window_title" in self.cmd:
            return self.cmd["window_title"]

        title = self.cmd["cmd"]
        if "focus_match" in self.cmd:
            title = self.cmd["focus_match"]

        return remove_special_chars(title, [" "])

    def _execute(self, cmd):
        logging.info(f"Command to run: {cmd}")
        if (
            self.context.is_group_command()
            and not self.context.should_execute_sequentially()
        ):
            return shell.run_command_no_wait(cmd)

        if self.context.should_execute_sequentially():
            return shell.run_with_result(cmd)

        return shell.run(cmd)

    def return_result(self, result):
        if "notify-result" in self.cmd:
            send_notification(result)

        return result

    def copiable_part(self):
        return self.cmd["cmd"]
