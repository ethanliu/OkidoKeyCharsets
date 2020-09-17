<?php
/**
 * diff - compare tables
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 27 August, 2020
 * @package module
 */


// $basePath = __DIR__ . "/../../table/bpmf-cns.cin";
$basePath = __DIR__ . "/../../table/array30.cin";

$baseTable = new TableReader($basePath, false);
$targetTable = new TableReader($srcPath, false);


function diffTable($a, $b) {
	$result = [];
	$base = [];

	foreach ($a->data as $item) {
		$base[$item->value][] = $item->key;
	}
	ksort($base);

	foreach ($b->data as $item) {
		if (!isset($base[$item->value])) {
			// echo "{$item->value}: {$base[$item->value][0]}\n";
			$result[] = $item;
		}
	}

	return $result;
}

// $result = diffTable($baseTable, $targetTable);
// var_dump($result);

$result = diffTable($targetTable, $baseTable);
// var_dump($result);
foreach ($result as $item) {
	echo "{$item->value}\n";
}



