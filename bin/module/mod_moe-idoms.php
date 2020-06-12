<?php
/**
 * moe-idoms
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 12 June, 2020
 * @package module
 */

// 編號	成語	注音	漢語拼音	釋義	典源	典故說明	書證	用法說明	近義	反義	辨識	參考語詞
// https://idiom.wlps.kl.edu.tw/dict_idioms/3106.html


$map = [
	"c00965" => "㕙",
	"00875_w02" => "(尊刂)", // 尊刂
];


$pattern1 = '/<img src=\/cydic\/dicword\/(.*)\.jpg[^>]+>/m';
$pattern2 = ["（變）", "（一）", "（二）", "（三）", "（四）"];
// $pattern2 = '/（.*）/m';

// foreach ($raw as $row) {
$handle = fopen($srcPath, "r");
while (($row = fgetcsv($handle)) !== FALSE) {

	$index = isset($row[0]) ? intval($row[0]) : -1;
	$phrase = isset($row[1]) ? trim($row[1]) : "";
	$pinyin = isset($row[3]) ? trim($row[3]) : "";

	if (strpos($phrase, "<img") !== false) {
		// echo "https://idiom.wlps.kl.edu.tw/dict_idioms/{index}.html";
		preg_match_all($pattern1, $phrase, $matches, PREG_SET_ORDER, 0);
		foreach ($matches as $match) {
			$word = $map[$match[1]];
			if (empty($word)) {
				// not exists in unicode
				continue;
			}
			$phrase = str_replace($match[0], $word, $phrase);
		}
	}

	if ($index <= 0 || empty($phrase) || empty($pinyin)) {
		// var_dump($row);
		continue;
	}

	// $pinyins = preg_split($pattern2, $pinyin);
	$pinyins = explode("\n", str_replace($pattern2, "\n", $pinyin));
	if (!empty($pinyins)) {
		foreach ($pinyins as $k => $v) {
			$v = trim(strtolower(str_replace(" ", "", self::stripAccents($v))));
			$pinyins[$k] = $v;
		}
		$pinyins = array_unique(array_filter($pinyins));
	}
	else {
		$pinyins[] = trim(strtolower(str_replace(" ", "", self::stripAccents($pinyin))));
	}

	foreach ($pinyins as $pinyin) {
		echo "{$phrase}\t0\t{$pinyin}\n";
	}
}

