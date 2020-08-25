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
		// echo "Exclude: {$filename}\n";
		continue;
	}

	$table = new TableReader($path, true);
	$item = [
		'ename' => $table->info['ename'] ?? '',
		'cname' => $table->info['cname'] ?? '',
		'name' => $table->info['name'] ?? '',
		'cin' => "table/{$filename}",
		'db' => "db/{$filename}.db",
		'license' => $table->description,
	];

	$result['datatables'][] = $item;
	echo "Add: {$filename} -> {$item['ename']} {$item['cname']}\n";
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($result, JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT));
fclose($f);
echo "...version: {$result['version']}\n\n";
