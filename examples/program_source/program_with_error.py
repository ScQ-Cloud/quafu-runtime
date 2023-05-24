from quafu import *
def run(task, userpub, params):
    """The entry point of the program."""
    print("Hello World!", params)
    # An error
    cout("xxx")
    # unreachable
    return {
        "result": 'error'
    }