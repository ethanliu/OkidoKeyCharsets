<?php
/**
 * bossy - merge boshiamy tables
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 24 August, 2020
 * @package module
 */

// function endsWith($string, $endString) {
// 	$len = strlen($endString);
// 	if ($len == 0) {
// 		return true;
// 	}
// 	return (substr($string, -$len) === $endString);
// }
//
// if (endsWith($srcPath, "_t.cin")) {
// 	$srcPath2 = str_replace("_t.cin", "_j.cin", $srcPath);
// }
// else if (endsWith($srcPath, "_j.cin")) {
// 	$srcPath2 = $srcPath;
// 	$srcPath = str_replace("_j.cin", "_t.cin", $srcPath2);
// }
//
// if (empty($srcPath2) || empty($srcPath2)) {
// 	die("Second cin table not found.\n");
// }

$base = new TableReader($srcPath, false);
$cache = [];
$data = [];

foreach ($base->data as $item) {
	$values1[] = $item->value;
	$key = $item->value . '_' . $item->key;
	$cache[] = $key;
}

foreach ($argv as $tablePath) {
	if (empty($tablePath) || !file_exists($tablePath)) {
		continue;
	}

	$name = basename($tablePath);
	$table = new TableReader($tablePath, false);

	foreach ($table->data as $index => $item) {
		$key = $item->value . '_' . $item->key;
		if (in_array($key, $cache)) {
			continue;
		}
		// append to cache
		$cache[] = $key;
		$data[$name][] = $item;
	}
}

$contents = file_get_contents($srcPath);
$contents = str_replace("%ename boshiamy-t", "%ename bossy", $contents);
$contents = str_replace("%cname 嘸蝦米-繁", "%cname 謥蝦米", $contents);
$contents = str_replace("%chardef end", "\n", $contents);

foreach ($data as $source => $items) {
	$contents .= "# {$source}\n";
	foreach ($items as $item) {
		$contents .= "{$item->key}\t{$item->value}\n";
	}
}

$contents .= "%chardef end";

echo $contents;
