<?php
echo "Generate DataTables.json\n\n";

$destinationPath = self::$baseDir . "DataTables.json";
$filenames = glob(self::$baseDir . 'table/*.cin', GLOB_NOSORT);
natcasesort($filenames);

$result = array(
	'version' => date("YmdHis"),
	'datatables' => [],
	'splits' => [],
);

$items = [];

foreach ($filenames as $path) {
	$filename = basename($path);
	if (in_array($filename, self::$excludeDatables)) {
		// echo "Exclude: {$filename}\n";
		continue;
	}

	$table = new TableReader($path, true);
	$license = trim($table->description);
	// $link = "";
	//
	// $re = '#\bhttps?://[^,\s()<>]+(?:\([\w\d]+\)|([^,[:punct:]\s]|/))#mi';
	// preg_match($re, $license, $matches);
	// if ($matches) {
	// 	$link = trim($matches[0]);
	// }

	$item = [
		'ename' => $table->info['ename'] ?? '',
		'cname' => $table->info['cname'] ?? '',
		'name' => $table->info['name'] ?? '',
		'cin' => "table/{$filename}",
		'db' => "db/{$filename}.db",
		'license' => $license,
		// 'link' => $link,
	];

	$result['datatables'][] = $item;

	// init splits
	// $result['splits'][$filename] = ["github" => 0, "gitee" => 0];
	// to ensure the correct json formating
	$result['splits'][$filename] = ["gitee" => 0];

	echo "Add: {$filename} -> {$item['ename']} {$item['cname']}\n";
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
$json = json_encode($result, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT);
fwrite($f, $json);
fclose($f);
echo "...version: {$result['version']}\n\n";
