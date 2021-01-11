<?php
/**
 * jieba dict.txt parser
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 6 January, 2021
 * @package module
 */


// $dict serve as pinyin cache, reduce CharTransformer usage

$dict = [];

foreach ($argv as $path) {
	if (!empty($path) && file_exists($path)) {
		$raw = explode("\n", file_get_contents($path));
		foreach ($raw as $line) {
			$line = trim($line);
			$rows = explode("\t", $line);
			if (isset($rows[2])) {
				$dict[$rows[0]] = $rows[2];
			}
		}
	}
}

// var_dump($dict);
// exit;

$raw = explode("\n", file_get_contents($srcPath));

foreach ($raw as $line) {
	$line = trim($line);
	// $row = explode(" ", $line);
	$row = preg_split('/\s+/', $line);

	$phrase = array_shift($row) ?? "";
	$weight = array_shift($row) ?? 0;
	$pinyin = isset($dict[$phrase]) ? $dict[$phrase] : "";

	if (empty($phrase)) {
		continue;
	}

	if (empty($pinyin)) {
		$cmd = __DIR__ . "/../CharTransformer -pinyin \"" . $phrase . "\"";
		$pinyin = trim(shell_exec($cmd));
		if ($pinyin === $phrase) {
			$pinyin = "";
		}
		else {
			$pinyin = str_replace(" ", "", $pinyin);
		}
	}

	echo $phrase . "\t" . $weight . "\t" . $pinyin . "\n";
}

