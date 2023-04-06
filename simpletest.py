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
    def TestUploadMore(num: int):
        account = Account("testapitoken")
        service = RuntimeService(account)
        for i in range(num):
            metadata = {"name": "testname"+str(i+10), "backend": "testbackend"}
            program_id = service.upload_program(data='program/hello.py', metadata=metadata)
            print(program_id)

    @staticmethod
    def TestGetPrograms():
        account = Account("testapitoken")
        service = RuntimeService(account)
        service.list_programs(refresh=True, detailed=True, limit=20)

    @staticmethod
    def TestRun():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="784376be3f8b40309be7e1e9ab7c7404", backend="py_simu", inputs="zsl")
        print(job.job_id())

    @staticmethod
    def TestJob_nowait():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="784376be3f8b40309be7e1e9ab7c7404", backend="py_simu", inputs="zxxx")
        print(job.job_id())
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        # sleep(5)
        response = job.result()
        print(response)

    @staticmethod
    def parallelTest(num):
        import multiprocessing
        nums = num
        plist = []
        for i in range(nums):
            p = multiprocessing.Process(target=TestJob_wait)
            plist.append(p)
            p.start()
        for p in plist:
            p.join()


def TestJob_wait():
    account = Account("testapitoken")
    service = RuntimeService(account)
    job = service.run(program_id="784376be3f8b40309be7e1e9ab7c7404", backend="py_simu", inputs="zxxx")
    print(job.job_id())
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    job.result(wait=True)


def test_args(name: str = None):
    if name:
        print("name:", name)
    else:
        print("None")


if __name__ == '__main__':
    print(os.getcwd())
    # TestAPI.TestJob_wait()
    # TestAPI.TestJob_nowait()
    # TestAPI.parallelTest(num=5)
    TestAPI.TestGetPrograms()
