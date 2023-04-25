<?php
// Check wheter this is an AJAX request
if (!isset($_SERVER['HTTP_X_REQUESTED_WITH']) && strtolower($_SERVER['HTTP_X_REQUESTED_WITH']) != 'xmlhttprequest') {
    die('NO HAX PLZ');
}
$host = $_GET['host'];

system("ping -c 3 $host");
