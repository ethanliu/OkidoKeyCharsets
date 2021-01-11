<?php
/**
 * update splits
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 5 January, 2021
 * @package module
 */


$giteeRepoPath = isset($argv[0]) ? $argv[0] : "";

if (empty($giteeRepoPath) || !file_exists($giteeRepoPath)) {
	echo "Gitee repo path not found";
	exit;
}

$data = json_decode(file_get_contents($srcPath), true);

if (empty($data) || empty($data["splits"])) {
	echo "Unable to parsing splits";
	exit;
}

foreach ($data["splits"] as $path => $splits) {
	$cmd = "ls {$giteeRepoPath}/db/{$path}* | wc -l";
	$count = intval(trim(exec($cmd))) ?? 0;
	// echo "${path}: {$count}\n";
	$data["splits"][$path]["gitee"] = $count;
}

$data["version"] = date("YmdHis");
// var_dump($data["splits"]);

$f = fopen($srcPath, "w") or die("Unable to create file.");
$json = json_encode($data, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT);
fwrite($f, $json);
fclose($f);

