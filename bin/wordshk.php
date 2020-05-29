<?php
/**
 * words.hk parser
 * Source:
 * https://words.hk/faiman/analysis/wordslist.json
 * https://words.hk/faiman/analysis/existingwordcount.json
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 29 May, 2020
 */


$src = __DIR__ . "/../tmp/wordslist.json";
$src2 = __DIR__ . "/../tmp/existingwordcount.json";

$weights = json_decode(file_get_contents($src2), true);
$raw = json_decode(file_get_contents($src), true);

// $index = 0;
$phrase = "";
$pinyin = "";
$weight = 0;

foreach ($raw as $phrase => $pinyins) {
	// $index++;

	$weight = 0;
	$phrase = trim($phrase);
	$pinyin = empty($pinyins) ? "" : $pinyins[0] ?? "";
	$pinyin = trim(str_replace(" ", "", $pinyin));

	if (empty($phrase) || empty($pinyin) || mb_strlen($phrase) < 2) {
		continue;
	}

	if (isset($weights[$phrase])) {
		$weight = intval($weights[$phrase]) * 1000;
	}

	echo("{$phrase}\t{$weight}\t{$pinyin}\n");

	// if ($index > 20) {
	// 	break;
	// }
}
