# User Guide



[Quafu]([ScQ-Cloud/pyquafu (github.com)](https://github.com/ScQ-Cloud/pyquafu)) is a Python toolkit for submitting quantum circuits on the superconducting quantum computing cloud [Quafu](http://quafu.baqis.ac.cn/). If you haven't used quafu before, see the [docs](https://scq-cloud.github.io/).

Quafu Runtime is new part of the Quantum Services on Quafu cloud. With Runtime, you can mix classical and quantum programs and send them to the cloud for execution, reducing the number of data transfers and execution time.

This module provides the interface for accessing the Runtime.

## Installation

You can install this package using pip:

```bash
pip install quafu-runtime
```



## Account Setup

Quafu Runtime is part of Quafu Cloud, so you can just use Quafu Account. Firstly, you need to register on the [Quafu](http://quafu.baqis.ac.cn/) website and get your apitoken `<your API token>`. If you already have an account, execute the following code to set up your account.

```python
from quafu_runtime import Account
account = Account()
account.save_apitoken("<your API token>")
```

You only need to save your token once and no longer need to execute above code when you use quafu runtime after, except if you want to change your account.




## Quafu Runtime programs

Quafu Runtime provides interface to upload your program to the cloud and then run it, and you can get your program's output in many ways.

### Finding your programs

List all available programs:

```python
from quafu_runtime import RuntimeService
service = RuntimeService()
service.list_programs()
```

### Upload your first program

`Runtime.upload_program()` is provided to upload your program, the function's prototype is:   

```python
upload_program(data: str, metadata: dict)
```

Argument `data` is used to pass your program source code, you can put your code into `data` directly or write it in a file and put the file path in.

Argument `metadata` is used to pass the metadata of the program. It's `dict` type in python,  and the supported keys are as follows:

| Key                | Description                                                  |
| ------------------ | ------------------------------------------------------------ |
| name               | Name of the program that should be unique between your programs. |
| description        | Description of program.                                      |
| max_execution_time | Maximum execution time the program will continuous run.      |
| is_public          | Whether the program should be public.                        |

The function will return `program_id` which can represent the program if upload program successfully.

The format of the program source code has strict requirements, as follows:

```python
import numpy as np
from quafu import QuantumCircuit
from quafu import simulate
"""Runtime program template."""


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
    userpub.publish("This is a interim message")
    print("Hello, world")
    return {
        'msg': 'The data you want get'
    }

```

Just as the template program source code above shown, the entry point of the program is a function `run`, the name and the argument of the function is the same as template. 

The first argument `task` can be used to run your circuit as [Quafu](http://quafu.baqis.ac.cn/) . It's one thing with `quafu.Task` because  `task` is an instance of `quafu.Task` class. So you can use it in your program just like you are using `Quafu.Task`.

The second argument `userpub` is used to return your interim result, which will help you monitor program execution. You can just call `userpub.publish()` function to return your interim result.

The last argument `params` is your program's parameters which will be passed in when you run the program by calling `RuntimeService.run()`. You can run the program with different parameters each time using `params` argument. It's type should be of `bytes` in python or be able to be implicitly converted to type `bytes`  because of the correctness of the transmission and the flexibility in use. 

Besides, after executing the `run` function, you can return your final result using `return` statement, and specifies what to return. As the same reason, your result should be `bytes` type or  type which can be implicitly converted to type `bytes`. The same is true for interim result. You can convert it back after receiving it.



### Executing your program

```python
from quafu_runtime import RuntimeService
service = RuntimeService()
job = service.run(program_id = "<your program id>",params = "<parameters of program>")
print(f"job ID: {job.job_id()}")
result = job.result(wait=True)
```

`RutimeService.run` is the only way to run your program which has been uploaded to cloud.

The parameters of the function is `program_id`, `name` and `params`.  `name` is the name of program. One of `program_id` or `name` should be passed to locate your program. The `params` argument is used by `run` entry function of your program. So you should be sure the content of `params` can be implicitly convert to `bytes` or  just `bytes`.

And you will get a job instance after calling `run`, you can get result using it. The result is the data returned by your program.



## Quafu Runtime Job

### Get result of your job

`RutimeService.run` will return an instance of `RuntimeJob` class that represent your running job on the cloud. You can use `RuntimeJob.job_id()` to get job ID and use `RuntimeJob.result()` to get job's result which will be returned by `run` function of your program. The `wait` argument of `RuntimeJob.result()` determines weather wait for the job return. If set to `False`, it will return no matter your job's status. 

Or you can construct a `RuntimeJob` instance is you have your job's job_id as follows:

```python
from quafu_runtime import RuntimeJob
job = RuntimJob(job_id="<your job id>")
job.result()
def callback(data):
    """Process interim result data here."""
    print(data)
job.interim_results(callback=callback)
```

The `RuntimeJob.interim_results()` can receive your job's interim results, which is returned by `userpub.publish` .  One argument of `interim_result` is a callback function, which has two argument `job_id` and `data`. `job_id` represents job' ID while `data` represent your interim result data. Because there are `bytes` be sent back, you should `decode` it before processing it in your callback function. Another way to do it is pass a decoder function to `interim_result`.



## Other Runtime features

Besides the main features above, there are also some auxiliary features.

You can use `RuntimeService.update_program` to update a program on the cloud, `RuntimeService.delete_program` to delete a program, and `RuntimeService.program` to get all message

of a program.

Meanwhile, `RuntimeJob.cancel` can be used to cancel a job.  `RuntimeJob.status` can used to get job's status. `RuntimeJob.delete` can be used to delete a job.  `RuntimeJob.err_msg` can be used to get error message if job failed. 

Moreover, `RuntimeJob.logs` can be used to get logs after job finished. You can just use `print` function of python to generate your logs message.



At last, be care of your result's type. Otherwise the transfer will fail.



## Authors

This project is developed by the quantum cloud computing team at the Beijing Academy of Quantum Information Sciences.

























