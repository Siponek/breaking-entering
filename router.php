<?php
// Define a constant for the project root directory
define('ROOT_DIR', __DIR__);

// Define a constant for the get_smoked directory
define('GET_SMOKED_DIR', '/get_smoked');

// Define the directory to serve files from
define('SERVE_DIR', ROOT_DIR );

// Get the requested URL
$url = $_SERVER['REQUEST_URI'];

// Strip the GET_SMOKED_DIR from the URL
$url = str_replace(GET_SMOKED_DIR, '', $url);

// Determine the file path to serve
$file_path = SERVE_DIR . '/' . ltrim($url, '/');

// Check if the file exists
if (is_file($file_path) && file_exists($file_path)) {
    // If this is a PHP script run it
    if (pathinfo($file_path, PATHINFO_EXTENSION) == 'php') {
        // Run the PHP script
        require_once($file_path);
        exit;
    }
    else
    {
        // Serve the static file
        header('Content-Type: ' . mime_content_type($file_path));
        readfile($file_path);
        exit;
    }
}
else {
    // Serve the 404 page
    header('HTTP/1.0 404 Not Found');
    echo '404 Not Found';
}
?>