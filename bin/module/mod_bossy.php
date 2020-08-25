<?php
/**
 * bossy - merge _t, _j tables from boshiamy
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 24 August, 2020
 * @package module
 */

function endsWith($string, $endString) {
	$len = strlen($endString);
	if ($len == 0) {
		return true;
	}
	return (substr($string, -$len) === $endString);
}

if (endsWith($srcPath, "_t.cin")) {
	$srcPath2 = str_replace("_t.cin", "_j.cin", $srcPath);
}
else if (endsWith($srcPath, "_j.cin")) {
	$srcPath2 = $srcPath;
	$srcPath = str_replace("_j.cin", "_t.cin", $srcPath2);
}

if (empty($srcPath2) || empty($srcPath2)) {
	die("Second cin table not found.\n");
}

$table1 = new TableReader($srcPath, false);
$table2 = new TableReader($srcPath2, false);

$values1 = [];
$values2 = [];

foreach ($table1->data as $item) {
	$values1[] = $item->value;
}

foreach ($table2->data as $index => $item) {
	if (in_array($item->value, $values1)) {
		// echo "{$index}: {$item->key} -> {$item->value}\n";
		continue;
	}

	// echo "{$index}: {$item->key} -> {$item->value}\n";
	$values2[] = $item;
}

if (empty($values2)) {
	die("No new items\n");
}

$contents = file_get_contents($srcPath);
$contents = str_replace("%ename boshiamy-t", "%ename bossy", $contents);
$contents = str_replace("%cname 嘸蝦米-繁", "%cname 謥蝦米", $contents);
$contents = str_replace("%chardef end", "# _j section\n", $contents);

foreach ($values2 as $item) {
	$contents .= "{$item->key}\t{$item->value}\n";
}
$contents .= "%chardef end";

echo $contents;
