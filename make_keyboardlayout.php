<?php
/**
 * Charsets.json builder
 *
 * @author Ethan Liu <***REMOVED***>
 * @copyright Creativecrap.com, 15 February, 2015
 */

include dirname(__FILE__) . "/config.php";

$destinationPath = "./KeyboardLayouts.json";

$charsetPaths = glob('./KeyboardLayouts/*.charset.json', GLOB_NOSORT);
natsort($charsetPaths);

$contents = array(
	'version' => date("YmdHis"),
	'charsets' => array(),
);

foreach ($charsetPaths as $path) {
	$charsets = json_decode(file_get_contents($path));
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
		unset($charset->name);
		$contents['charsets'][$name] = $charset;
	}
}

$f = fopen($destinationPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($contents));
fclose($f);
echo "\nExported {$destinationPath} version: {$contents['version']}\n";

