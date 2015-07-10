<?php
/**
 *
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

    $item = array('ename' => '', 'cname' => '', 'name' => '', 'link' => $link . $filename, 'license' => '');
    $checkComments = true;
    $contents = explode("\n", file_get_contents($filename), 100);

    foreach ($contents as $line) {
        $line = trim($line);

        if ($checkComments && strpos($line, '#') === 0) {
            // echo $line . "\n";
            $item['license'] .= $line . "\n";
            continue;
        }

        $rows = explode(' ', str_replace("\t", " ", $line), 2);
        switch ($rows[0]) {
            case '%ename':
            case '%cname':
            case '%name':
                $checkComments = false;
                $key = str_replace('%', '', $rows[0]);
                $item[$key] = trim($rows[1]);
                break;

            case '%chardef':
            case '%keyname':
                $checkComments = false;
                continue;

            default:
                break;
        }

    }

    $result['datatables'][] = $item;
    echo "Adding {$filename} -> {$item['ename']} {$item['cname']}\n";
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($result));
fclose($f);
echo "\nExported {$destinationPath} verions: {$result['version']}\n";
//

// $data = [];
//
// foreach (glob('OkidoKeyCharsets/DataTables/*.cin') as $path) {
// 	$filename = str_replace('OkidoKeyCharsets/DataTables/', '', $path);
// 	$contents = explode("\n", file_get_contents($path), 100);
// 	foreach ($contents as $line) {
// 		$line = trim($line);
// 		$rows = explode(' ', $line, 2);
// 		if ($rows[0] == '%ename' || $rows[0] == '%cname' || $rows[0] == '%name') {
// 			$data[$filename] .= trim($rows[1]) . ' ';
// 		}
// 		else if ($rows[0] == '%chardef' || $rows[0] == '%keyname') {
// 			break;
// 		}
// 	}
// }
//
// $data = array_flip($data);
// print_r($data);
//
