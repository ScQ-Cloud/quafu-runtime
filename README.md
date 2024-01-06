> This package is still in a beta stage. For API token, please register this http://120.46.209.71/ website instead of the [official website](https://quafu.baqis.ac.cn/). Please file an [issue](https://github.com/ScQ-Cloud/quafu-runtime/issues) if you met any problems. 

# Quafu Runtime Client


Quafu is a Python toolkit for submitting quantum circuits on the superconducting quantum computing cloud [Quafu](http://quafu.baqis.ac.cn/).

Quafu Runtime is new part of the Quantum Services on Quafu cloud. With Runtime, you can mix classical and quantum programs and send them to the cloud for execution, reducing the number of data transfers and execution time.

This module provides the interface for accessing the Runtime.

## Installation

You can install this package using pip:

```bash
pip install quafu-runtime
```

Or you can build from source:

```bash
pip install .
```


## Account Setup

Quafu Runtime is part of Quafu Cloud, so you can just use Quafu Account. Firstly, you need to register on the [Quafu](http://quafu.baqis.ac.cn/) website and get your apitoken `<your API token>`. If you already have an account, execute the following code to set up your account.

```python
from quafu_runtime import Account
from quafu_runtime import RuntimeService

account = Account(api_token=<your quafu api token>)
service = RuntimeService(account=account)
```

You only need to save your token once and no longer need to execute above code when you use quafu runtime after, except if you want to change your account.



## Quafu Runtime programs

Quafu Runtime provides interface to upload your program to the cloud and then run it, and you can get your program's output in many ways.

### Upload your programs
```python
metadata = {"name": "multi-task", "backend": "testbackend"}
program_id = service.upload_program(data='examples/program_source/multi-task.py', metadata=metadata)
```

### Finding your programs

List all available programs:

```python
service.list_programs()
```

### Executing your program

```python
job = service.run(program_id = "<your program id>", params = <parameters of program>)
print(f"job ID: {job.job_id()}")
```

And you will get a job instance after calling `run`, you can get result using it.

### Get program result

```
result = job.result(wait=True)
```

The result is the data returned by your program.

### Retrieve job

You can also save your job id after submitting it using `service.run`, then you can sign off and get back later to retrieve your job results.

First [create your account instance](#account-setup). Then simply create a job instance following:

```python
from quafu_runtime import RuntimeJob

job = RuntimeJob("<job-id>", account=account)
```

Then you can get your job results using `job.result()`.


## Command line interface
We also provide a cli tool for convenience.


Show help info.
```bash
python runtime_cli.py -h
```

List available commands.
```bash
python runtime_cli.py --show-methods
```

Run a specific command.

```bash
python runtime_cli.py --run run_get_programs
```

Some commands require input additional params, to show required params, you could run:

```bash
python runtime_cli.py --run run_upload
```

The output should be like
```
program_name,program_path must be set!
```

Then you can use this command to upload a program
```bash
python runtime_cli.py --run run_upload --program-name "name-of-the-program" --program-path path/to/this/program
```

For other commands like `run_job_sync, run_update_program`, you can follow the same procedure to use them.


## Document

If you want to learn more features about Runtime, Please see the website [docs](https://scq-cloud.github.io/).


## Authors

This project is developed by the quantum cloud computing team at the Beijing Academy of Quantum Information Sciences.



## License

[Apache License 2.0](https://github.com/Qiskit/qiskit-ibm-runtime/blob/main/LICENSE.txt).
