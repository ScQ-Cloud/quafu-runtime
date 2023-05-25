import numpy as np
from quafu import QuantumCircuit
from quafu import simulate
"""Runtime program template.

It takes a
:class:`Quafu.Task` and a :class:`UserPub` that can be used to
send circuits to run on the backend and interim messages to the user.
"""


def prepare_circuits():
    """Prepare a circuits."""
    q = QuantumCircuit(5)
    q.x(0)
    q.x(1)
    q.cnot(0, 1)
    measures = [0, 1]
    cbits = [0, 1]
    q.measure(measures,  cbits=cbits)
    return q


def run(task, userpub, params):
    """The entry point of the program.

    Make sure the arguments of `run` is `task`, `userpub` and `params`.

    Args:
        task(pyquafu.Task): task instance used to run a circuit.
        userpub(quafu_runtime.program.templates.userpub): UserPub instance used to publish interim result.
        params: User inputs.

    Returns:
        Final result of the program.

    The result and your interim result will be jsonfy before send to client.
    So you should encode your data to `bytes`, and decode it when you get it.
    And remember write your encode code in the program file.
    """
    q = prepare_circuits()
    simu_res = simulate(q)
    userpub.publish("This is a interim message")
    return {
        "num": simu_res.num,
        "probabilities": simu_res.probabilities.tolist(),
        "message": "final result"
    }
