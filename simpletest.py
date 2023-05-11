import datetime
import os
import time
from time import sleep

from clients.account import Account
from job.job import Job
from quafu_runtime_service import RuntimeService


class TestAPI:
    @staticmethod
    def TestUpload():
        account = Account("testapitoken")
        service = RuntimeService(account)
        metadata = {"name": "for-while", "backend": "testbackend"}
        id2 = service.upload_program(data='program/for-while.py', metadata=metadata)
        metadata = {"name": "hello", "backend": "testbackend"}
        id1 = service.upload_program(data='program/hello.py', metadata=metadata)
        metadata = {"name": "raise-exception", "backend": "testbackend"}
        id3 = service.upload_program(data='program/raise-exception.py', metadata=metadata)
        metadata = {"name": "long-run-task", "backend": "testbackend"}
        id4 = service.upload_program(data='program/long-run-task.py', metadata=metadata)
        print('id1:', id1)
        print('id2:', id2)
        print('id3:', id3)
        print('id4:', id4)

    @staticmethod
    def TestUploadMore(num: int):
        account = Account("testapitoken")
        service = RuntimeService(account)
        for i in range(num):
            metadata = {"name": "testname" + str(i + 10), "backend": "testbackend"}
            program_id = service.upload_program(data='program/hello.py', metadata=metadata)
            print(program_id)

    @staticmethod
    def TestGetPrograms():
        account = Account("testapitoken")
        service = RuntimeService(account)
        service.list_programs(refresh=True, detailed=False, limit=20)
        # service.program(program_id='e2afae0de2de482e9b057e8f510559ac')

    @staticmethod
    def TestUpdateProgram():
        account = Account("testapitoken")
        service = RuntimeService(account)
        service.update_program(program_id='1304493a31d34e4d8e73e3164d0cb8ed',
                               data='program/raise-exception.py',
                               description='The program is created by QuaFu')
        # service.program()

    @staticmethod
    def TestCheckSourceCode():
        account = Account("testapitoken")
        service = RuntimeService(account)
        metadata = {"name": "program_with_error", "backend": "testbackend"}
        service.upload_program(data='program/program_with_error.py',
                               metadata=metadata)

    @staticmethod
    def TestDelProgram():
        account = Account("testapitoken")
        service = RuntimeService(account)
        service.delete_program(program_id='f08e063a0e7b42c48815cb5004fac7f2')
        # service.program()

    @staticmethod
    def TestRun():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(name='hello', backend="py_simu", inputs="zsl")
        result = job.result(wait=True)
        print(result)
        # return job

    @staticmethod
    def TestJobCancel(job_id: str):
        account = Account("testapitoken")
        service = RuntimeService(account)
        service.cancel(job_id)

    @staticmethod
    def TestJob_nowait():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="409c55020cda4eedbae341fe316c1970", backend="py_simu", inputs="zxxx")
        print(job.job_id())
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sleep(5)
        response = job.result(wait=False)
        print(response)

    @staticmethod
    def parallelTest(num):
        import multiprocessing
        nums = num
        plist = []
        for i in range(nums):
            p = multiprocessing.Process(target=TestAPI.TestJob_wait)
            plist.append(p)
            p.start()
        for p in plist:
            p.join()

    @staticmethod
    def TestJob_wait():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(name='long-run-task', backend="py_simu", inputs="zxxx")
        print(job.job_id())
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(job.result(wait=True))

    @staticmethod
    def TestWebsockets():
        account = Account("testapitoken")
        servie = RuntimeService(account)
        job = servie.run(name='long-run-task', inputs='zxxx')
        job.interim_results(callback=callback)
        job.interim_result_cancel()
        print(job.result(wait=True))


def callback(job_id, message):
    print(f"job_id:{job_id}, message:{message}")


if __name__ == '__main__':
    print(os.getcwd())
    # TestAPI.TestRun()
    # TestAPI.TestJob_wait()
    # TestAPI.TestJob_nowait()
    # TestAPI.parallelTest(num=5)
    # TestAPI.TestGetPrograms()
    # TestAPI.TestUpload()
    # TestAPI.TestUploadMore(10)
    # TestAPI.TestUpdateProgram()
    # TestAPI.TestDelProgram()
    job = TestAPI.TestRun()
    #TestAPI.TestJobCancel(job.job_id())
    # TestAPI.TestJob_wait()
    # TestAPI.TestCheckSourceCode()
    # TestAPI.TestWebsockets()