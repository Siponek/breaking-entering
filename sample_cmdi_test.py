#!/usr/bin/env python3
# Python version 3.11.0

import requests
import pathlib
import yaml
import pprint
import asyncio
from typing import Self
from tqdm import tqdm

pp = pprint.PrettyPrinter(indent=4, width=43, compact=True)
# pbar1 = tqdm(total=100, position=1)
# pbar2 = tqdm(total=200, position=0)
# Open taml file
WHOAMI_ORACLE: str
QUERY_PARAMS: list
with open("config.yaml", "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)
    WHOAMI_ORACLE = cfg["user_name"]
    QUERY_PARAMS = cfg["query_params"]
# Getting the name with the whoami command
# Getting the name with the whoami command as -exec argument
# find -name . ping.php -exec whoami

COMMAND_INJECTION_CMD: dict = {
    "semicolon": r";whoami",
    "ampersand": r"&whoami",
    "logical AND": r"&&whoami",
    "pipe": r"|whoami",
    "logical OR": r"||whoami",
    "newline": r"0x0awhoami",
    "subshell": r"$(whoami)",
    "command substitution": r"`whoami`",
    "process substitution": r"<(whoami)",
    "here document": r"<<EOF\nwhoami\nEOF",
    "here string": r"<<<whoami",
    "arithmetic expansion": r"$((whoami))",
    "double quotes": r'"$(whoami)"',
    "single quotes": r"'$(whoami)'",
    "backslash": r"\$(whoami)",
    "backticks": r"\`whoami\`",
    "dollar sign": r"\$whoami",
    "braces": r"\${whoami}",
    "double braces": r"\$\{whoami\}",
    "double dollar sign": r"$$whoami",
    "double backslash": r"\\$(whoami)",
    "double backticks": r"\`\`whoami\`\`",
    "double dollar sign": r"\$\$whoami",
    "double braces": r"\$\$\{whoami\}",
    "double backslash": r"\\\\$(whoami)",
    "double backticks": r"\\\`\`whoami\`\`",
    # echo "Welcome $name!";
    "quote system injection 1": r'\"system("whoami");',
    "quote system injection 2": r'\'system("whoami");\'',
    "quote system injection 3": r'\"system("whoami");\"',
    "quote shell_exec injection 1": r'\"shell_exec("whoami");',
    "quote shell_exec injection 2": r'\'shell_exec("whoami");\'',
    "quote shell_exec injection 3": r'\"shell_exec("whoami");\"',
    "quote php code injection": r'\"${system("whoami")};\"',
}

ARGUMENT_INJECTION_CMD: dict = {
    # This could be tested with ls cmd and then with cat cmd
    # "webshell" : """; echo "<?php system(\$_GET['cmd']);" > webshell.php""",
    "exec_semicolon": " -exec whoami;",
    "exec": " -exec whoami",
}
BLIND_COMMAND_INJECTION_CMD: dict = {
    "blind_command_injection": " ping.php -c 1 -w 1;whoami",
}

XSS_CMD: dict = {
    # Bonus
    # The best case I can think of to test this is to get the cookie value or pass the validation
    "create_xss_text": f'<script> document.body.appendChild(document.createTextNode("{WHOAMI_ORACLE}"));</script>',
}

MARKS: dict = {
    "checkmark": "\u2705",
    "failmark": "\u274c",
}

list_of_routes_in_folder: list = [
    str(path)
    for path in pathlib.Path().iterdir()
    if path.is_file()
    and path.suffix == ".php"
    and path.name not in ["index.php", "router.php"]
]
pp.pprint(list_of_routes_in_folder)


class report:
    def __init__(self) -> None:
        self.test_report = {}
        self.all_tests_length = (
            len(COMMAND_INJECTION_CMD)
            + len(ARGUMENT_INJECTION_CMD)
            + len(BLIND_COMMAND_INJECTION_CMD)
            + len(XSS_CMD)
        )

    def append_to_report(
        self, route: str, test_name: str, test_result: bool
    ) -> Self:
        if route not in self.test_report:
            self.test_report[route] = {}
        self.test_report[route][test_name] = test_result
        return self

    def calcualte_passed_tests(self, route: str) -> Self:
        for route in self.test_report:
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
            for test_name, test_value in test_dict.items():
                print(f"Testing: \033[1m{test_name:*^15}\033[0m")
                # for route in list_of_routes_in_folder:
                complete_route: str = f"http://localhost:9000/{route}"
                test_result = test_step(
                    test_name=test_name,
                    test_value=test_value,
                    url_for_request=complete_route,
                )
                self.append_to_report(
                    route=route, test_name=test_name, test_result=test_result
                )
        return self


def test_step(test_name: str, test_value: str, url_for_request: str) -> bool:
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
    test_result: bool = not WHOAMI_ORACLE in response.text
    return test_result
    # pp.pprint(response.text)
    # report(route=url_for_request, test_name=test_name, test_result=test_result).
    # print(
    #     f"{MARKS['checkmark'] if test_result else MARKS['failmark']} test: {test_name:*^15}"
    # )


# def test_suite(array_of_dicts: list, report_object, route) -> dict:
#     for test_dict in array_of_dicts:
#         for test_name, test_value in test_dict.items():
#             print(f"Testing: \033[1m{test_name:*^15}\033[0m")
#             # for route in list_of_routes_in_folder:
#             complete_route: str = f"http://localhost:9000/{route}"
#             test_result = test_step(
#                 test_name=test_name,
#                 test_value=test_value,
#                 url_for_request=complete_route,
#             )
#             report_object.append_to_report(route=route, test_name=test_name, test_result=test_result)
#     return report_object


def main(*args, **kwargs):
    current_route_test_report = report()
    for testing_route in list_of_routes_in_folder:
        print(f"Testing route: \033[1m{testing_route:*^15}\033[0m")
        complete_route: str = f"http://localhost:9000/{testing_route}"
        array_of_tests: list = [
            COMMAND_INJECTION_CMD,
            ARGUMENT_INJECTION_CMD,
            BLIND_COMMAND_INJECTION_CMD,
            XSS_CMD,
        ]
        current_route_test_report.test_suite(
            array_of_dicts=array_of_tests, route=testing_route
        ).calcualte_passed_tests(
            route=testing_route
        ).calculate_total_tests().calculate_passed_tests_percentage()

    pp.pprint(current_route_test_report.test_report)
    # current_route_test_report.calcualte_passed_tests(route=testing_route)
    # current_route_test_report.calculate_total_tests()
    # # for cmd_injection_test_name, test_value in COMMAND_INJECTION_CMD.items():
    # #     test_result = test_step(
    # #         test_name=cmd_injection_test_name,
    # #         test_value=test_value,
    # #         url_for_request=complete_route,
    # #     )
    # #     current_route_test_report.append_to_report(route=testing_route, test_name=cmd_injection_test_name, test_result=test_result)
    # # for arg_injection_test_name in ARGUMENT_INJECTION_CMD:
    # #     test_result = test_step(
    # #         test_name=arg_injection_test_name,
    # #         test_value=ARGUMENT_INJECTION_CMD[arg_injection_test_name],
    # #         url_for_request=complete_route,
    # #     )
    # #     current_route_test_report.append_to_report(route=testing_route, test_name=arg_injection_test_name, test_result=test_result)
    # # for blind_cmd_injection_test_name in BLIND_COMMAND_INJECTION_CMD:
    #     test_result = test_step(
    #         test_name=blind_cmd_injection_test_name,
    #         test_value=BLIND_COMMAND_INJECTION_CMD[blind_cmd_injection_test_name],
    #         url_for_request=complete_route,
    #     )
    #     current_route_test_report.append_to_report(route=testing_route, test_name=blind_cmd_injection_test_name, test_result=test_result)


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
