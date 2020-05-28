<?php


function reada() {
	$data = explode("\n", file_get_contents("./all-b.csv"));
	$contents = [];

	foreach ($data as $line) {
		$items = explode("\t", $line);
		$contents[$items[0]][] = $items[1];
	}

	return $contents;
}

$base = reada();
$paths = [];
$contents = [];

$paths[] = "./McBopomofo-phrase.csv";
$paths[] = "./MoE-concised.csv";
$paths[] = "./MoE-Revised.csv";
$paths[] = "./MoE-idioms.csv";

foreach ($paths as $path) {
	$data = explode("\n", file_get_contents($path));

	foreach ($data as $line) {
		$items = explode("\t", $line);

		if (isset($base[$items[0]]) && isset($items[2])) {
			foreach ($base[$items[0]] as $pinyin) {
				if ($pinyin != $items[2]) {
					// echo "{$items[0]}\t{$pinyin}\t{$items[2]}\n";
					$contents[] = $items[0] . "\t" . $pinyin;
				}
			}
		}
	}
}


$contents = implode("\n", $contents);
file_put_contents("./all-c.csv", $contents);


