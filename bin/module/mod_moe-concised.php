<?php
/**
 * moe-concised
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 12 June, 2020
 * @package module
 */


// "字詞號","字詞名","部首外筆畫數","總筆畫數","注音一式","漢語拼音","相似詞","相反詞","釋義","多音參見訊息"

$pattern1 = '/<img src=\/cydic\/dicword\/(.*)\.jpg[^>]+>/m';
$pattern2 = ["（變）", "（一）", "（二）", "（三）", "（四）", "(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "（語音）"];
$pattern3 = '/(.*)（[0-9A-Za-z]{1,}）/m';
$pattern3 = '/　{1,}([a-z　 ]{1,})（/m';

// foreach ($raw as $row) {
$handle = fopen($srcPath, "r");
while (($row = fgetcsv($handle)) !== FALSE) {

	$index = isset($row[0]) ? intval($row[0]) : -1;
	$phrase = isset($row[1]) ? trim($row[1]) : "";
	$pinyin = isset($row[5]) ? trim($row[5]) : "";
	$extra = isset($row[9]) ? trim($row[9]) : "";

	// if (strpos($phrase, "<img") !== false) {
	// 	// echo "https://idiom.wlps.kl.edu.tw/dict_idioms/{index}.html";
	// 	preg_match_all($pattern1, $phrase, $matches, PREG_SET_ORDER, 0);
	// 	foreach ($matches as $match) {
	// 		$word = $map[$match[1]];
	// 		if (empty($word)) {
	// 			// not exists in unicode
	// 			var_dump($row);exit;
	// 			continue;
	// 		}
	// 		$phrase = str_replace($match[0], $word, $phrase);
	// 	}
	// }

	if ($index <= 0 || empty($phrase) || empty($pinyin)) {
		// var_dump($row);
		continue;
	}

	// $pinyins = preg_split($pattern2, $pinyin);
	$pinyins = explode("\n", str_replace($pattern2, "\n", $pinyin));
	if (!empty($pinyins)) {
		// if (count($pinyins) > 1) {
		// 	echo "---------\n{$pinyin}\n";
		// 	var_dump($pinyins);
		// }
		foreach ($pinyins as $k => $v) {
			$v = trim(strtolower(str_replace(["　", " "], "", self::stripAccents($v))));
			$pinyins[$k] = $v;
		}
		$pinyins = array_unique(array_filter($pinyins));
		// var_dump($pinyins);
		// echo "xxxx\n";
		// var_dump($row);
	}
	else {
		$pinyins[] = trim(strtolower(str_replace(" ", "", self::stripAccents($pinyin))));
	}

	if (!empty($extra)) {
		$extra = str_replace(["<br>", "  "], "\n", $extra);
		$extra = self::stripAccents($extra);
		preg_match_all($pattern3, $extra, $matches, PREG_SET_ORDER, 0);
		foreach ($matches as $match) {
			$v = trim(str_replace(["　", " "], "", $match[1]));
			// echo "==> " . $match[1] . "\n";
			$pinyins[] = $v;
		}
		$pinyins = array_unique(array_filter($pinyins));
	}

	// var_dump($pinyins);
	foreach ($pinyins as $pinyin) {
		echo "{$phrase}\t0\t{$pinyin}\n";
	}
}

