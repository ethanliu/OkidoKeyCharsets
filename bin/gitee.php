<?php
/**
 * gitee build script
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 14 November, 2020
 */

$root = realpath(__DIR__ . "/../");
$home = $root . "/_repos/gitee";

function datatable() {
	global $root, $home;

	$jsonPath = $root . "/DataTables.json";
	$data = json_decode(file_get_contents($jsonPath), true);

	foreach ($data["splits"] as $path => $splits) {
		$dbPath = "db/{$path}.db";
		echo "Split {$dbPath}\n";

		@unlink("{$home}/{$dbPath}");
		$cmd = "cp \"{$root}/{$dbPath}\" \"{$home}/{$dbPath}\" ";
		exec($cmd);
		// echo $cmd . "\n";

		$cmd = __DIR__ . "/LoveMachine -s \"{$home}/{$dbPath}\" ";
		exec($cmd);

		// echo $cmd . "\n";
		@unlink("{$home}/{$dbPath}");

		// count
		$cmd = "ls {$home}/{$dbPath}* | wc -l";
		$count = intval(trim(exec($cmd))) ?? 0;

		$data["splits"][$path]["gitee"] = $count;
	}

	$data["version"] = date("YmdHis");

	$f = fopen($jsonPath, "w") or die("Unable to create file.");
	$json = json_encode($data, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT);
	fwrite($f, $json);
	fclose($f);
}


function lexicon() {
	global $root, $home;

	$jsonPath = $root . "/Lexicon.json";
	$data = json_decode(file_get_contents($jsonPath), true);

	foreach ($data["splits"] as $path => $splits) {
		$dbPath = "db/{$path}";
		echo "Split {$dbPath}\n";

		@unlink("{$home}/{$dbPath}");
		$cmd = "cp \"{$root}/{$dbPath}\" \"{$home}/{$dbPath}\" ";
		exec($cmd);

		$cmd = __DIR__ . "/LoveMachine -s \"{$home}/{$dbPath}\" ";
		exec($cmd);

		// echo $cmd . "\n";
		@unlink("{$home}/{$dbPath}");

		// count
		$cmd = "ls {$home}/{$dbPath}* | wc -l";
		$count = intval(trim(exec($cmd))) ?? 0;

		$data["splits"][$path]["gitee"] = $count;
	}

	$data["version"] = date("YmdHis");

	$f = fopen($jsonPath, "w") or die("Unable to create file.");
	$json = json_encode($data, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT);
	fwrite($f, $json);
	fclose($f);
}

function misc() {
	global $root, $home;
	$files = ["DataTables.json", "KeyboardLayouts.json", "KeyMapping.json", "Lexicon.json"];
	foreach ($files as $name) {
		$cmd = "cp \"{$root}/{$name}\" \"{$home}/{$name}\" ";
		// echo $cmd . "\n";
		exec($cmd);
	}

}

// $cmd = "rm {$home}/db/*";
// @exec($cmd);
// array_map('unlink', glob("some/dir/*.txt"));

array_map('unlink', glob("{$home}/db/*"));

datatable();
lexicon();
misc();

