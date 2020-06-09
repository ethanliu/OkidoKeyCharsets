<?php
/**
 * rime-cantonese cin converter
 *
 * https://github.com/rime/rime-cantonese/
 * https://raw.githubusercontent.com/rime/rime-cantonese/blob/master/jyut6ping3.dict.yaml
 * https://words.hk/faiman/analysis/existingwordcount.json
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 3 June, 2020
 */


$src = __DIR__ . "/../tmp/jyut6ping3.dict.yaml";
$src2 = __DIR__ . "/../tmp/existingwordcount.json";

// table/jyut6ping3.cin
// table/jyut6ping3-toneless.cin
// lexicon/rime-cantonese.csv

if (!file_exists($src)) {
	echo "File Not Found";
	exit;
}

$raw = explode("\n", file_get_contents($src));
$argv = getopt("pt");
// $stripPhraseSection = isset($argv["p"]) ? true : false;
// $stripTone = isset($argv["t"]) ? true : false;

if (isset($argv["p"])) {
	parsePhrase($raw, $src2);
}
else {
	parseRadical($raw, isset($argv["t"]));
}

function parseRadical($raw, $toneless = false) {
	$ename = "Jyut6ping3" . ($toneless ? " (Toneless)" : "");
	$cname = "粵拼" . ($toneless ? " (無調號)" : "");

	$radicals = [];
	$parsing = false;

	foreach ($raw as $line) {
		if ($line === "# 單字音") {
			$parsing = true;
			continue;
		}

		if ($line === "# 詞彙") {
			break;
		}

		if (!$parsing) {
			continue;
		}

		$line = trim(preg_replace('/#(.?)*/', '', $line));
		if (empty($line)) {
			continue;
		}

		$row = explode("\t", $line);
		if (empty($row)) {
			continue;
		}

		$phrase = trim($row[0]);
		$radical = trim(str_replace(" ", "", $row[1]));
		if ($toneless) {
			$radical = str_replace(['1', '2', '3', '4', '5', '6'], '', $radical);
		}

		// $weight = intval(str_replace("%", "", ($row[2] ?? "0"))) / 100;

		$weight = 0;
		if (!isset($row[2])) {
			$weight = 100;
		}
		else {
			$weight = intval(str_replace("%", "", $row[2])) * 100;
			$weight = ($weight == 0) ? 10 : $weight;
		}

		$radicals[$radical][] = ["r" => $phrase, "w" => $weight];

		// if ($index > 30) {
		// 	break;
		// }
	}

	// dump

	echo "#
# Jyut6ping3 - " . $cname . "
# Version: 2020.05.19
#
# 本 CIN 表格轉換自 Rime 粵語拼音方案 jyut6ping3.dict.yaml
# 不含詞彙內容，將拼音去除空格後合併，並保留詞頻做為取字順序。
# 詞頻為 0% 為罕用詞，給予低優先權，未含詞頻者為一般優先權。
#
# 本檔案與原始來源相同，採共享創意 - 姓名標示 4.0 國際 (CC BY 4.0) 協議。
#
# Rime 粵語拼音方案: https://github.com/rime/rime-cantonese
# 共享創意 - 姓名標示 4.0 國際: https://creativecommons.org/licenses/by/4.0/deed.zh_TW
#
%ename " . $ename . "
%cname " . $cname . "
%encoding UTF-8
%selkey 1234567890
%endkey " . ($toneless ? "" : "123456") . "
%keyname begin
a a
b b
c c
d d
e e
f f
g g
h h
i i
j j
k k
l l
m m
n n
o o
p p
q q
r r
s s
t t
u u
v v
w w
x x
y y
z z" . ($toneless ? "" : "
1 1
2 2
3 3
4 4
5 5
6 6") . "
%keyname end
%chardef begin
";

	foreach ($radicals as $radical => $items) {
		usort($items, function($l, $r) {
			return $r["w"] <=> $l["w"];
		});

		foreach ($items as $item) {
			$comment = ($item['w'] == 100) ? '' : "\t#{$item['w']}";
			$phrase = trim($item['r']);
			echo "{$radical}\t{$phrase}{$comment}\n";
		}
	}

	echo "%chardef end\n";
}

function parsePhrase($raw, $wordcountPath) {
	$weights = json_decode(file_get_contents($wordcountPath), true);

	$radicals = [];
	$parsing = false;

	foreach ($raw as $line) {
		if ($line === "# 詞彙") {
			$parsing = true;
			continue;
		}

		if (!$parsing) {
			continue;
		}

		$line = trim(preg_replace('/#(.?)*/', '', $line));
		if (empty($line)) {
			continue;
		}

		$row = explode("\t", $line);
		if (empty($row)) {
			continue;
		}

		$phrase = trim($row[0]);
		$radical = trim(str_replace(" ", "", $row[1]));
		$radical = str_replace(['1', '2', '3', '4', '5', '6'], '', $radical);
		$weight = 0;

		if (isset($weights[$phrase])) {
			$weight = intval($weights[$phrase]) * 1000;
		}

		echo "{$phrase}\t{$weight}\t{$radical}\n";
	}
}

