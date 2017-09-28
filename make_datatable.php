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

$excludes = [
	'array30_OkidoKey-big_0.75.cin',
	'array30.cin',
	'klingon.cin',
	'bpmf_punctuation.cin',
	'esperanto.cin',
	'kk.cin',
	'kks.cin',
	'morse.cin',
];

$filenames = glob('./DataTables/*.cin', GLOB_NOSORT);
natsort($filenames);

$result = array(
	'version' => date("YmdHis"),
	'datatables' => [],
);

$items = [];

function stripComments($string) {
	$pattern = '/(.*)(#.*)/';
	$replacement = '\1';
	return trim(preg_replace($pattern, $replacement, $string));
}

foreach ($filenames as $path) {
	$filename = str_replace('./DataTables/', '', $path);
	if (in_array($filename, $excludes)) {
		echo "Exclude: {$filename}\n";
		continue;
	}

	$beginKeyname = false;
	$keyname = '';
	$item = array('ename' => '', 'cname' => '', 'name' => '', 'link' => $link . $filename, 'license' => '');
	$contents = explode("\n", file_get_contents($path), 1000);

	foreach ($contents as $line) {
		$line = trim($line);
		$rows = explode(' ', str_replace("\t", " ", $line), 2);
		$key = trim($rows[0]);
		$value = stripComments($rows[1]);

		if ($key == '%chardef') {
			break;
		}
		else if (in_array($key, ['%ename', '%cname', '%name', '%tcname', '%scname'])) {
			$key = str_replace('%', '', $key);
			$item[$key] = $value;
		}
		else if ($key == '%keyname') {
			if ($value == 'begin') {
				$beginKeyname = true;
				continue;
			}
			else if ($value == 'end') {
				$beginKeyname = false;
				break;
			}
		}
		else {
			if ($beginKeyname) {
				$keyname .= trim($rows[0]);
			}
			else if (strpos($line, '%') === 0) {
				// echo "ignore: ". $line . "\n";
				continue;
			}
			else {
				$line = str_replace(['#', '　'], '', $line);
				$line = trim($line);
				$item['license'] .= $line . "\n";
			}
		}
	}

	if (!empty($keyname)) {
		$result['datatables'][] = $item;
		echo "Add: {$filename} -> {$item['ename']} {$item['cname']}\n";
	}
	else {
		echo "Ignore: {$filename}\n";
	}
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($result));
fclose($f);
echo "\nExported {$destinationPath} version: {$result['version']}\n";
