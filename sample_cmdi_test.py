#!/usr/bin/env python3
# Python version 3.11.0

import requests
import pathlib
import yaml
import pprint
import asyncio
from typing import Self
from tqdm import tqdm
from collections import ChainMap
import random
import colorama
from colorama import Fore, Back, Style

colorama.init()
pp = pprint.PrettyPrinter(indent=4, width=43, compact=True)

WHOAMI_ORACLE: str
QUERY_PARAMS: list
COMMAND_INJECTION_CMD: dict
ARGUMENT_INJECTION_CMD: dict
BLIND_COMMAND_INJECTION_CMD: dict
XSS_CMD: dict
list_of_routes_in_folder: list
MARKS: dict = {
    "checkmark": "\u2705",
    "failmark": "\u274c",
}


with open("config.yaml", "r") as ymlfile:
    attack_config: dict = yaml.load(ymlfile, Loader=yaml.CLoader)
    # Get the variable values
    user_name: str = attack_config["variables"]["user_name"]
    folder_to_watch: str = attack_config["variables"]["folder_to_watch"]
    query_params: list = attack_config["variables"]["query_params"]
    command: str = attack_config["variables"]["command"]
    replaced_config: dict = {}
    print(attack_config)
    for attack_type in attack_config.keys():
        print(Fore.CYAN + attack_type + Fore.RESET)
        if attack_type == "variables":
            continue
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
            print(attack_key)
            print(attack_value)
    print(Fore.CYAN, attack_config, Fore.RESET)
    WHOAMI_ORACLE = attack_config["variables"]["user_name"]
    COMMAND_INJECTION_CMD = attack_config["command_injection"]
    ARGUMENT_INJECTION_CMD = attack_config["argument_injection"]
    BLIND_COMMAND_INJECTION_CMD = attack_config["blind_command_injection"]
    XSS_CMD = attack_config["xss"]
    # pp.pprint(ARGUMENT_INJECTION_CMD)


class report:
    """Class for generating a report of the tests performed"""

    def __init__(self) -> None:
        self.test_report = {}
        self.all_tests_length = (
            len(COMMAND_INJECTION_CMD)
            + len(ARGUMENT_INJECTION_CMD)
            + len(BLIND_COMMAND_INJECTION_CMD)
            + len(XSS_CMD)
        )
        self.secondary_position = 1

    def append_to_report(
        self, route: str, test_name: str, test_result: bool
    ) -> Self:
        if route not in self.test_report:
            self.test_report[route] = {}
        self.test_report[route][test_name] = test_result
        return self

    def calcualte_passed_tests(self, route: str) -> Self:
        for route in self.test_report:
            self.test_report[route]["passed_tests"] = 0
            for test in self.test_report[route]:
                if self.test_report[route][test]:
                    self.test_report[route]["passed_tests"] += 1
        return self

    def calculate_total_tests(self) -> Self:
        for route in self.test_report:
            self.test_report[route]["total_tests"] = len(
                self.test_report[route]
            )
        return self

    def calculate_passed_tests_percentage(self) -> Self:
        for route in self.test_report:
            self.test_report[route]["passed_tests_percentage"] = round(
                self.test_report[route]["passed_tests"]
                / self.test_report[route]["total_tests"]
                * 100
            )
        return self

    def test_suite(self, array_of_dicts: list, route) -> Self:
        for test_dict in array_of_dicts:
            with tqdm(
                total=len(test_dict),
                position=self.secondary_position,
                colour="CYAN",
                leave=False,
            ) as pbar2:
                for test_name, test_value in test_dict.items():
                    pbar2.set_description(
                        f"Testing: \033[1m{test_name}\033[0m"
                    )
                    complete_route: str = f"http://localhost:9000/{route}"
                    test_result = test_step(
                        test_name=test_name,
                        test_value=test_value,
                        url_for_request=complete_route,
                    )
                    self.append_to_report(
                        route=route,
                        test_name=test_name,
                        test_result=test_result,
                    )
                    pbar2.update(1)
            pbar2.close()
            # self.secondary_position += 1
        return self


def test_step(test_name: str, test_value: str, url_for_request: str) -> bool:
    """Function for testing a single test case"""
    return random.choice([True, False])
    cookies: dict = {"a": "1"}
    headers: dict = {}
    params: dict = {x: test_value for x in QUERY_PARAMS}
    response: requests.Response = requests.Response()
    try:
        response = requests.get(
            url=url_for_request,
            params=params,
            cookies=cookies,
            headers=headers,
        )
    except requests.exceptions.ConnectionError:
        print("Connection error. Check if the server is running.")
        exit()
    return not WHOAMI_ORACLE in response.text


def main(*args, **kwargs):
    """Main function for running the tests"""
    current_route_test_report = report()
    array_of_tests: list = [
        COMMAND_INJECTION_CMD,
        ARGUMENT_INJECTION_CMD,
        BLIND_COMMAND_INJECTION_CMD,
        XSS_CMD,
    ]
    list_of_routes_in_folder = [
        str(path)
        for path in pathlib.Path().iterdir()
        if path.is_file()
        and path.suffix == ".php"
        and path.name not in ["index.php", "router.php"]
    ]
    pp.pprint(list_of_routes_in_folder)

    tmp_dict = dict(ChainMap(*array_of_tests))
    # TODO make this async for every route
    with tqdm(total=len(list_of_routes_in_folder), position=0) as pbar1:
        for testing_route in list_of_routes_in_folder:
            pbar1.set_description(
                f"Testing route: \033[1m{testing_route}\033[0m"
            )
            pbar1.update(1)
            complete_route: str = f"http://localhost:9000/{testing_route}"
            current_route_test_report.test_suite(
                array_of_dicts=array_of_tests, route=complete_route
            ).calcualte_passed_tests(
                route=testing_route
            ).calculate_total_tests().calculate_passed_tests_percentage()
        pbar1.close()
    for route, values in current_route_test_report.test_report.items():
        print(
            f"\033[1m{route}\033[0m",
            # f"{MARKS['checkmark']} Passed {values['passed_tests']} out of {values['total_tests']}",
        )
        pbar_test = tqdm(
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
    result: float = 0
    print(f"Overall suite result:")
    for route, values in current_route_test_report.test_report.items():
        result += values["passed_tests"]
    print(
        f"{MARKS['checkmark']} Passed {result} out of {current_route_test_report.all_tests_length*len(list_of_routes_in_folder)}"
    )


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
