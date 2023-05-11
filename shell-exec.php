<?php

$user_input = $_GET['input'];
// Check whether the string has rm 
if (strpos($user_input, "rm") !== false ) {
    echo "You are not allowed to use rm";
    exit;
}
shell_exec("echo $user_input");
// lol%3B%20touch%20file.txt