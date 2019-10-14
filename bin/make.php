<?php
/**
 * builder - cli
 *
 * @author Ethan Liu <ethan@creativecrap.com>
 * @copyright Creativecrap.com
 */

// error_reporting(0);
// ini_set("error_reporting", FALSE);

include __DIR__ . "/database.php";
include __DIR__ . "/EmojiReader.php";

class Builder {
	private static $shared;
	private static $excludeDatables = [
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
		'kk.cin',
		'klingon.cin',
		'simplex-ext.cin',
		'morse.cin',
		// 'telecode.cin',
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
		$argv = getopt("tdkmex:");
		// var_dump($argv);
		// var_dump($_SERVER['argv']);

		if (isset($argv['x'])) {
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
		else {
			$invalid = true;

			if (isset($argv['k'])) {
				$invalid = false;
				self::generateKeyboardLayouts();
			}
			if (isset($argv['t'])) {
				$invalid = false;
				self::generateDataTables();
			}
			if (isset($argv['d'])) {
				$invalid = false;
				self::buildTableDatabase();
			}
			if (isset($argv['m'])) {
				$invalid = false;
				self::buildLexiconDatabase();
			}
			if (isset($argv['e'])) {
				$invalid = false;
				self::buildEmojiDatabase();
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

OPTIONS:
	-k	Generate KeyboardLayouts.json
	-t	Generate DataTables.json
	-d	Build Data Table Databases
	-m	Build Lexicon Databases
	-e	Build Emoji Databases

	-x[level]	Strip Unicode blocks (BMP, SPUA, CJK-Ext...)
			level 0: strip all blocks (default)
			level 1: strip all blocks except CJK-ExtA
			level 2: strip SPUA blocks
			level 3: strip CJK-Ext A~D blocks

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

	function unicodeBlock($string) {
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


	// interface

	private static function generateKeyboardLayouts() {
		echo "Generate KeyboardLayouts.json\n\n";

		$destinationPath = self::$baseDir . "KeyboardLayouts.json";
		$charsetPaths = glob(self::$baseDir . 'charset/*.charset.json', GLOB_NOSORT);
		natsort($charsetPaths);

		$contents = array(
			'version' => date("YmdHis"),
			'charsets' => array(),
		);

		foreach ($charsetPaths as $path) {
			$charsets = json_decode(file_get_contents($path));
			$error = json_last_error();

			if ($error !== JSON_ERROR_NONE) {
				echo "Syntax error: {$path}\n";
				// continue;
				exit;
			}

			foreach ($charsets as $charset) {
				if (empty($charset) || empty($charset->name) || empty($charset->charsets)) {
					echo "Skipped, invalid json or charset structure: {$path}\n";
					continue;
				}
				// $names = array_map('strrev', array_reverse(explode('-', $charset->name, 2)));
				$name = $charset->name;
				if (isset($contents['charsets'][$name])) {
					echo "Skipped, charset already exists. {$path} [{$name}]\n";
					continue;
				}
				echo "{$charset->name}\n";
				unset($charset->name);
				$contents['charsets'][$name] = $charset;
			}
		}

		$f = fopen($destinationPath, "w") or die("Unable to create file.");
		fwrite($f, json_encode($contents, JSON_UNESCAPED_UNICODE));
		fclose($f);
		echo "...version: {$contents['version']}\n\n";
	}

	private static function generateDataTables() {
		echo "Generate DataTables.json\n\n";

		$destinationPath = self::$baseDir . "DataTables.json";
		$filenames = glob(self::$baseDir . 'table/*.cin', GLOB_NOSORT);
		natsort($filenames);

		$result = array(
			'version' => date("YmdHis"),
			'datatables' => [],
		);

		$items = [];

		foreach ($filenames as $path) {
			$filename = basename($path);
			if (in_array($filename, self::$excludeDatables)) {
				echo "Exclude: {$filename}\n";
				continue;
			}

			$beginKeyname = false;
			$keyname = '';
			$item = array(
				'ename' => '',
				'cname' => '',
				'name' => '',
				'cin' => "table/{$filename}",
				'db' => "db/{$filename}.db",
				'license' => '',
			);
			$contents = explode("\n", file_get_contents($path), 5000);

			foreach ($contents as $line) {
				$line = trim($line);
				$rows = explode(' ', str_replace("\t", " ", $line), 2);
				$key = trim($rows[0]);
				$value = count($rows) > 1 ? self::stripComments($rows[1]) : '';

				if ($key == '%chardef') {
					break;
				}
				else if (in_array($key, ['%ename', '%cname', '%name', '%tcname', '%scname'])) {
					$key = str_replace('%', '', $key);
					$item[$key] = $value;
				}
				else if ($key == '%keyname') {
					if ($value == 'begin') {
						$beginKeyname = true;
						continue;
					}
					else if ($value == 'end') {
						$beginKeyname = false;
						break;
					}
				}
				else {
					if ($beginKeyname) {
						$keyname .= trim($rows[0]);
					}
					else if (strpos($line, '%') === 0) {
						// echo "ignore: ". $line . "\n";
						continue;
					}
					else {
						$line = str_replace(['#', '　'], '', $line);
						$line = trim($line);
						$item['license'] .= $line . "\n";
					}
				}
			}

			if (!empty($keyname)) {
				$result['datatables'][] = $item;
				echo "Add: {$filename} -> {$item['ename']} {$item['cname']}\n";
			}
			else {
				echo "Ignore: {$filename}\n";
			}
		}

		$f = fopen($destinationPath, "w") or die("Unable to create file.");
		fwrite($f, json_encode($result, JSON_UNESCAPED_UNICODE));
		fclose($f);
		echo "...version: {$result['version']}\n\n";

	}

	private static function buildTableDatabase($skipSC = false) {
		echo "Generate Database\n\n";
		// $skipSC = true;
		$words = [];
		if ($skipSC) {
			$words = include(dirname(__FILE__) . "/words.php");
		}

		$propertyNames = ["%selkey", "%ename", "%cname", "%tcname", "%scname", "%endkey", "%encoding"];
		$mapNames = ["%keyname", "%chardef"];
		$isArray = false;

		$filenames = glob(self::$baseDir . 'table/*.cin', GLOB_NOSORT);
		// $filenames = glob('./DataTables/array*.cin', GLOB_NOSORT);

		foreach ($filenames as $path) {

			// $path = './DataTables/array30.cin';
			$filename = basename($path);
			if (in_array($filename, self::$excludeDatables)) {
				// echo "Exclude: {$filename}\n";
				continue;
			}

			if (strpos($filename, "array30") !== false) {
				$isArray = true;
			}
			else {
				$isArray = false;
			}

			$output = self::$baseDir . "db/{$filename}.db";
			if (file_exists($output)) {
				echo "{$filename} -> [exists]\n";
				continue;
			}
			// @unlink($output);

			$db = new Database($output);
			$db->exec("PRAGMA synchronous = OFF");
			$db->exec("PRAGMA journal_mode = MEMORY");

			echo "{$filename} -> " . basename($output) . "...";

			$db->exec("CREATE TABLE info (`name` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')");
			$db->exec("CREATE TABLE keyname (`key` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '')");
			$db->exec("CREATE TABLE keydef (`key` CHAR(255) UNIQUE NOT NULL)");
			$db->exec("CREATE TABLE chardef (`char` CHAR(255) UNIQUE NOT NULL)");
			$db->exec("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)");

			if ($isArray) {
				$db->exec("CREATE TABLE keydef_special (`key` CHAR(255) UNIQUE NOT NULL)");
				$db->exec("CREATE TABLE keydef_shortcode (`key` CHAR(255) UNIQUE NOT NULL)");
				$db->exec("CREATE TABLE entry_special (`keydef_special_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)");
				$db->exec("CREATE TABLE entry_shortcode (`keydef_shortcode_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)");
			}

			$section = '';
			$contents = explode("\n", file_get_contents($path));

			$keydefRowId = 0;
			$chardefRowId = 0;

			$db->exec("BEGIN TRANSACTION");

			foreach ($contents as $line) {
				$line = trim(preg_replace('/#(.?)*/', '', $line));

				if (empty($line)) {
					continue;
				}

				// echo "{$line}\n";


				$line = preg_replace('/[ ]{2,}|[\t]/', ' ', $line);
				if (empty($line)) {
					continue;
				}

				// $rows = explode(' ', str_replace("\t", " ", $line), 2);
				// $rows = explode(' ', $line, 2);
				$rows = mb_split('[[:space:]]', $line, 2);
				if (count($rows) != 2) {
					continue;
				}

				$key = trim($rows[0]);
				$value = trim($rows[1]);

				if ($skipSC && in_array($value, $words)) {
					// echo "skip: {$value}\n";
					continue;
				}

				if (in_array($key, $propertyNames)) {
					$_key = str_replace('%', '', $key);
					self::addInfo($db, $_key, $value);
				}
				else if (in_array($key, $mapNames)) {
					if ($value == 'begin') {
						$section = $key;
						continue;
					}
					else if ($value == 'end') {
						if ($section == $key) {
							$secton = '';
							// echo "section: {$section} end\n";
						}
						else {
							echo "section: end of {$section}???\n";
						}
					}
				}
				else {
					if ($section == '%keyname') {
						self::addKeyname($db, $key, $value);
					}
					else if ($section == '%chardef') {
						$keydefRowId = self::getKeydefId($db, $key);

						if (!$keydefRowId) {
							self::addKeydef($db, $key);
							$keydefRowId = self::getKeydefId($db, $key);
						}

						$chardefRowId = self::getChardefId($db, $value);

						if (!$chardefRowId) {
							self::addChardef($db, $value);
							$chardefRowId = self::getChardefId($db, $value);
						}

						self::addEntry($db, $keydefRowId, $chardefRowId);
					}
					else {
						// echo "Unknown section: {$line}\n";
					}
				}
			}

			$db->exec("COMMIT TRANSACTION");

			// $query = "CREATE INDEX keydef_keys ON keydef (key)";
			// $db->exec($query);
			// $query = "CREATE INDEX chardef_chars ON chardef (char)";
			// $db->exec($query);
			// $query = "CREATE INDEX entry_index ON entry (keydef_id, chardef_id)";
			// $db->exec($query);
			// $query = "CREATE INDEX entry_keydefs ON entry (keydef_id)";
			// $db->exec($query);
			// $query = "CREATE INDEX entry_chardefs ON entry (chardef_id)";
			// $db->exec($query);

			if ($isArray) {

				$keydefRowId = 0;
				$chardefRowId = 0;

				$db->exec("BEGIN TRANSACTION");

				foreach (['array-special.cin', 'array-shortcode.cin'] as $filename) {
					echo "{$filename}...";
					$path = self::$baseDir . 'table/' . $filename;
					$suffix = '_' . str_replace(['array-', '.cin'], '', $filename);
					$section = '';
					$contents = explode("\n", file_get_contents($path));

					$keydefRowId = 0;
					$chardefRowId = 0;
					$valid = false;

					foreach ($contents as $line) {
						$line = trim(preg_replace('/#(.?)*/', '', $line));
						if (empty($line)) {
							continue;
						}

						$line = preg_replace('/[ ]{2,}|[\t]/', ' ', $line);
						if (empty($line)) {
							continue;
						}

						// $rows = explode(' ', str_replace("\t", " ", $line), 2);
						// $rows = explode(' ', $line, 2);
						$rows = mb_split('[[:space:]]', $line, 2);
						if (count($rows) != 2) {
							continue;
						}

						$key = trim($rows[0]);
						$value = trim($rows[1]);

						if ($key == '%chardef' && $value == 'begin') {
							$valid = true;
							continue;
						}

						if ($key == '%chardef' && $value == 'end') {
							$valid = false;
							continue;
						}

						if (!$valid) {
							continue;
						}

						// echo "{$key} = {$value}\n";

						$keydefRowId = self::getKeydefId($db, $key, $suffix);

						if (!$keydefRowId) {
							self::addKeydef($db, $key, $suffix);
							$keydefRowId = self::getKeydefId($db, $key, $suffix);
						}

						$chardefRowId = self::getChardefId($db, $value);

						if (!$chardefRowId) {
							self::addChardef($db, $value);
							$chardefRowId = self::getChardefId($db, $value);
						}

						self::addEntry($db, $keydefRowId, $chardefRowId, $suffix);

					}
				}

				$db->exec("COMMIT TRANSACTION");
			}

			$db->exec('vacuum;');
			$db->close();

			// $db->open();

			echo "[done]\n";
			// exit;
		}

		echo "\n";
	}

	private static function buildLexiconDatabase() {
		echo "Build Lexicon Database\n\n";

		// load pronunciation
		$pronunciation = [];
		$contents = explode("\n", file_get_contents("lexicon/pronunciation.txt"));
		foreach ($contents as $row) {
			$items = explode("\t", $row);
			$phrase = isset($items[0]) ? trim($items[0]) : "";
			$pinyin = isset($items[1]) ? trim($items[1]) : "";
			if (empty($phrase) || empty($pinyin)) {
				continue;
			}
			$pronunciation[$phrase][] = strtolower($pinyin);
		}

		$filenames = glob(self::$baseDir . 'lexicon/*.csv', GLOB_NOSORT);
		foreach ($filenames as $path) {
			$filename = basename($path);
			$output = self::$baseDir . "db/lexicon-{$filename}.db";
			// @unlink($output);
			if (file_exists($output)) {
				echo "{$filename} -> [exists]\n";
				continue;
			}

			echo "{$filename} -> " . basename($output) . "...";

			$db = new Database($output);
			$db->exec("PRAGMA synchronous = OFF");
			$db->exec("PRAGMA journal_mode = MEMORY");

	        $db->exec("CREATE TABLE IF NOT EXISTS pinyin (`pinyin` CHAR(255) UNIQUE NOT NULL)");
	        $db->exec("CREATE TABLE IF NOT EXISTS lexicon (`phrase` CHAR(255) UNIQUE NOT NULL, `pinyin_id` INTEGER NOT NULL, `weight` INTEGER DEFAULT 0)");

			$db->exec("BEGIN TRANSACTION");

			$contents = explode("\n", file_get_contents($path));
			foreach ($contents as $row) {
				$items = explode("\t", $row);
				$phrase = isset($items[0]) ? trim($items[0]) : "";
				$weight = isset($items[1]) ? intval($items[1]) : 0;
				$pinyin = isset($items[2]) ? trim($items[2]) : "";
				$pinyin_id = 0;

				if (mb_strlen($phrase) <= 1) {
					// echo "[ignore_short] {$phrase}\n";
					continue;
				}

				if (isset($pronunciation[$phrase])) {
					foreach ($pronunciation[$phrase] as $p) {
						if (strcmp($pinyin, $p) !== 0) {
							// echo "change: {$phrase} {$pinyin} -> {$p}\n";
							$pinyin = $p;
							break;
						}
					}
				}


				if (!empty($pinyin)) {
					$db->exec("INSERT OR IGNORE INTO pinyin (pinyin) VALUES (:pinyin)", [":pinyin" => $pinyin]);
				}

				$pinyin_id = $db->getOne("SELECT rowid FROM pinyin WHERE pinyin = :pinyin", [":pinyin" => $pinyin]) ?? 0;
	            $db->exec("INSERT OR IGNORE INTO lexicon (phrase, weight, pinyin_id) VALUES (:phrase, :weight, :pinyin_id)", [":phrase" => $phrase, ":weight" => $weight, ":pinyin_id" => $pinyin_id]);
			}

			$db->exec("COMMIT TRANSACTION");
			$db->exec('vacuum;');
			$db->close();

			echo "[done]\n";
		}

		echo "\n";
	}

	private static function buildEmojiDatabase() {
		echo "Build Emoji Database\n\n";
		// pull
		$url = "https://unicode.org/emoji/charts/emoji-list.html";

		if (!file_exists(self::$baseDir . "/tmp/emoji-list.txt")) {
			$contents = file_get_contents($url);
			$contents = strip_tags($contents);
			file_put_contents(self::$baseDir . "/tmp/emoji-list.txt", $contents);
		}

		$reader = new Reader();
		$reader->listPath = self::$baseDir . "/tmp/emoji-list.txt";
		// $reader->jsonPath = self::$baseDir . "/tmp/emoji-list.json";
		$reader->dbPath = self::$baseDir . "/tmp/emoji.db";
		// $reader->test = 100;
		$reader->parse();
		$reader->build();

		echo "[done]\n\n";
	}


	private function tiny($src, $level = 0) {
		include_once dirname(__FILE__) . "/portable-utf8.php";
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