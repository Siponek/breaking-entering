<?php

$host = $_GET['host'];

shell_exec("ping -c 3 $host");
