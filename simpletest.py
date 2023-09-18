import argparse
import datetime
import os
import time
from time import sleep
from quafu_runtime.clients.account import Account
from quafu_runtime.job.job import RuntimeJob
from quafu_runtime.quafu_runtime_service import RuntimeService

API_TOKEN = "ENqgPTQ0OnS5hUhy0hlLwoDP_sPoNsj4jitGoJ7aUVX.9VzN0UzNwcTO2EjOiAHelJCL3ITM6ICZpJye.9JCVXpkI6ICc5RnIsIiN1IzUIJiOicGbhJye"

class TestAPI:
    @staticmethod
    def TestUpload():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        #metadata = {"name": "for-while", "backend": "testbackend"}
        #id2 = service.upload_program(data='examples/program_source/for-while.py', metadata=metadata)
        metadata = {"name": "hello", "backend": "testbackend"}
        id1 = service.upload_program(data='examples/program_source/hello.py', metadata=metadata)
        #metadata = {"name": "raise-exception", "backend": "testbackend"}
        #id3 = service.upload_program(data='examples/program_source/raise-exception.py', metadata=metadata)
        #metadata = {"name": "long-run-task", "backend": "testbackend"}
        #id4 = service.upload_program(data='examples/program_source/long-run-task.py', metadata=metadata)
        #metadata = {"name": "multi-task", "backend": "testbackend"}
        #id5 = service.upload_program(data='examples/program_source/multi-task.py', metadata=metadata)
        print('id1:', id1)
        #print('id2:', id2)
        #print('id3:', id3)
        #print('id4:', id4)
        #print('id5:', id5)

    @staticmethod
    def TestUploadMore(num: int):
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        for i in range(num):
            metadata = {"name": "testname" + str(i + 10), "backend": "testbackend"}
            program_id = service.upload_program(data='examples/program_source/hello.py', metadata=metadata)
            print(program_id)

    @staticmethod
    def TestGetPrograms():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        service.list_programs(refresh=True, detailed=False, limit=20)
        # service.program(program_id='e2afae0de2de482e9b057e8f510559ac')

    @staticmethod
    def TestGetProgram():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        res = service.program(name='long-run-task')
        print(res)

    @staticmethod
    def TestUpdateProgram():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        service.update_program(program_id='3eaeb8960d22487abd6d8b4b91f40461',
                               data='examples/program_source/raise-exception.py',
                               is_public=True,
                               description='The program is created by QuaFu')
        # service.program()

    @staticmethod
    def TestCheckSourceCode():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        metadata = {"name": "program_with_error", "backend": "testbackend"}
        service.upload_program(data='examples/program_source/program_with_error.py',
                               metadata=metadata)

    @staticmethod
    def TestDelProgram():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        service.delete_program(program_id='8ca38b518f1546c89e9dec112b997e4b')
        # service.program()

    @staticmethod
    def TestRun():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        job = service.run(name='hello', backend="py_simu", inputs="zsl")
        result = job.result(wait=True)
        print(result)
        # return job

    @staticmethod
    def TestJob_nowait():
        account = Account(api_token=API_TOKEN)
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
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        #job = service.run(name='long-run-task', backend="py_simu", inputs="zxxx")
        #job = service.run(name='long-run-task', backend="py_simu")
        #job = service.run(name='hello', backend="py_simu")
        job = service.run(name='multi-task', backend="py_simu")
        print(job.job_id())
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(job.result(wait=True))
        print(job.logs())

    @staticmethod
    def TestWebsockets():
        account = Account(api_token=API_TOKEN)
        servie = RuntimeService(account)
        job = servie.run(name='long-run-task', inputs='zxxx')
        job.interim_results(callback=callback)
        # job.interim_result_cancel()
        print(job.result(wait=True))

def callback(job_id, message):
    print(f"job_id:{job_id}, message:{message}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run different TestAPI methods based on arguments.')
    parser.add_argument('--test', type=str, help='The name of the TestAPI static method to run (e.g., TestUpload, TestRun, etc.)')
    parser.add_argument('--show-methods', action='store_true', help='Show available TestAPI methods')
    args = parser.parse_args()

    if args.show_methods:
        print("Available TestAPI methods:")
        for method_name in dir(TestAPI):
            if method_name.startswith("Test") and callable(getattr(TestAPI, method_name)):
                print(f" - {method_name}")
    elif args.test:
        test_method = getattr(TestAPI, args.test, None)
        if test_method and callable(test_method):
            test_method()
        else:
            print(f"Invalid test method: {args.test}")
    else:
        print("No test method provided. Use --test argument to specify the method to run.")
