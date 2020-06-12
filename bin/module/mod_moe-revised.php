<?php
/**
 * moe-revised
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 12 June, 2020
 * @package module
 */


// "字詞屬性","字詞號","字詞名","部首字","部首外筆畫數","總筆畫數","注音一式","漢語拼音","相似詞","相反詞","釋義","編按","多音參見訊息","異體字"


// http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi?o=dcbdic&searchid=W00000000086

// $map = [];


$pattern1 = '/<img src=\/cydic\/dicword\/(.*)\.jpg[^>]+>/m';
$pattern2 = ["（變）", "（一）", "（二）", "（三）", "（四）", "(一)", "(二)", "(三)", "(四)", "(五)", "(六)", "（語音）", "（又音）", "（讀音）"];
// $pattern3 = '/(.*)（[0-9A-Za-z]{1,}）/m';
$pattern3 = '/　{1,}([a-z　 ]{1,})（/m';
$pattern4 = '/\.gif|png|jpg|jpeg|GIF|PNG|JPG|JPEG/';

// $index = 0;
$handle = fopen($srcPath, "r");
while (($row = fgetcsv($handle)) !== FALSE) {

	// $index += 1;
	$code = isset($row[1]) ? trim($row[1]) : '';
	$phrase = isset($row[2]) ? trim($row[2]) : "";
	$pinyin = isset($row[7]) ? trim($row[7]) : "";
	$extra = isset($row[12]) ? trim($row[12]) : "";

	// if (strpos($phrase, ".gif") !== false) {
	if (preg_match($pattern4, $phrase)) {
		// echo $phrase . "\n";
		// // $serial = str_pad($index, 11, "0");
		// // echo "http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi?o=dcbdic&searchid=W{$serial}\n";
		// echo $row[1] . "\n";
		// echo $row[6] . "\n";
		// echo $row[10] . "\n";
		// echo "--------\n";
		// exit;
		continue;
	}

	if (empty($code) || $code == '字詞號' || empty($phrase) || empty($pinyin)) {
		// var_dump($row);exit;
		// 異體字
		// echo "{$row[1]}, {$row[2]}, {$row[7]}, {$row[10]}, {$row[12]}\n";
		continue;
	}

	// $pinyins = preg_split($pattern2, $pinyin);
	$pinyins = explode("\n", str_replace($pattern2, "\n", $pinyin));
	if (!empty($pinyins)) {
		foreach ($pinyins as $k => $v) {
			$v = trim(strtolower(str_replace(["　", " ", "，"], "", self::stripAccents($v))));
			$pinyins[$k] = $v;
		}
		$pinyins = array_unique(array_filter($pinyins));
	}
	else {
		$pinyins[] = trim(strtolower(str_replace([" ", "，"], "", self::stripAccents($pinyin))));
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

	foreach ($pinyins as $pinyin) {
		// echo "{$row[1]}, {$row[2]}, {$row[7]}, {$row[12]}\n=> ";
		echo "{$phrase}\t0\t{$pinyin}\n";
	}
}

