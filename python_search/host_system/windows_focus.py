import os


class Focus:

    def focus_register_new(self):
        result = os.system("""
        osascript -e 'tell application "System Events" to tell process "python3" 
    set frontmost to true
    windows where title contains "Register New" 
end tell' 
        """)

        return True if result == 0 else False



if __name__ == "__main__":
    import fire
    fire.Fire(Focus)
