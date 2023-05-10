#!/usr/bin/env python3
# Python version 3.11.0

import requests
import pathlib
import yaml
import pprint
import asyncio
import aiohttp
import random
from typing import Self
from tqdm import tqdm
from time import sleep
from collections import ChainMap
import colorama
from colorama import Fore, Back, Style

colorama.init()
pp = pprint.PrettyPrinter(indent=4, width=43, compact=True)

WHOAMI_ORACLE: str
QUERY_PARAMS: dict
COMMAND_INJECTION_CMD: dict
ARGUMENT_INJECTION_CMD: dict
BLIND_COMMAND_INJECTION_CMD: dict
XSS_CMD: dict
MARKS: dict = {
    "checkmark": "\u2705",
    "failmark": "\u274c",
}
HTTP_BASE: str = "http://localhost:9000/"


def process_config_file(config_file_path: str) -> dict:
    """Function for processing the config file

    Args:
        config_file_path (str): Path to the config file

    Returns:
        dict: Dictionary with the config file values replaced
    """
    with open(config_file_path, "r") as ymlfile:
        attack_config: dict = yaml.load(ymlfile, Loader=yaml.CLoader)
        # Get the variable values
        user_name: str = attack_config["variables"]["user_name"]
        folder_to_watch: str = attack_config["variables"]["folder_to_watch"]
        # query_params: list = attack_config["variables"]["query_params"]
        command: str = attack_config["variables"]["command"]
        replaced_config: dict = {}
        for attack_type in attack_config.keys():
            if attack_type == "variables":
                continue
            print(Fore.CYAN + f"Config processing {attack_type}" + Fore.RESET)
            replaced_config[attack_type] = {}
            for attack_key, attack_value in attack_config[attack_type].items():
                replaced_config[attack_type][attack_key] = {}
                for key in attack_value:
                    replaced_config[attack_type][attack_key][key] = (
                        attack_config[attack_type][attack_key][key]
                        .replace(r"${ variables.user_name }", user_name)
                        .replace(
                            r"${ variables.folder_to_watch }", folder_to_watch
                        )
                        .replace(r"${ variables.command }", command)
                    )
        replaced_config["variables"] = attack_config["variables"]
        return replaced_config


class TestingClass:
    """Class for generating a report of the tests performed"""

    def __init__(self) -> None:
        self.test_report: dict = {}
        self.secondary_position: int = 1
        self.test_route: list = []

    @property
    def all_tests_length(self) -> int:
        return sum(
            [
                len(dct.values())
                for dct in [
                    COMMAND_INJECTION_CMD,
                    ARGUMENT_INJECTION_CMD,
                    BLIND_COMMAND_INJECTION_CMD,
                    XSS_CMD,
                ]
            ]
        )

    def append_to_report(
        self, route: str, test_name: str, test_result: bool
    ) -> Self:
        if route not in self.test_report:
            tqdm.write(f"Appending current route path to report for: {route}")
            self.test_report[route] = {}
        self.test_report[route][test_name] = test_result
        return self

    def calcualte_passed_tests(self, route: str) -> Self:
        self.test_report[route]["passed_tests"] = 0
        for test in self.test_report[route]:
            # tqdm.write(f"test {test} {self.test_report[test]}")
            if self.test_report[route][test] and test != "passed_tests":
                self.test_report[route]["passed_tests"] += 1
        return self

    def calculate_total_tests(self) -> Self:
        for route in self.test_report:
            self.test_report[route]["total_tests"] = (
                len(self.test_report[route]) - 1
            )
        return self

    def calculate_passed_tests_percentage(self) -> Self:
        for route in self.test_report:
            self.test_report[route]["passed_tests_percentage"] = round(
                self.test_report[route]["passed_tests"]
                / self.test_report[route]["total_tests"]
                * 100
            )
        # self._reset()
        return self

    async def test_suite(
        self,
        array_of_dicts: list,
        file_route: str,
        route_type: list,
        http_adress: str = "http://localhost:9000/",
    ) -> Self:
        self.test_route = route_type
        amount_of_tests: int = 0
        for test_dict in array_of_dicts:
            if route_type[0] not in test_dict:
                continue
            amount_of_tests = sum([len(test_dict[x]) for x in test_dict])
            with tqdm(
                total=amount_of_tests,
                position=self.secondary_position,
                colour="CYAN",
                leave=False,
            ) as pbar2:
                tasks = []
                for test_type, test_value in test_dict.items():
                    if test_type != route_type[0]:
                        pbar2.update(1)
                        continue
                    for test in test_value:
                        task = asyncio.create_task(
                            self.test_step(
                                test_value=test_value[test],
                                url_for_request=http_adress + file_route,
                            )
                        )
                        task.add_done_callback(lambda fut: pbar2.update(1))
                        tasks.append((task, test_type, test))
                await asyncio.gather(*[task for task, _, _ in tasks])
                for task, test_type, test in tasks:
                    test_result = task.result()
                    self.append_to_report(
                        route=file_route,
                        test_name=test_type + " " + test,
                        test_result=test_result,
                    )
            pbar2.close()
        return self

    async def test_step(self, test_value: str, url_for_request: str) -> bool:
        """Function for testing a single test case"""
        # return random.choice([True, False])
        cookies: dict = {"a": "1"}
        headers: dict = {}
        params: dict = {self.test_route[1]: test_value}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url=url_for_request,
                    params=params,
                    cookies=cookies,
                    headers=headers,
                ) as response:
                    text = await response.text()
                    tqdm.write(
                        f"Testing {params} {Fore.MAGENTA + url_for_request.split('/')[-1] + Fore.RESET} response:\t\t{Fore.GREEN + text + Fore.RESET}"
                    )
                return not WHOAMI_ORACLE in text
            except aiohttp.ClientError:
                tqdm.write("Connection error. Check if the server is running.")
                exit()

    def _reset(self) -> Self:
        self.test_report = {}
        self.secondary_position = 1
        return self


async def define_testing_type(testing_route: str) -> list:
    if testing_route.find("echo") != -1:
        return ["echo", QUERY_PARAMS["echo"]]
    elif testing_route.find("ping") != -1:
        return ["ping", QUERY_PARAMS["ping"]]
    elif testing_route.find("find") != -1:
        return ["find", QUERY_PARAMS["find"]]
    elif testing_route.find("exec") != -1:
        return ["exec", QUERY_PARAMS["exec"]]
    raise ValueError(
        f"No testing type found for given route {Fore.RED +  testing_route + Fore.RESET}. Make sure that the page has either exec, echo, find, or ping in the name."
    )


async def update_progress_bar(pbar_test, passed_tests, total_tests):
    while True:
        pbar_test.set_description(
            f"{MARKS['checkmark']}Passed {passed_tests} out of {total_tests-1}"
        )
        pbar_test.update()
        await asyncio.sleep(0.1)


async def main(*args, **kwargs):
    """Main function for running the tests"""
    TestClass: TestingClass = TestingClass()
    array_of_tests: list = [
        COMMAND_INJECTION_CMD,
        ARGUMENT_INJECTION_CMD,
        BLIND_COMMAND_INJECTION_CMD,
        XSS_CMD,
    ]
    list_of_routes_in_folder: list = [
        str(path)
        for path in pathlib.Path().iterdir()
        if path.is_file()
        and path.suffix == ".php"
        and path.name not in ["index.php", "router.php"]
        and path.name.find("webshell") == -1
    ]
    # TODO make this async for every route
    with tqdm(total=len(list_of_routes_in_folder), position=0) as pbar1:
        tasks = []
        for testing_route in list_of_routes_in_folder:
            pbar1.set_description(
                f"Testing route: \033[1m{testing_route}\033[0m"
            )
            task = asyncio.create_task(
                TestClass.test_suite(
                    array_of_dicts=array_of_tests,
                    http_adress=HTTP_BASE,
                    file_route=testing_route,
                    route_type=await define_testing_type(testing_route),
                )
            )
            task.add_done_callback(lambda fut: pbar1.update(1))
            tasks.append((task))
            # Here the http_adress could be the base attr for the class since it is global and read from config.yaml
        await asyncio.gather(*[task for task in tasks])
        for testing_route in list_of_routes_in_folder:
            print(f"Calculating passed tests for {testing_route}")
            TestClass.calcualte_passed_tests(route=testing_route)
        TestClass.calculate_total_tests().calculate_passed_tests_percentage()
        pbar1.close()
    for route, values in TestClass.test_report.items():
        print(
            f"\033[1m{route}\033[0m",
        )
        pbar_test = tqdm(
            # passed_test is always 1 less than total_tests beacuse of the passed_tests key
            total=values["total_tests"],
            position=1,
            colour="GREEN",
            leave=True,
            initial=values["passed_tests"],
            disable=not values["passed_tests"] and not values["total_tests"],
            desc=f"{MARKS['checkmark']}Passed {values['passed_tests']} out of {values['total_tests']}",
        )
        pbar_test.close()
        print(f"\n{MARKS['failmark']} Falied tests:")
        pp.pprint([x for x in values if not values[x]])
    result: int = 0
    total_tests_ran: int = 0
    print(f"Overall suite result:")
    for route, values in TestClass.test_report.items():
        # print(
        #     f"\033[1m{route}\033[0m has {values['passed_tests']} tests passed out of {values['total_tests']}"
        # )
        result += values["passed_tests"]
        total_tests_ran += values["total_tests"]
    print(
        f"{MARKS['checkmark']} Passed {result} out of {total_tests_ran} := {round(result/total_tests_ran*100)}%"
    )


if __name__ == "__main__":
    import sys

    yaml_config = process_config_file("config.yaml")
    WHOAMI_ORACLE = yaml_config["variables"]["user_name"]
    COMMAND_INJECTION_CMD = yaml_config["command_injection"]
    ARGUMENT_INJECTION_CMD = yaml_config["argument_injection"]
    BLIND_COMMAND_INJECTION_CMD = yaml_config["blind_command_injection"]
    XSS_CMD = yaml_config["xss"]
    QUERY_PARAMS = yaml_config["variables"]["query_params"]
    HTTP_BASE = yaml_config["variables"]["base_url"]
    asyncio.run(main(sys.argv[1:]))
