from time import sleep
def run(task, userpub, params):
    """The entry point of the program."""
    # q = prepare_circuits()
    # simu_res = simulate(q)
    print("Hello World!", params)
    x = 10
    while x:
        sleep(10)
        message = 'publish from job '+str(x)
        userpub.publish(message.encode())
        print("Sleep 10...")
        x = x-1
    # no possible go here.
    return {
        "result": params
    }
