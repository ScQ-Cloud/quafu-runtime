import datetime
import os
from time import sleep

from clients.account import Account
from job.job import Job
from quafu_runtime_service import RuntimeService

class TestAPI():
    @staticmethod
    def TestUpload():
        account = Account("testapitoken")
        service = RuntimeService(account)
        metadata = {"name": "testname1", "backend": "testbackend"}
        program_id = service.upload_program(data='program/hello.py', metadata=metadata)
        print(program_id)
    @staticmethod
    def TestRun():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="784376be3f8b40309be7e1e9ab7c7404", backend="py_simu", inputs="zsl")
        print(job.job_id())

    @staticmethod
    def TestJob():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="784376be3f8b40309be7e1e9ab7c7404", backend="py_simu", inputs="zxxx")
        print(job.job_id())
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sleep(5)
        response = job.result()
        print(response)

if __name__ == '__main__':
    print(os.getcwd())
    TestAPI.TestRun()