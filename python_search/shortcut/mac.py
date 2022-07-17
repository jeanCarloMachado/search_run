import os


class Mac:
    """
    Mac support for tool iCanHazShortcut

    """

    def __init__(self, configuration):
        self.configuration = configuration
        import os

        self.config_folder = f'{os.environ["HOME"]}/.config/iCanHazShortcut/'

    def generate(self):
        print("Generating macos shortctus")

        shortcut_found = False
        # starts with number 2 as number 1 is static in config.part1
        shortcut_number = 2
        import shutil

        shutil.copyfile(
            f"{self.config_folder}/config.ini.part1", f"{self.config_folder}/config.ini"
        )

        for key, content in list(self.configuration.commands.items()):
            if not type(content) is dict:
                continue

            if "mac_shortcut" in content:
                self._add_shortcut(content["mac_shortcut"], key, shortcut_number)
                shortcut_found = True
                shortcut_number += 1

            if "mac_shortcuts" in content:
                for shortcut in content["mac_shortcuts"]:
                    self._add_shortcut(shortcut, key, shortcut_number)
                    shortcut_found = True
                    shortcut_number += 1

        if not shortcut_found:
            print("No shortcuts found for mac")
            return

        os.system(f"cd {self.config_folder} ; add_bom_to_file.sh config.ini")

        os.system("pkill -f iCanHaz")
        os.system("open -a iCanHazSHortcut")

    def _add_shortcut(self, shortcut, key, shortcut_number):
        print(f"Generating shortcut for {key}")

        shortcut_content = self._entry(shortcut, key, shortcut_number)
        with open(f"{self.config_folder}/config.ini", "a") as myfile:
            print(shortcut_content)
            myfile.write(shortcut_content)

    def _entry(self, shortcut, key, number) -> str:
        shortcut = shortcut
        return f"""
        
[shortcut{number}]
shortcut = {shortcut}
action = {key}
command = log_command.sh search_run run_key '{key}'
workdir = 
enabled = yes
"""
