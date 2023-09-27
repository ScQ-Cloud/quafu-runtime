import sys
import argparse
import datetime
from deprecated import deprecated
from time import sleep
from quafu_runtime.clients.account import Account
from quafu_runtime.quafu_runtime_service import RuntimeService

API_TOKEN = "ENqgPTQ0OnS5hUhy0hlLwoDP_sPoNsj4jitGoJ7aUVX.9VzN0UzNwcTO2EjOiAHelJCL3ITM6ICZpJye.9JCVXpkI6ICc5RnIsIiN1IzUIJiOicGbhJye"


class RuntimeAPI:
    """Collection of quafu runtime APIs"""

    @staticmethod
    def run_upload(args):
        check_non_empty_args(
            program_name=args.program_name, program_path=args.program_path
        )
        account = Account(api_token=args.api_token)
        service = RuntimeService(account)
        metadata = {"name": args.program_name, "backend": "testbackend"}
        pid = service.upload_program(data=args.program_path, metadata=metadata)
        print(f"program_id: {pid}")

    # TODO(zhaoyilun): refactor
    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run_upload_more(num: int):
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        for i in range(num):
            metadata = {"name": "testname" + str(i + 10), "backend": "testbackend"}
            program_id = service.upload_program(
                data="examples/program_source/hello.py", metadata=metadata
            )
            print(program_id)

    @staticmethod
    def run_get_programs(args):
        account = Account(api_token=args.api_token)
        service = RuntimeService(account)
        service.list_programs(refresh=True, detailed=False, limit=20)

    # TODO(zhaoyilun): refine
    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run_get_program():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        res = service.program(name="long-run-task")
        print(res)

    @staticmethod
    def run_update_program(args):
        # Check arguments
        check_non_empty_args(program_id=args.program_id, program_path=args.program_path)

        # Init account
        account = Account(api_token=args.api_token)
        service = RuntimeService(account)

        # Update program
        service.update_program(
            program_id=args.program_id,
            data=args.program_path,
            is_public=True,
            description=args.description,
        )

    # TODO(zhaoyilun): refine
    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run_check_source_code():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        metadata = {"name": "program_with_error", "backend": "testbackend"}
        service.upload_program(
            data="examples/program_source/program_with_error.py", metadata=metadata
        )

    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run_del_program():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        service.delete_program(program_id="8ca38b518f1546c89e9dec112b997e4b")

    # TODO(zhaoyilun): refine
    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        job = service.run(name="hello", backend="py_simu")
        result = job.result(wait=True)
        print(result)

    # TODO(zhaoyilun): refine
    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run_job_async():
        account = Account(api_token=API_TOKEN)
        service = RuntimeService(account)
        job = service.run(
            program_id="409c55020cda4eedbae341fe316c1970", backend="py_simu"
        )
        print(job.job_id())
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        sleep(5)
        response = job.result(wait=False)
        print(response)

    # TODO(zhaoyilun): refine
    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run_parallel(num):
        import multiprocessing

        nums = num
        plist = []
        for i in range(nums):
            p = multiprocessing.Process(target=RuntimeAPI.run_job_sync)
            plist.append(p)
            p.start()
        for p in plist:
            p.join()

    @staticmethod
    def run_job_sync(args):
        # Check arguments
        check_non_empty_args(program_name=args.program_name)

        # Init account
        account = Account(api_token=args.api_token)
        service = RuntimeService(account)

        # Launch a job
        job = service.run(name=args.program_name, backend="py_simu")
        print(job.job_id())
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print(job.result(wait=True))
        print(job.logs())

    # TODO(zhaoyilun): needs refine
    @deprecated(reason="needs refine")
    @staticmethod
    def legacy_run_websockets():
        account = Account(api_token=API_TOKEN)
        servie = RuntimeService(account)
        job = servie.run(name="long-run-task")
        job.interim_results(callback=callback)
        print(job.result(wait=True))


def callback(job_id, message):
    print(f"job_id:{job_id}, message:{message}")


def check_non_empty_args(**kwargs):
    required_params = []
    for k, v in kwargs.items():
        if v == "" or v is None:
            required_params.append(k)
    if required_params:
        print(f"{','.join(required_params)} must be set!")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Run different RuntimeAPI methods based on arguments."
    )
    parser.add_argument(
        "--run",
        type=str,
        help="The name of the RuntimeAPI static method to run (e.g., run_upload, run_job_sync, etc.)",
    )
    parser.add_argument(
        "--show-methods", action="store_true", help="Show available RuntimeAPI methods"
    )
    parser.add_argument(
        "--program-name", type=str, help="name of the program", default=""
    )
    parser.add_argument(
        "--program-path", type=str, help="path of the program", default=""
    )
    parser.add_argument(
        "--program-id",
        type=str,
        help="id of the program, used to update the program",
        default="",
    )
    parser.add_argument(
        "--program-description",
        type=str,
        help="description, used when updating the program",
        default="",
    )
    parser.add_argument(
        "--api-token",
        type=str,
        help="API token from quafu website: https://quafu.baqis.ac.cn/",
        default=API_TOKEN,
    )

    args = parser.parse_args()

    if args.show_methods:
        print("Available runtime methods:")
        for method_name in dir(RuntimeAPI):
            if method_name.startswith("run") and callable(
                getattr(RuntimeAPI, method_name)
            ):
                print(f" - {method_name}")
    elif args.run:
        run_method = getattr(RuntimeAPI, args.run, None)
        if run_method and callable(run_method):
            run_method(args)
        else:
            print(f"Invalid run method: {args.run}")
    else:
        print(
            "No run method provided. Use --run argument to specify the method to run."
        )


if __name__ == "__main__":
    main()
