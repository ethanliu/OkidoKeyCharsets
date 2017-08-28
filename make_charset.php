<?php
/**
 * Charsets.json builder
 *
 * @author Ethan Liu <***REMOVED***>
 * @copyright Creativecrap.com, 15 February, 2015
 */

error_reporting(0);
ini_set("error_reporting", FALSE);

$destinationPath = "./KeyboardLayouts.json";

$charsetPaths = glob('./Charsets/*.charset.json', GLOB_NOSORT);
$uniqueNames = array();
$contents = array(
    'version' => date("YmdHis"),
    'charsets' => array(),
);

foreach ($charsetPaths as $path) {
    $charsets = json_decode(file_get_contents($path));
    foreach ($charsets as $charset) {
        if ($charset && $charset->name && $charset->charsets) {
            if (!in_array($charset->name, $uniqueNames)) {
                echo "Adding {$path} [{$charset->name}]\n";
                $contents['charsets'][] = $charset;
                $uniqueNames[] = $charset->name;
            }
            else {
                echo "Skipped, charset already exists. {$path} [{$charset->name}]\n";
            }
        }
        else {
            echo "Skipped, invalid json or charset structure: {$path}\n";
        }
    }
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($contents));
fclose($f);
echo "\nExported {$destinationPath} version: {$contents['version']}\n";

