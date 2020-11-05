<?php
/**
 * builder - cli
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com
 */

// error_reporting(0);
// ini_set("error_reporting", FALSE);

include __DIR__ . "/database.php";
include __DIR__ . "/portable-utf8.php";
include __DIR__ . "/EmojiReader.php";
include __DIR__ . "/TableReader.php";

class Builder {
	private static $shared;
	private static $excludeDatables = [
		'array-shortcode.cin',
		'array-special.cin',
		// 'array30.cin',
		'array30_OkidoKey-big_0.75.cin',
		// 'bpmf-cns.cin',
		'bpmf-ext.cin',
		// 'bpmf-symbol.cin',
		// 'bpmf_punctuation.cin',
		'cj-ext.cin',
		'cj-wildcard.cin',
		'CnsPhonetic2016-08_GCINv2.cin',
		'egyptian.cin',
		'ehq-symbols.cin',
		'esperanto.cin',
		'jyutping.cin',
		'jyutping-toneless.cin',
		'kk.cin',
		'kks.cin',
		'klingon.cin',
		'ov_ezbig.cin',
		'ov_ezsmall.cin',
		'simplex-ext.cin',
		'stroke-stroke5.cin',
		'morse.cin',
		'telecode.cin',
		'wus.cin',
		'wut.cin',
	];
	private static $baseDir = "";

	public function __construct() {
		self::init();
	}

	public static function shared() {
		if (is_null(self::$shared)) {
			self::$shared = new self();
		}
		return self::$shared;
	}

	public static function run() {
		$argv = getopt("tdkmex:c:a:b:");
		// var_dump($argv);
		// var_dump($_SERVER['argv']);

		if (isset($argv['a']) || isset($argv['b'])) {
			$level = isset($argv['x']) ? intval($argv['x']) : 0;
			$basePath = isset($argv['b']) ? $argv['b'] : "table/array30.cin";
			$targetPath = isset($argv['a']) ? $argv['a'] : '';

			if (empty($targetPath) || !file_exists($targetPath)) {
				echo "Target table file not found.\n";
				exit;
			}

			if (empty($basePath) || !file_exists($basePath)) {
				echo "Base table file not found.\n";
				exit;
			}


			$baseTable = new TableReader($basePath, false);
			$targetTable = new TableReader($targetPath, false);

			// $result = diffTable($baseTable, $targetTable);
			// var_dump($result);

			$result = self::diffTable($targetTable, $baseTable);
			// var_dump($result);
			foreach ($result as $item) {
				if ($level > 0) {
					$category = self::unicodeBlock($item->value);
					if ($level == 3 && (strpos($category, 'CJK-Ext') !== false)) {
						continue;
					}
					else if ($level == 2 && ($category == 'BMP' || $category == 'SPUA-A' || $category == 'SPUA-B')) {
						continue;
					}
					else if ($level == 1 && !($category == 'CJK-ExtA' || $category == '')) {
						continue;
					}
				}
				echo "{$item->value}\n";
			}
			exit;
		}
		else if (isset($argv['x'])) {
			$level = intval($argv['x']);
			$src = "";
			$dst = "";

			$total = count($_SERVER['argv']);
			if ($total < 3) {
				echo "Missing argument\n";
				exit;
			}

			// $src = isset($_SERVER['argv'][$total - 2]) ? trim($_SERVER['argv'][$total - 2]) : '';
			// $dst = isset($_SERVER['argv'][$total - 1]) ? trim($_SERVER['argv'][$total - 1]) : '';

			$src = isset($_SERVER['argv'][$total - 1]) ? trim($_SERVER['argv'][$total - 1]) : '';
			if (empty($src)) {
				echo "Missing argument for input or output file paths\n";
				exit;
			}

			if (!file_exists($src)) {
				echo "Input file \"{$src}\" not exists\n";
				exit;
			}

			self::tiny($src, $level);
		}
		else if (isset($argv['c'])) {

			$offset = count($_SERVER['argv']) - 1;
			if ($offset != 3) {
				echo "Missing argument\n";
				exit;
			}

			$src = isset($_SERVER['argv'][$offset]) ? trim($_SERVER['argv'][$offset]) : '';
			$module = trim($argv['c']);

			switch ($module) {
				case 'jyut6ping3':
					$modulePath = __DIR__ . "/module/mod_jyut6ping3.php";
					$mode = "radical";
					$toneless = false;
				break;
				case 'jyut6ping3-toneless':
					$modulePath = __DIR__ . "/module/mod_jyut6ping3.php";
					$mode = "radical";
					$toneless = true;
				break;
				case 'jyut6ping3-phrase':
					$modulePath = __DIR__ . "/module/mod_jyut6ping3.php";
					$mode = "phrase";
					$toneless = true;
				break;
				default:
					$modulePath = __DIR__ . "/module/mod_{$module}.php";
				break;
			}

			$srcPath = realpath(__DIR__ . "/../" . $src);

			if (empty($module) || !file_exists($modulePath)) {
				echo "Module \"{$module}\" not found.\n";
				exit;
			}

			if (empty($src) || !file_exists($srcPath)) {
				echo "Input file \"{$src}\" not found.\n";
			}

			include $modulePath;
		}
		else {
			$invalid = true;

			if (isset($argv['k'])) {
				$invalid = false;
				include __DIR__ . "/module/KeyboardLayouts.php";
			}
			if (isset($argv['t'])) {
				$invalid = false;
				include __DIR__ . "/module/DataTables.php";
			}
			if (isset($argv['d'])) {
				$invalid = false;
				include __DIR__ . "/module/DatabaseTable.php";
			}
			if (isset($argv['m'])) {
				$invalid = false;
				include __DIR__ . "/module/DatabaseLexicon.php";
			}
			if (isset($argv['e'])) {
				$invalid = false;
				include __DIR__ . "/module/DatabaseEmoji.php";
			}

			if ($invalid) {
				self::usage();
			}
		}
	}

	private static function init() {
		self::$baseDir = realpath(dirname(__FIle__) . '/../') . '/';
	}

	private static function usage() {
		$basename = basename($_SERVER['PHP_SELF']);
		echo "
NAME
	{$basename} -- OkidoKey Package Tools

SYNOPSIS
	{$basename} [options]
	{$basename} -x [level] input.cin > output.cin
	{$basename} -c module input.file > output.csv

OPTIONS:
	-k	Generate KeyboardLayouts.json
	-t	Generate DataTables.json
	-d	Build Data Table Databases
	-m	Build Lexicon Databases
	-e	Build Emoji Databases
	-c	Run sub-module

	-x[level]	Strip Unicode blocks (BMP, SPUA, CJK-Ext...)
			level 0: strip all blocks (default)
			level 1: strip all blocks except CJK-ExtA
			level 2: strip SPUA blocks
			level 3: strip CJK-Ext A~D blocks

MODULES:
	jyut6ping3, jyut6ping3-tonless, jyut6ping3-phrase,
	moe-idioms, moe-concised, moe-revised,
	mcbpmf,

";
		exit;
	}

	// database

	static function getChardefId($db, $value, $suffix = "") {
		return $db->getOne("SELECT rowid FROM chardef{$suffix} WHERE char = :value", [":value" => $value]) ?? 0;
	}

	static function getKeydefId($db, $value, $suffix = "") {
		return $db->getOne("SELECT rowid FROM keydef{$suffix} WHERE key = :value", [":value" => $value]) ?? 0;
	}

	static function addChardef($db, $value, $suffix = "") {
		$db->exec("INSERT INTO chardef{$suffix} (`char`) VALUES (:value)", [":value" => $value]);
	}

	static function addKeydef($db, $value, $suffix = "") {
		$db->exec("INSERT INTO keydef{$suffix} (`key`) VALUES (:value)", [":value" => $value]);
	}

	static function addEntry($db, $key_id, $char_id, $suffix = "") {
		if ($key_id < 1 || $char_id < 1) {
			return false;
		}

		$db->exec("INSERT INTO entry{$suffix} (`keydef{$suffix}_id`, `chardef_id`) VALUES (:v1, :v2)", [":v1" => $key_id, ":v2" => $char_id]);
	}

	static function addInfo($db, $name, $value) {
		$db->exec("INSERT OR IGNORE INTO info (`name`, `value`) VALUES (:name, :value)", [":name" => $name, ":value" => $value]);
	}

	static function addKeyname($db, $key, $value) {
		$db->exec("INSERT OR IGNORE INTO keyname (`key`, `value`) VALUES (:key, :value)", [":key" => $key, ":value" => $value]);
	}

	// utilities

	// $str = utf8_encode($str);
	// $str = iconv('UTF-8', 'ASCII//TRANSLIT', $str);
	// https://www.wikiwand.com/zh-tw/%E6%B1%89%E8%AF%AD%E6%8B%BC%E9%9F%B3
	static function stripAccents($str) {
		$search = explode(",","ā,ɑ̄,ē,ī,ō,ū,ǖ,Ā,Ē,Ī,Ō,Ū,Ǖ,á,ɑ́,é,í,ó,ú,ǘ,Á,É,Í,Ó,Ú,Ǘ,ǎ,ɑ̌,ě,ǐ,ǒ,ǔ,ǚ,Ǎ,Ě,Ǐ,Ǒ,Ǔ,Ǚ,à,ɑ̀,è,ì,ò,ù,ǜ,À,È,Ì,Ò,Ù,Ǜ,a,ɑ,e,i,o,u,ü,A,E,I,O,U,Ü");
		$replace = explode(",","a,a,e,i,o,u,u,A,E,I,O,U,U,a,a,e,i,o,u,u,A,E,I,O,U,U,a,a,e,i,o,u,u,A,E,I,O,U,U,a,a,e,i,o,u,u,A,E,I,O,U,U,a,a,e,i,o,u,u,A,E,I,O,U,U");
		return str_replace($search, $replace, $str);
	}

	static function unicodeBlock($string) {
		$type = "";
		$value = utf8_hex_to_int(utf8_chr_to_hex($string));

		// Private Use Area Basic Multilingual Plane (U+E000–U+F8FF)
		// Private Use Area Supplementary Private Use Area-A: U+F0000–U+FFFFD
		// Private Use Area Supplementary Private Use Area-B: U+100000–U+10FFFD
		// CJK Unified Ideographs Extension B, U+20000 to U+2A6DF

		if ($value >= utf8_hex_to_int("U+E000") && $value <= utf8_hex_to_int("U+F8FF") ) {
			$type = "BMP";
		}
		else if ($value >= utf8_hex_to_int("U+F0000") && $value <= utf8_hex_to_int("U+FFFFD") ) {
			$type = "SPUA-A";
		}
		else if ($value >= utf8_hex_to_int("U+100000") && $value <= utf8_hex_to_int("U+10FFFD") ) {
			$type = "SPUA-B";
		}
		else if ($value >= utf8_hex_to_int("U+3400") && $value <= utf8_hex_to_int("U+4DBF") ) {
			$type = "CJK-ExtA";
		}
		else if ($value >= utf8_hex_to_int("U+20000") && $value <= utf8_hex_to_int("U+2A6DF") ) {
			$type = "CJK-ExtB";
		}
		else if ($value >= utf8_hex_to_int("U+2A700") && $value <= utf8_hex_to_int("U+2B73F") ) {
			$type = "CJK-ExtC";
		}
		else if ($value >= utf8_hex_to_int("U+2B740") && $value <= utf8_hex_to_int("U+2B81F") ) {
			$type = "CJK-ExtD";
		}
		else if ($value >= utf8_hex_to_int("U+2B820") && $value <= utf8_hex_to_int("U+2CEAF") ) {
			$type = "CJK-ExtE";
		}
		else if ($value >= utf8_hex_to_int("U+2CEB0") && $value <= utf8_hex_to_int("U+2EBEF") ) {
			$type = "CJK-ExtF";
		}

		return $type;
	}

	private static function stripComments($string) {
		$pattern = '/(.*)(#.*)/';
		$replacement = '\1';
		return trim(preg_replace($pattern, $replacement, $string));
	}


	private static function diffTable($a, $b) {
		$result = [];
		$base = [];

		foreach ($a->data as $item) {
			$base[$item->value][] = $item->key;
		}
		ksort($base);

		foreach ($b->data as $item) {
			if (!isset($base[$item->value])) {
				// echo "{$item->value}: {$base[$item->value][0]}\n";
				$result[] = $item;
			}
		}

		return $result;
	}


	// interface

	private function tiny($src, $level = 0) {
		// echo "Tiny {$src} by level: {$level}\n";

		$chardefBegin = false;
		$contents = explode("\n", file_get_contents(self::$baseDir . $src));
		// $x = 0;

		foreach ($contents as $orig) {
			$orig = trim($orig);
			$content = trim(preg_replace('/#(.?)*/', '', $orig));
			if (empty($content)) {
				echo $orig . "\n";
				continue;
			}

			$content = preg_replace('/[ ]{2,}|[\t]/', ' ', $content);
			if (empty($content)) {
				echo $orig . "\n";
				continue;
			}

			$rows = mb_split('[[:space:]]', $content, 2);
			if (count($rows) != 2) {
				echo $orig . "\n";
				continue;
			}

			$key = trim($rows[0]);
			$value = trim($rows[1]);

			if ($key == '%chardef' && $value == 'begin') {
				$chardefBegin = true;
				echo $orig . "\n";
				continue;
			}

			if ($key == '%chardef' && $value == 'end') {
				$chardefBegin = false;
				echo $orig . "\n";
				continue;
			}

			if (!$chardefBegin) {
				echo $orig . "\n";
				continue;
			}

			$type = self::unicodeBlock($value);

			if ($level == 3) {
				if (strpos($type, 'CJK-Ext') !== false) {
					continue;
				}
			}
			else if ($level == 2) {
				if ($type == 'BMP' || $type == 'SPUA-A' || $type == 'SPUA-B') {
					continue;
				}
			}
			else if ($level == 1) {
				if (!($type == 'CJK-ExtA' || $type == '')) {
					continue;
				}
			}
			else {
				if ($type != '') {
					continue;
				}
			}

			echo $orig . "\n";
			// echo "{$key} = {$value} ({$type})\n";

			// if ($x >= 100) {
			// 	break;
			// }
			// $x++;

		}


	}


}

Builder::shared()::run();