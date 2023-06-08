from time import sleep
import numpy as np
from quafu import QuantumCircuit
from quafu import simulate
from quafu import Task
"""A sample runtime program called hello-world that submits random circuits."""


def prepare_circuits():
    """Prepare a circuits."""
    q = QuantumCircuit(5)
    q.x(0)
    q.x(1)
    q.cnot(2, 1)
    q.ry(1, np.pi / 2)
    q.rx(2, np.pi)
    q.rz(3, 0.1)
    q.cz(2, 3)
    measures = [0, 1, 2, 3]
    cbits = [0, 1, 2, 3]
    q.measure(measures,  cbits=cbits)
    return q


def run(task: Task, userpub, params):
    """The entry point of the program.
    Make sure the first and the second arg of `run` is `task` and `userpub`.

    """
    q = prepare_circuits()
    #user = User()
    #user.save_apitoken("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjcsImV4cCI6MTY4ODM1OTA4M30.lu2i_DFvu2HBb25u_aWTdaG7X4eoH51j1vfbYErx0_w")
    #user.load_account()
    task.config(backend="ScQ-P10", shots=100, compile=True)

    num_iter = 2

    for i in range(num_iter):
        sleep(2)
        res = task.send(q, wait=False)
        print(f"Result of task #{i}: {res}")

    simu_res = simulate(q)
    print("Hello World!", params)
    return {
        "num": simu_res.num,
        "probabilities": simu_res.probabilities.tolist(),
    }


if __name__ == '__main__':
    task = Task()
    run(task, None, "")
