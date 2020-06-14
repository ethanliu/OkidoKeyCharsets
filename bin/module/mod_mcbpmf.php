<?php
/**
 * McBopomofo
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 14 June, 2020
 * @package module
 */


$weightPhrasePath = dirname($srcPath) . "/phrase.occ";
$weights = [];
if (file_exists($weightPhrasePath)) {
	$raw = explode("\n", file_get_contents($weightPhrasePath));
	foreach ($raw as $line) {
		$row = explode("\t", trim($line));
		if (empty($row) || empty($line)) {
			continue;
		}
		if (count($row) != 2) {
			continue;
		}
		$weights[$row[0]] = (intval($row[1] ?? 0)) * 100;
	}
}

$map = [
	"ㄅ" => "b", "ㄅㄚ" => "ba", "ㄅㄛ" => "bo", "ㄅㄞ" => "bai", "ㄅㄟ" => "bei", "ㄅㄠ" => "bao", "ㄅㄢ" => "ban", "ㄅㄣ" => "ben", "ㄅㄤ" => "bang", "ㄅㄥ" => "beng", "ㄅㄧ" => "bi", "ㄅㄧㄝ" => "bie", "ㄅㄧㄠ" => "biao", "ㄅㄧㄢ" => "bian", "ㄅㄧㄣ" => "bin", "ㄅㄧㄥ" => "bing", "ㄅㄨ" => "bu",
	"ㄆ" => "p", "ㄆㄚ" => "pa", "ㄆㄛ" => "po", "ㄆㄞ" => "pai", "ㄆㄟ" => "pei", "ㄆㄠ" => "pao", "ㄆㄡ" => "pou", "ㄆㄢ" => "pan", "ㄆㄣ" => "pen", "ㄆㄤ" => "pang", "ㄆㄥ" => "peng", "ㄆㄧ" => "pi", "ㄆㄧㄝ" => "pie", "ㄆㄧㄠ" => "piao", "ㄆㄧㄢ" => "pian", "ㄆㄧㄣ" => "pin", "ㄆㄧㄥ" => "ping", "ㄆㄨ" => "pu",
	"ㄇ" => "m", "ㄇㄚ" => "ma", "ㄇㄛ" => "mo", "ㄇㄜ" => "me", "ㄇㄞ" => "mai", "ㄇㄟ" => "mei", "ㄇㄠ" => "mao", "ㄇㄡ" => "mou", "ㄇㄢ" => "man", "ㄇㄣ" => "men", "ㄇㄤ" => "mang", "ㄇㄥ" => "meng", "ㄇㄧ" => "mi", "ㄇㄧㄝ" => "mie", "ㄇㄧㄠ" => "miao", "ㄇㄧㄡ" => "miu", "ㄇㄧㄢ" => "mian", "ㄇㄧㄣ" => "min", "ㄇㄧㄥ" => "ming", "ㄇㄨ" => "mu",
	"ㄈ" => "f", "ㄈㄚ" => "fa", "ㄈㄛ" => "fo", "ㄈㄟ" => "fei", "ㄈㄡ" => "fou", "ㄈㄢ" => "fan", "ㄈㄣ" => "fen", "ㄈㄤ" => "fang", "ㄈㄥ" => "feng", "ㄈㄧㄠ" => "fiao", "ㄈㄨ" => "fu", "ㄈㄨㄥ" => "fong",
	"ㄉ" => "d", "ㄉㄚ" => "da", "ㄉㄜ" => "de", "ㄉㄞ" => "dai", "ㄉㄟ" => "dei", "ㄉㄠ" => "dao", "ㄉㄡ" => "dou", "ㄉㄢ" => "dan", "ㄉㄣ" => "den", "ㄉㄤ" => "dang", "ㄉㄥ" => "deng", "ㄉㄧ" => "di", "ㄉㄧㄚ" => "dia", "ㄉㄧㄝ" => "die", "ㄉㄧㄠ" => "diao", "ㄉㄧㄡ" => "diu", "ㄉㄧㄢ" => "dian", "ㄉㄧㄤ" => "diang", "ㄉㄧㄥ" => "ding", "ㄉㄨ" => "du", "ㄉㄨㄛ" => "duo", "ㄉㄨㄟ" => "dui", "ㄉㄨㄢ" => "duan", "ㄉㄨㄣ" => "dun", "ㄉㄨㄥ" => "dong",
	"ㄊ" => "t", "ㄊㄚ" => "ta", "ㄊㄜ" => "te", "ㄊㄞ" => "tai", "ㄊㄠ" => "tao", "ㄊㄡ" => "tou", "ㄊㄢ" => "tan", "ㄊㄤ" => "tang", "ㄊㄥ" => "teng", "ㄊㄧ" => "ti", "ㄊㄧㄝ" => "tie", "ㄊㄧㄠ" => "tiao", "ㄊㄧㄢ" => "tian", "ㄊㄧㄥ" => "ting", "ㄊㄨ" => "tu", "ㄊㄨㄛ" => "tuo", "ㄊㄨㄟ" => "tui", "ㄊㄨㄢ" => "tuan", "ㄊㄨㄣ" => "tun", "ㄊㄨㄥ" => "tong",
	"ㄋ" => "n", "ㄋㄚ" => "na", "ㄋㄜ" => "ne", "ㄋㄞ" => "nai", "ㄋㄟ" => "nei", "ㄋㄠ" => "nao", "ㄋㄡ" => "nou", "ㄋㄢ" => "nan", "ㄋㄣ" => "nen", "ㄋㄤ" => "nang", "ㄋㄥ" => "neng", "ㄋㄧ" => "ni", "ㄋㄧㄚ" => "nia", "ㄋㄧㄝ" => "nie", "ㄋㄧㄠ" => "niao", "ㄋㄧㄡ" => "niu", "ㄋㄧㄢ" => "nian", "ㄋㄧㄣ" => "nin", "ㄋㄧㄤ" => "niang", "ㄋㄧㄥ" => "ning", "ㄋㄨ" => "nu", "ㄋㄨㄛ" => "nuo", "ㄋㄨㄢ" => "nuan", "ㄋㄨㄣ" => "nun", "ㄋㄨㄥ" => "nong", "ㄋㄩ" => "nü", "ㄋㄩㄝ" => "nüe", "ㄋㄩㄢ" => "nuan",
	"ㄌ" => "l", "ㄌㄚ" => "la", "ㄌㄛ" => "lo", "ㄌㄜ" => "le", "ㄌㄞ" => "lai", "ㄌㄟ" => "lei", "ㄌㄠ" => "lao", "ㄌㄡ" => "lou", "ㄌㄢ" => "lan", "ㄌㄤ" => "lang", "ㄌㄥ" => "leng", "ㄌㄧ" => "li", "ㄌㄧㄚ" => "lia", "ㄌㄧㄝ" => "lie", "ㄌㄧㄠ" => "liao", "ㄌㄧㄡ" => "liu", "ㄌㄧㄢ" => "lian", "ㄌㄧㄣ" => "lin", "ㄌㄧㄤ" => "liang", "ㄌㄧㄥ" => "ling", "ㄌㄨ" => "lu", "ㄌㄨㄛ" => "luo", "ㄌㄨㄢ" => "luan", "ㄌㄨㄣ" => "lun", "ㄌㄨㄥ" => "long", "ㄌㄩ" => "lü", "ㄌㄩㄝ" => "lüe", "ㄌㄩㄢ" => "lvan", "ㄌㄩㄣ" => "lün",
	"ㄍ" => "g", "ㄍㄚ" => "ga", "ㄍㄜ" => "ge", "ㄍㄞ" => "gai", "ㄍㄟ" => "gei", "ㄍㄠ" => "gao", "ㄍㄡ" => "gou", "ㄍㄢ" => "gan", "ㄍㄣ" => "gen", "ㄍㄤ" => "gang", "ㄍㄥ" => "geng", "ㄍㄨ" => "gu", "ㄍㄨㄚ" => "gua", "ㄍㄨㄛ" => "guo", "ㄍㄨㄞ" => "guai", "ㄍㄨㄟ" => "gui", "ㄍㄨㄢ" => "guan", "ㄍㄨㄣ" => "gun", "ㄍㄨㄤ" => "guang", "ㄍㄨㄥ" => "gong",
	"ㄎ" => "k", "ㄎㄚ" => "ka", "ㄎㄜ" => "ke", "ㄎㄞ" => "kai", "ㄎㄠ" => "kao", "ㄎㄡ" => "kou", "ㄎㄢ" => "kan", "ㄎㄣ" => "ken", "ㄎㄤ" => "kang", "ㄎㄥ" => "keng", "ㄎㄨ" => "ku", "ㄎㄨㄚ" => "kua", "ㄎㄨㄛ" => "kuo", "ㄎㄨㄞ" => "kuai", "ㄎㄨㄟ" => "kui", "ㄎㄨㄢ" => "kuan", "ㄎㄨㄣ" => "kun", "ㄎㄨㄤ" => "kuang", "ㄎㄨㄥ" => "kong",
	"ㄏ" => "h", "ㄏㄚ" => "ha", "ㄏㄜ" => "he", "ㄏㄞ" => "hai", "ㄏㄟ" => "hei", "ㄏㄠ" => "hao", "ㄏㄡ" => "hou", "ㄏㄢ" => "han", "ㄏㄣ" => "hen", "ㄏㄤ" => "hang", "ㄏㄥ" => "heng", "ㄏㄨ" => "hu", "ㄏㄨㄚ" => "hua", "ㄏㄨㄛ" => "huo", "ㄏㄨㄞ" => "huai", "ㄏㄨㄟ" => "hui", "ㄏㄨㄢ" => "huan", "ㄏㄨㄣ" => "hun", "ㄏㄨㄤ" => "huang", "ㄏㄨㄥ" => "hong",
	"ㄐ" => "ji", "ㄐㄧ" => "ji", "ㄐㄧㄚ" => "jia", "ㄐㄧㄝ" => "jie", "ㄐㄧㄠ" => "jiao", "ㄐㄧㄡ" => "jiu", "ㄐㄧㄢ" => "jian", "ㄐㄧㄣ" => "jin", "ㄐㄧㄤ" => "jiang", "ㄐㄧㄥ" => "jing", "ㄐㄩ" => "ju", "ㄐㄩㄝ" => "jue", "ㄐㄩㄢ" => "juan", "ㄐㄩㄣ" => "jun", "ㄐㄩㄥ" => "jiong",
	"ㄑ" => "qi", "ㄑㄧ" => "qi", "ㄑㄧㄚ" => "qia", "ㄑㄧㄝ" => "qie", "ㄑㄧㄠ" => "qiao", "ㄑㄧㄡ" => "qiu", "ㄑㄧㄢ" => "qian", "ㄑㄧㄣ" => "qin", "ㄑㄧㄤ" => "qiang", "ㄑㄧㄥ" => "qing", "ㄑㄩ" => "qu", "ㄑㄩㄝ" => "que", "ㄑㄩㄢ" => "quan", "ㄑㄩㄣ" => "qun", "ㄑㄩㄥ" => "qiong",
	"ㄒ" => "xi", "ㄒㄧ" => "xi", "ㄒㄧㄚ" => "xia", "ㄒㄧㄝ" => "xie", "ㄒㄧㄠ" => "xiao", "ㄒㄧㄡ" => "xiu", "ㄒㄧㄢ" => "xian", "ㄒㄧㄣ" => "xin", "ㄒㄧㄤ" => "xiang", "ㄒㄧㄥ" => "xing", "ㄒㄩ" => "xu", "ㄒㄩㄝ" => "xue", "ㄒㄩㄢ" => "xuan", "ㄒㄩㄣ" => "xun", "ㄒㄩㄥ" => "xiong",
	"ㄓ" => "zhi", "ㄓㄚ" => "zha", "ㄓㄜ" => "zhe", "ㄓㄞ" => "zhai", "ㄓㄟ" => "zhei", "ㄓㄠ" => "zhao", "ㄓㄡ" => "zhou", "ㄓㄢ" => "zhan", "ㄓㄣ" => "zhen", "ㄓㄤ" => "zhang", "ㄓㄥ" => "zheng", "ㄓㄨ" => "zhu", "ㄓㄨㄚ" => "zhua", "ㄓㄨㄛ" => "zhuo", "ㄓㄨㄞ" => "zhuai", "ㄓㄨㄟ" => "zhui", "ㄓㄨㄢ" => "zhuan", "ㄓㄨㄣ" => "zhun", "ㄓㄨㄤ" => "zhuang", "ㄓㄨㄥ" => "zhong",
	"ㄔ" => "chi", "ㄔㄚ" => "cha", "ㄔㄜ" => "che", "ㄔㄞ" => "chai", "ㄔㄠ" => "chao", "ㄔㄡ" => "chou", "ㄔㄢ" => "chan", "ㄔㄣ" => "chen", "ㄔㄤ" => "chang", "ㄔㄥ" => "cheng", "ㄔㄨ" => "chu", "ㄔㄨㄚ" => "chua", "ㄔㄨㄛ" => "chuo", "ㄔㄨㄞ" => "chuai", "ㄔㄨㄟ" => "chui", "ㄔㄨㄢ" => "chuan", "ㄔㄨㄣ" => "chun", "ㄔㄨㄤ" => "chuang", "ㄔㄨㄥ" => "chong",
	"ㄕ" => "shi", "ㄕㄚ" => "sha", "ㄕㄜ" => "she", "ㄕㄞ" => "shai", "ㄕㄟ" => "shei", "ㄕㄠ" => "shao", "ㄕㄡ" => "shou", "ㄕㄢ" => "shan", "ㄕㄣ" => "shen", "ㄕㄤ" => "shang", "ㄕㄥ" => "sheng", "ㄕㄨ" => "shu", "ㄕㄨㄚ" => "shua", "ㄕㄨㄛ" => "shuo", "ㄕㄨㄞ" => "shuai", "ㄕㄨㄟ" => "shui", "ㄕㄨㄢ" => "shuan", "ㄕㄨㄣ" => "shun", "ㄕㄨㄤ" => "shuang", "ㄕㄨㄥ" => "shong",
	"ㄖ" => "ri", "ㄖㄜ" => "re", "ㄖㄠ" => "rao", "ㄖㄡ" => "rou", "ㄖㄢ" => "ran", "ㄖㄣ" => "ren", "ㄖㄤ" => "rang", "ㄖㄥ" => "reng", "ㄖㄨ" => "ru", "ㄖㄨㄛ" => "ruo", "ㄖㄨㄟ" => "rui", "ㄖㄨㄢ" => "ruan", "ㄖㄨㄣ" => "run", "ㄖㄨㄥ" => "rong",
	"ㄗ" => "zi", "ㄗㄚ" => "za", "ㄗㄜ" => "ze", "ㄗㄞ" => "zai", "ㄗㄟ" => "zei", "ㄗㄠ" => "zao", "ㄗㄡ" => "zou", "ㄗㄢ" => "zan", "ㄗㄣ" => "zen", "ㄗㄤ" => "zang", "ㄗㄥ" => "zeng", "ㄗㄨ" => "zu", "ㄗㄨㄛ" => "zuo", "ㄗㄨㄟ" => "zui", "ㄗㄨㄢ" => "zuan", "ㄗㄨㄣ" => "zun", "ㄗㄨㄥ" => "zong",
	"ㄘ" => "ci", "ㄘㄚ" => "ca", "ㄘㄜ" => "ce", "ㄘㄞ" => "cai", "ㄘㄠ" => "cao", "ㄘㄡ" => "cou", "ㄘㄢ" => "can", "ㄘㄣ" => "cen", "ㄘㄤ" => "cang", "ㄘㄥ" => "ceng", "ㄘㄨ" => "cu", "ㄘㄨㄛ" => "cuo", "ㄘㄨㄟ" => "cui", "ㄘㄨㄢ" => "cuan", "ㄘㄨㄣ" => "cun", "ㄘㄨㄥ" => "cong",
	"ㄙ" => "si", "ㄙㄚ" => "sa", "ㄙㄜ" => "se", "ㄙㄞ" => "sai", "ㄙㄟ" => "sei", "ㄙㄠ" => "sao", "ㄙㄡ" => "sou", "ㄙㄢ" => "san", "ㄙㄣ" => "sen", "ㄙㄤ" => "sang", "ㄙㄥ" => "seng", "ㄙㄨ" => "su", "ㄙㄨㄛ" => "suo", "ㄙㄨㄟ" => "sui", "ㄙㄨㄢ" => "suan", "ㄙㄨㄣ" => "sun", "ㄙㄨㄥ" => "song",
	"ㄧ" => "yi", "ㄧㄚ" => "ya", "ㄧㄛ" => "yo", "ㄧㄝ" => "ye", "ㄧㄞ" => "yai", "ㄧㄠ" => "yao", "ㄧㄡ" => "you", "ㄧㄢ" => "yan", "ㄧㄣ" => "yin", "ㄧㄤ" => "yang", "ㄧㄥ" => "ying",
	"ㄨ" => "wu", "ㄨㄚ" => "wa", "ㄨㄛ" => "wo", "ㄨㄞ" => "wai", "ㄨㄟ" => "wei", "ㄨㄢ" => "wan", "ㄨㄣ" => "wen", "ㄨㄤ" => "wang", "ㄨㄥ" => "weng",
	"ㄩ" => "yu", "ㄩㄝ" => "yue", "ㄩㄢ" => "yuan", "ㄩㄣ" => "yun", "ㄩㄥ" => "yong",
	"ㄚ" => "a",
	"ㄛ" => "o",
	"ㄜ" => "e",
	"ㄝ" => "e",
	"ㄞ" => "ai",
	"ㄟ" => "ei",
	"ㄠ" => "ao",
	"ㄡ" => "ou",
	"ㄢ" => "an",
	"ㄣ" => "en",
	"ㄤ" => "ang",
	"ㄥ" => "eng",
	"ㄦ" => "er",
];
$tones = ["ˊ", "ˇ", "ˋ", "˙"];

$fixes = [
	"嚇出 ㄏㄧㄚˋ ㄔㄨ" => "嚇出 ㄒㄧㄚˋ ㄔㄨ",
	"嚇到 ㄏㄧㄚˋ ㄉㄠˋ" => "嚇到 ㄒㄧㄚˋ ㄉㄠˋ",
];

$raw = explode("\n", file_get_contents($srcPath));
foreach ($raw as $line) {
	$line = isset($fixes[$line]) ? $fixes[$line] : trim($line);

	$row = explode(" ", $line);
	$phrase = array_shift($row);
	$pinyin = "";

	if (empty($row) || empty($phrase)) {
		continue;
	}

	foreach ($row as $seg) {
		$seg = str_replace($tones, "", $seg);
		if (!isset($map[$seg])) {
			echo "{$seg}: {$line}\n";
			continue;
		}
		$pinyin .= $map[$seg];
	}

	$weight = (isset($weights[$phrase])) ? $weights[$phrase] : 0;

	echo "{$phrase}\t{$weight}\t{$pinyin}\n";
}
