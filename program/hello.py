import numpy as np
from quafu import QuantumCircuit
from quafu import simulate
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


def run(task, userpub, params):
    """The entry point of the program.
    Make sure the first and the second arg of `run` is `task` and `userpub`.

    Args:
        task(quafu.task): task instance used to run a circuit.
        userpub(quafu_runtime.program.userpub): UserPub instance used to publish interim result.
        params: User inputs.

    Returns:
        Final result of the program.

    The result and your interim result will be jsonfy before send to client,
    so you should encode your data to `bytes`, and decode it when you get it
    """
    q = prepare_circuits()
    simu_res = simulate(q)
    print("Hello World!", params)
    return {
        "num": simu_res.num,
        "probabilities": simu_res.probabilities.tolist(),
    }
