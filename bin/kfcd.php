<?php
/**
 * kfcd parser
 * Source:
 * http://www.kaifangcidian.com/xiazai/cidian_zhyue-kfcd.zip
 * https://words.hk/faiman/analysis/existingwordcount.json
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 27 May, 2020
 */


$src = __DIR__ . "/../tmp/existingwordcount.json";
$weights = json_decode(file_get_contents($src), true);

$src = __DIR__ . "/../tmp/cidian_zhyue-ft-kfcd-yp-2019623.txt";
$raw = file_get_contents($src);
$offset = mb_strpos($raw, "[");
$raw = json_decode(mb_substr($raw, $offset), true);

$phrase = "";
$pinyin = "";
$weight = 0;
$matches = [];

foreach ($raw as $index => $item) {
	// echo "#{$index}: {$item}\n";
	preg_match('/^[a-zA-Z]/', $item, $matches);
	if (empty($matches)) {
		if (!empty($phrase) && !empty($pinyin)) {
			if (mb_strlen($phrase) > 1) {
				$weight = (isset($weights[$phrase])) ? intval($weights[$phrase]) * 1000 : 0;
				echo "{$phrase}\t{$weight}\t{$pinyin}\n";
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