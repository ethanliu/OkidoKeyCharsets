<?php
/**
 * kfcd parser
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 27 May, 2020
 */

$src = __DIR__ . "/../tmp/cidian_zhyue-ft-kfcd-yp-2019623.txt";
$raw = file_get_contents($src);
$offset = mb_strpos($raw, "[");
$raw = json_decode(mb_substr($raw, $offset), true);

$phrase = "";
$pinyin = "";
$matches = [];

foreach ($raw as $index => $item) {
	// echo "#{$index}: {$item}\n";
	preg_match('/^[a-zA-Z]/', $item, $matches);
	if (empty($matches)) {
		if (!empty($phrase) && !empty($pinyin)) {
			if (mb_strlen($phrase) > 1) {
				echo "{$phrase}\t0\t{$pinyin}\n";
			}
		}
		$phrase = $item;
		$pinyin = "";
	}
	else {
		$pinyin .= $item;
	}
	// if ($index > 220) {
	// 	break;
	// }
}