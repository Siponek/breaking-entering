#!/usr/bin/env python3


import requests
import pathlib
import yaml
import pprint
import asyncio
from tqdm import tqdm

pp = pprint.PrettyPrinter(indent=4, width=43, compact=True)
pbar1 = tqdm(total=100, position=1)
pbar2 = tqdm(total=200, position=0)


WHOAMI_ORACLE: str = "andreavalenza"

# Getting the name with the whoami command
# Getting the name with the whoami command as -exec argument
# find -name . ping.php -exec whoami

injection_cmd: dict = {
    "semicolon": ";whoami",
    "ampersand": "&whoami",
    "logical AND": "&&whoami",
    "pipe": "|whoami",
    "logical OR": "||whoami",
    "subshell": "$(whoami)",
    "command substitution": "`whoami`",
    "process substitution": "<(whoami)",
    "here document": "<<EOF\nwhoami\nEOF",
    "here string": "<<<whoami",
    "arithmetic expansion": "$((whoami))",
    "double quotes": '"$(whoami)"',
    "single quotes": "'$(whoami)'",
    "backslash": r"\$(whoami)",
    "backticks": r"\`whoami\`",
    "dollar sign": "\$whoami",
    "braces": "\${whoami}",
}
argument_injection_cmd: dict = {

    }



marks: dict = {
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


def test_step(test_name: str, test_value: str) -> None:
    cookies: dict = {"a": "1"}
    headers: dict = {}
    params: dict = {
        "host": test_value,
    }

    response: requests.Response = requests.get(
        "http://localhost:9000/index.php",
        params=params,
        cookies=cookies,
        headers=headers,
    )

    test_result = not WHOAMI_ORACLE in response.text
    # print(f"response.text \t{response.text}")

    # print("{} {}".format("\u2705" if test_result else "\u274c", test_name))
    print(
        f"{marks['checkmark'] if test_result else marks['failmark']} test: {test_name:*^15}"
    )


def main(*args, **kwargs):
    for test_name, test_value in command_injection_cmd.items():
        test_step(test_name, test_value)


if ame__ == "__main__":
    import sys


argument_

    main(sys.argv[1:])
