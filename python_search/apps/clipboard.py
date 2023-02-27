import os
from typing import Union
from python_search.environment import is_mac


def chomp(x):
    """remove special chars from end of string"""
    if x.endswith("\r\n"):
        return x[:-2]
    if x.endswith("\n") or x.endswith("\r"):
        return x[:-1]
    return x


class Clipboard:
    def get_content(self, source="--primary") -> str:
        """
        Accepted values are --primary and --clipboard
        """

        cmd = f"xsel {source} --output"
        if is_mac():
            cmd = "pbpaste"

        import subprocess

        result = subprocess.getoutput(cmd)

        result = chomp(result)

        return result

    def set_content(
        self, content: Union[str, None] = None, enable_notifications=True, notify=False
    ):
        """
        Put a string in the clipboard.
        If no string is provided it tries to fetch it from stdin
        :param content:
        :param enable_notifications:
        :return:
        """

        if not content:
            import sys

            data = sys.stdin.readlines()
            content = "\n".join(data)

        if not content:
            raise Exception("Tryring to set empty to clipboard")

        if type(content) != str:
            raise Exception("Tryring to set a non string to clipboard")

        def shellquote(s):
            return "'" + s.replace("'", "'") + "'"

        sanitized = shellquote(content)

        clipboard_cmd = "xsel --clipboard --primary --input"
        if is_mac():
            clipboard_cmd = "pbcopy"

        cmd = f"echo {sanitized} | {clipboard_cmd}"

        print(f"Setting clipboard content: {sanitized}")
        result = os.system(cmd)
        if result != 0:
            raise Exception("Failed to set clipboard content")

        if enable_notifications or notify:
            from python_search.apps.notification_ui import send_notification

            send_notification(f"Content copied: {sanitized}")


def main():
    import fire

    fire.Fire(Clipboard)


if __name__ == "__main__":
    main()
