import numpy as np
from quafu import QuantumCircuit
from quafu import Task


HAMILTONIAN = [-1.0537157499303196, [], 0.3939591228374733, ['Z0'], 0.39395912283747336, ['Z1'],
    0.011236311320494491, ['Z0', 'Z1'], 0.18129104765420154, ['X0', 'X1']]
NUM_Q=2
NUM_LAYER=1

# circuit for h2 in 2 qubits
def ry_cascade(nqubits, nlayer, params):
    c = QuantumCircuit(nqubits)
    for i in range(nqubits):
        c.x(i)
    count = 0
    for i in range(nqubits):
        c.ry(i, params[count])
        count += 1
    for _ in range(1, nlayer+1):
        for i in range(nqubits-1):
            c.cnot(i, i+1)
        for i in range(nqubits):
            c.ry(i, params[count])
            count += 1
        for i in range(nqubits-1):
            c.cnot(i, i+1)
        for i in range(nqubits):
            c.ry(i, params[count])
            count += 1
    return c

def measure_single(circuit, term, cbits):
    m = []
    for i in range(len(term)):
        if term[i][0] == 'Z':
            m = m + [eval(term[i][1:])]
        elif term[i][0] == 'X':
            iqubit = eval(term[i][1:])
            m = m + [iqubit]
            circuit.h(iqubit)
        elif term[i][0] == 'Y':
            iqubit = eval(term[i][1:])
            m = m + [iqubit]
            #circuit.sdg(iqubit)
            circuit.rz(iqubit, np.pi/2)
            circuit.rz(iqubit, np.pi/2)
            circuit.rz(iqubit, np.pi/2)
            circuit.h(iqubit)
    circuit.measure(m, cbits=cbits[:len(m)])
    return circuit

def measure(params, shots, task: Task):
    energy = 0
    cbits = list(np.arange(NUM_Q))
    for i in range(3, len(HAMILTONIAN), 2):
        qc = ry_cascade(NUM_Q, NUM_LAYER, params)  # get circuit
        qc = measure_single(qc, HAMILTONIAN[i], cbits)
        res = task.send(qc, wait=True).res
        print(res)
        for key in res.keys():
            d = res[key]/shots
            eig = 1
            for k in key:
                if k == '1':
                    eig = -eig
            energy += eig * d * HAMILTONIAN[i-1]
    return energy+HAMILTONIAN[0]

def parameter_shift(params, shots, task: Task):
    amps_grad = np.zeros_like(params)
    for i in range(len(params)):
        amps_plus, amps_minus = params.copy(), params.copy()
        amps_plus[i] += np.pi/2
        amps_minus[i] -= np.pi/2
        value_plus = measure(amps_plus, shots, task)
        value_minus = measure(amps_minus, shots, task)
        amps_grad[i] += 0.5 * (value_plus - value_minus)
    return params - amps_grad

def run(task: Task, userpub, params):
    params = np.random.uniform(-2*np.pi, 2*np.pi, 6)

    shots = 100
    task.config(backend="ScQ-P18", shots=shots, compile=True)

    # use for loop get energy one by one
    energys = []
    for i in range(10):
        params = parameter_shift(params, shots, task)
        energy = measure(params, shots, task)
        print(f'{i} iterations, energy: {energy:.10f}')
        energys.append(energy)
    return energys, params.tolist()
