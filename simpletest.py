import datetime
import os
from time import sleep

from clients.account import Account
from job.job import Job
from quafu_runtime_service import RuntimeService


class TestAPI:
    @staticmethod
    def TestUpload():
        account = Account("testapitoken")
        service = RuntimeService(account)
        metadata = {"name": "hello", "backend": "testbackend"}
        id1 = service.upload_program(data='program/hello.py', metadata=metadata)
        metadata = {"name": "for-while", "backend": "testbackend"}
        id2 = service.upload_program(data='program/for-while.py', metadata=metadata)
        metadata = {"name": "raise-exception", "backend": "testbackend"}
        id3 = service.upload_program(data='program/raise-exception.py', metadata=metadata)
        print('id1:', id1)
        print('id2:', id2)
        print('id3:', id3)

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
    def TestDelProgram():
        account = Account("testapitoken")
        service = RuntimeService(account)
        service.delete_program(program_id='f08e063a0e7b42c48815cb5004fac7f2')
        # service.program()

    @staticmethod
    def TestRun():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="168bce332e8144d686def23145db1651", backend="py_simu", inputs="zsl")
        print(job.job_id())

    @staticmethod
    def TestJob_nowait():
        account = Account("testapitoken")
        service = RuntimeService(account)
        job = service.run(program_id="168bce332e8144d686def23145db1651", backend="py_simu", inputs="zxxx")
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
            p = multiprocessing.Process(target=TestJob_wait)
            plist.append(p)
            p.start()
        for p in plist:
            p.join()


def TestJob_wait():
    account = Account("testapitoken")
    service = RuntimeService(account)
    job = service.run(program_id="168bce332e8144d686def23145db1651", backend="py_simu", inputs="zxxx")
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
    # TestAPI.TestRun()
    # TestAPI.TestJob_wait()
    # TestAPI.TestJob_nowait()
    # TestAPI.parallelTest(num=5)
    TestAPI.TestGetPrograms()
    # TestAPI.TestUpload()
    # TestAPI.TestUploadMore(10)
    # TestAPI.TestUpdateProgram()
    # TestAPI.TestDelProgram()