from time import sleep


def run(backend, userpub, params):
    """The entry point of the program."""
    # q = prepare_circuits()
    # simu_res = simulate(q)
    print("Hello World!", params)
    while True:
        sleep(10)
        print("Sleep 10...")
    # no possible go here.
    return {
        "result": params
    }