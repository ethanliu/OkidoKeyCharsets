<?php
echo "Generate KeyboardLayouts.json\n\n";

$destinationPath = self::$baseDir . "KeyboardLayouts.json";
$charsetPaths = glob(self::$baseDir . 'charset/*.charset.json', GLOB_NOSORT);
natsort($charsetPaths);

$contents = array(
	'version' => date("YmdHis"),
	'charsets' => array(),
);

foreach ($charsetPaths as $path) {
	// $charsets = json_decode(file_get_contents($path));
	// allows comments inside json
	$charsets = preg_replace('~//?\s*\*[\s\S]*?\*\s*//?~', '', file_get_contents($path));
	$charsets = json_decode($charsets);
	$error = json_last_error();

	if ($error !== JSON_ERROR_NONE) {
		echo "Syntax error: {$path}\n" . json_last_error_msg() . "\n";
		// var_dump($error);
		// continue;
		exit;
	}

	foreach ($charsets as $charset) {
		if (empty($charset) || empty($charset->name) || empty($charset->charsets)) {
			echo "Skipped, invalid json or charset structure: {$path}\n";
			continue;
		}
		// $names = array_map('strrev', array_reverse(explode('-', $charset->name, 2)));
		$name = $charset->name;
		if (isset($contents['charsets'][$name])) {
			echo "Skipped, charset already exists. {$path} [{$name}]\n";
			continue;
		}
		echo "{$charset->name}\n";
		unset($charset->name);
		$contents['charsets'][$name] = $charset;
	}
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($contents, JSON_UNESCAPED_UNICODE));
fclose($f);
echo "...version: {$contents['version']}\n\n";
