<?php
/**
 * tongwen - create ChineseVariant.db from tongwen dictionaries
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 21 April, 2021
 * @package module
 */

function loadDictionary($mode, $category, $root) {
	$filename = "{$mode}-{$category}.json";
	$path = $root . "/" . $filename;
	if (file_exists($path)) {
		$data = json_decode(file_get_contents($path), true);
		if ($data) {
			return $data;
			// return array_keys($data);
		}
	}
	return [];
}





// create database

$output = $argv[0] ?? "ChineseVariant.db";
@unlink($output);

$db = new Database($output);
$db->exec("PRAGMA synchronous = OFF");
$db->exec("PRAGMA journal_mode = MEMORY");

$db->exec("CREATE TABLE char_hans (`hans` CHAR(255) UNIQUE NOT NULL, `hant` CHAR(255) default '')");
$db->exec("CREATE TABLE char_hant (`hant` CHAR(255) UNIQUE NOT NULL, `hans` CHAR(255) default '')");
$db->exec("CREATE TABLE phrase_hans (`hans` CHAR(255) UNIQUE NOT NULL, `hant` CHAR(255) default '')");
$db->exec("CREATE TABLE phrase_hant (`hant` CHAR(255) UNIQUE NOT NULL, `hans` CHAR(255) default '')");

// $categories = ["char", "phrase"];
$categories = ["char"];

foreach ($categories as $category) {
	foreach (["s2t", "t2s"] as $mode) {
		$data = loadDictionary($mode, $category, $srcPath);
		if (empty($data)) {
			continue;
		}

		$tableName = "{$category}_" . (($mode == "s2t") ? "hans" : "hant");

		foreach ($data as $key => $value) {
			// var_dump("{$key} => {$value}\n");
			$db->exec("INSERT INTO `{$tableName}` VALUES(:k, :v);", [":k" => $key, ":v" => $value]);
		}

	}
}

$db->exec('vacuum;');
$db->close();

