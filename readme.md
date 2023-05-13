# Shell pentesting PHP web app

[python]: https://www.python.org/downloads/
[php]: https://www.php.net/downloads.php
[make]: https://www.gnu.org/software/make/
[chocolatey]: https://chocolatey.org/install

```ascii
--   ______   ______     __   __     ______   __   __     ______     ______     ______     ______   __     ______     __   __        __    __     ______     __   __    
--  /\  == \ /\  ___\   /\ "-.\ \   /\__  _\ /\ "-.\ \   /\  ___\   /\  == \   /\  __ \   /\__  _\ /\ \   /\  __ \   /\ "-.\ \      /\ "-./  \   /\  __ \   /\ "-.\ \   
--  \ \  _-/ \ \  __\   \ \ \-.  \  \/_/\ \/ \ \ \-.  \  \ \  __\   \ \  __<   \ \  __ \  \/_/\ \/ \ \ \  \ \ \/\ \  \ \ \-.  \     \ \ \-./\ \  \ \  __ \  \ \ \-.  \  
--   \ \_\    \ \_____\  \ \_\\"\_\    \ \_\  \ \_\\"\_\  \ \_____\  \ \_\ \_\  \ \_\ \_\    \ \_\  \ \_\  \ \_____\  \ \_\\"\_\     \ \_\ \ \_\  \ \_\ \_\  \ \_\\"\_\ 
--    \/_/     \/_____/   \/_/ \/_/     \/_/   \/_/ \/_/   \/_____/   \/_/ /_/   \/_/\/_/     \/_/   \/_/   \/_____/   \/_/ \/_/      \/_/  \/_/   \/_/\/_/   \/_/ \/_/ 
--                                                                                                                                                                      
```

## Description

This is a Python script with . PHP web pages that can be used to test shell commands. It is intended to be used for common pentesting cases.

For now it only has tests consisting of a:

- Command injection
- Argument injection
- Blind command incjection
- Xss

## Requirements

- [PHP][php] 7.2 or higher
- [Python][python] 3.11 or higher (Should work on 3.8, but you need to install the required packages manually)
- Python libaries that can be installed with pip:

    ```bash
    pip install -r requirements.txt
    ```

- If on windows:
  - Use [Chocolatey][chocolatey] to install [Make][make] (To be implemented)

## Running the tests

Run the following command to start the server:

```bash
php -S localhost:9000
```

Run the following command to start the tests:

```bash
python ./sample_cmdi_test.py
```

---

```bash
config.yaml
```

This is a YAML configuration file that allows users to specify attack payloads for various attack types such as command injection, argument injection, and blind command injection. The file consists of key-value pairs that define variables and attack payloads. The syntax is YAML, which uses indentation and a consistent set of delimiters to define the structure of the file.

## Configuring the Config File

The following is a guide for configuring this YAML configuration file:

## Variables

The variables section contains variables that are used throughout the configuration file. The variables that can be modified include:

```yaml
    user_name: A string that represents the test string to look for in response text.
    command: The name of the command to receive user_name.
    # To be implemented, e.g. cat /etc/passwd
    folder_to_watch: The folder to watch.
    query_params: A map that contains query parameters for various attack types. The parameters that can be modified include:
    # Keep in mind that Python script will use the first substring that matches the key of the page that is being tested. E.g. ping-escapeshellcmd has both "ping" and "shell" substirngs, but ping comes first, so it will be used.
        ping: The host parameter.
        find: The input parameter.
        echo: The name parameter.
        exec: The input parameter.
    base_url: The base URL of the target website.
```

To modify a variable, simply change the value associated with the key.

## Command Injection

The command_injection section contains attack payloads for command injection. The available attack vectors are **exec** and **ping**.

## Argument Injection

The argument_injection section contains attack payloads for argument injection. The available attack vectors are **find** and **ping**.

## Blind Command Injection

The blind_command_injection section contains attack payloads for blind command injection like webshell creation. The available attack vectors are **find** and **ping**.

## Cross-Site Scripting

There is also a xss section that contains attack payloads for cross-site scripting. The available attack vectors are **echo** and **exec**. The problem is that these are diffucult to test, because the response is not visible to the user. The only way to test it is to use a proxy like **Burp Suite** or just seeing if the XSS is possible via insterting the **oracle** name in script incjection.

## Example Usage

An example usage of this configuration file is to specify the attack payloads for command injection, argument injection, and blind command injection attacks. Once the configuration file is modified with the desired attack payloads, it can be used to test the target website. To use the configuration file, it needs to be loaded into a script that executes the attack payloads on the target website.

By default the script called sample_cmdi_test.py will get config.yaml file from current folder. To run the script with specified config path, simply run the following command:

```bash
python ./sample_cmdi_test.py --config your_config_name.yaml
```

You can also specify to use --verbose flag to see more details about the test.

```bash
python ./sample_cmdi_test.py --verbose
```

![alt text](./Example%20of%20an%20result.jpg "Example of an result")

## Conclusion

This YAML configuration file provides users with an easy and flexible way to specify attack payloads for various attack types. By modifying the values associated with the keys, users can quickly configure the attack payloads to suit their needs.

## Disclaimer

Keep in mind that the default tests are not perfect and may not work on all websites. It is recommended to modify the tests to suit your needs.

For example blind injection test is not working on windows because of the way the command is executed. The php development does not allow to execute php tasks in the background (I THINK).
