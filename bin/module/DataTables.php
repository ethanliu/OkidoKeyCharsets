<?php
echo "Generate DataTables.json\n\n";

$destinationPath = self::$baseDir . "DataTables.json";
$filenames = glob(self::$baseDir . 'table/*.cin', GLOB_NOSORT);
natsort($filenames);

$result = array(
	'version' => date("YmdHis"),
	'datatables' => [],
);

$items = [];

foreach ($filenames as $path) {
	$filename = basename($path);
	if (in_array($filename, self::$excludeDatables)) {
		echo "Exclude: {$filename}\n";
		continue;
	}

	$beginKeyname = false;
	$keyname = '';
	$item = array(
		'ename' => '',
		'cname' => '',
		'name' => '',
		'cin' => "table/{$filename}",
		'db' => "db/{$filename}.db",
		'license' => '',
	);
	$contents = explode("\n", file_get_contents($path), 5000);

	foreach ($contents as $line) {
		$line = trim($line);
		$rows = explode(' ', str_replace("\t", " ", $line), 2);
		$key = trim($rows[0]);
		$value = count($rows) > 1 ? self::stripComments($rows[1]) : '';

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
fwrite($f, json_encode($result, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
fclose($f);
echo "...version: {$result['version']}\n\n";
