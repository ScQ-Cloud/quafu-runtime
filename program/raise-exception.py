
"""
It's program used to check api.
"""

def run(backend, userpub, params):
    """The entry point of the program."""
    print("Hello World!", params)
    raise Exception("Raised by program")
    # unreachable
    return {
        "result": 'error'
    }
