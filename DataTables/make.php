<?php
/**
 * DataTables.json builder
 *
 * @author Ethan Liu <***REMOVED***>
 * @copyright Creativecrap.com, 10 July, 2015
 */

error_reporting(0);
ini_set("error_reporting", FALSE);

$link = 'https://raw.githubusercontent.com/ethanliu/OkidoKeyCharsets/master/DataTables/';
$destinationPath = "./DataTables.json";

$filenames = glob('*.cin', GLOB_NOSORT);
$result = array(
    'version' => date("YmdHis"),
    'datatables' => [],
);

$items = [];

foreach ($filenames as $filename) {
    // if (strpos($filename, 'lookup') !== false) {
    //     continue;
    // }

    $checkComments = true;
    $beginKeyname = false;
    $keyname = '';
    $item = array('ename' => '', 'cname' => '', 'name' => '', 'link' => $link . $filename, 'license' => '');
    $contents = explode("\n", file_get_contents($filename), 100);

    foreach ($contents as $line) {
        $line = trim($line);

        if ($checkComments && strpos($line, '#') === 0) {
            // echo $line . "\n";
            $item['license'] .= $line . "\n";
            continue;
        }

        $rows = explode(' ', str_replace("\t", " ", $line), 2);
        $rows[0] = trim($rows[0]);
        $rows[1] = trim($rows[1]);
        switch ($rows[0]) {
            case '%ename':
            case '%cname':
            case '%name':
                $checkComments = false;
                $key = str_replace('%', '', $rows[0]);
                $item[$key] = trim($rows[1]);
                break;

            case '%chardef':
                break;
            case '%keyname':
                $checkComments = false;
                if ($rows[1] == 'begin') {
                    $beginKeyname = true;
                    continue;
                }
                else if ($rows[1] == 'end') {
                    $beginKeyname = false;
                    continue;
                }
                continue;

            default:
                if ($beginKeyname) {
                    $keyname .= trim($rows[0]);
                }
                break;
        }

    }

    if (!empty($keyname)) {
        $result['datatables'][] = $item;
        echo "Adding {$filename} -> {$item['ename']} {$item['cname']}\n";
    }
    else {
        echo "Skipping {$filename} -> {$item['ename']} {$item['cname']}\n";
    }
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($result));
fclose($f);
echo "\nExported {$destinationPath} version: {$result['version']}\n";
