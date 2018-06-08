<?php
/**
 * builder command line
 *
 * @author Ethan Liu <ethan@creativecrap.com>
 * @copyright Creativecrap.com
 * @package default
 */

// error_reporting(0);
// ini_set("error_reporting", FALSE);

class Builder {
	private static $shared;
	private static $excludeDatables = [
		'array30_OkidoKey-big_0.75.cin',
		'array30.cin',
		'klingon.cin',
		'bpmf_punctuation.cin',
		'bpmf-symbol.cin',
		'bpmf-cns.cin',
		'CnsPhonetic2016-08_GCINv2.cin',
		'egyptian.cin',
		'esperanto.cin',
		'kk.cin',
		'kks.cin',
		'morse.cin',
		'telecode.cin',
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
		$argv = getopt("tdkx:");
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
				self::keyboardLayouts();
			}
			if (isset($argv['t'])) {
				$invalid = false;
				self::dataTables();
			}
			if (isset($argv['d'])) {
				$invalid = false;
				//isset($argv['s']
				self::databases();
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
	-d	Generate Databases

	-x[level]	Strip Unicode blocks (BMP, SPUA, CJK-Ext...)
			level 0: strip all blocks (default)
			level 1: strip all blocks except CJK-ExtA
			level 2: strip SPUA blocks
			level 3: strip CJK-Ext A~D blocks

";
		exit;
	}

	// database

	function getChardefId($db, $value, $suffix = "") {
		$query = "SELECT rowid FROM chardef{$suffix} WHERE char = ?";
		$st = $db->prepare($query);
		$st->bindParam(1, $value, SQLITE3_TEXT);
		$result = $st->execute();
		$rows = $result->fetchArray(SQLITE3_ASSOC);

		$id = ($rows && $rows["rowid"]) ? $rows["rowid"] : 0;
		return $id;
	}

	function getKeydefId($db, $value, $suffix = "") {
		$query = "SELECT rowid FROM keydef{$suffix} WHERE key = ?";
		$st = $db->prepare($query);
		$st->bindParam(1, $value, SQLITE3_TEXT);
		$result = $st->execute();
		$rows = $result->fetchArray(SQLITE3_ASSOC);

		$id = ($rows && $rows["rowid"]) ? $rows["rowid"] : 0;
		return $id;
	}

	function addChardef($db, $value, $suffix = "") {
		$query = "INSERT INTO chardef{$suffix} (`char`) VALUES (?)";
		$st = $db->prepare($query);
		$st->bindParam(1, $value, SQLITE3_TEXT);
		$st->execute();
	}

	function addKeydef($db, $value, $suffix = "") {
		$query = "INSERT INTO keydef{$suffix} (`key`) VALUES (?)";
		$st = $db->prepare($query);
		$st->bindParam(1, $value, SQLITE3_TEXT);
		$st->execute();
	}

	function addEntry($db, $key_id, $char_id, $suffix = "") {
		if ($key_id < 1 || $char_id < 1) {
			return false;
		}

		$query = "INSERT INTO entry{$suffix} (`keydef{$suffix}_id`, `chardef_id`) VALUES (?, ?)";
		$st = $db->prepare($query);
		$st->bindParam(1, $key_id, SQLITE3_INTEGER);
		$st->bindParam(2, $char_id, SQLITE3_INTEGER);
		$st->execute();
	}

	function addInfo($db, $name, $value) {
		$query = "INSERT OR IGNORE INTO info (`name`, `value`) VALUES (?, ?)";
		$st = $db->prepare($query);
		$st->bindParam(1, $name, SQLITE3_TEXT);
		$st->bindParam(2, $value, SQLITE3_TEXT);
		$st->execute();
		// echo "\n{$query} {$_key} {$value}";
	}

	function addKeyname($db, $key, $value) {
		$query = "INSERT OR IGNORE INTO keyname (`key`, `value`) VALUES (?, ?);";
		$st = $db->prepare($query);
		$st->bindParam(1, $key, SQLITE3_TEXT);
		$st->bindParam(2, $value, SQLITE3_TEXT);
		$st->execute();
		// echo "\n{$query} {$key} {$value}";
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

	function stripComments($string) {
		$pattern = '/(.*)(#.*)/';
		$replacement = '\1';
		return trim(preg_replace($pattern, $replacement, $string));
	}


	// interface

	private function keyboardLayouts() {
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

	private function dataTables() {
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

	private function databases($skipSC = false) {
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

			if (strpos($filename, "array") !== false) {
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

			try {
				$db = new SQLite3($output);
			} catch (Exception $e) {
				echo $e->getmessage();
				exit;
			}

			echo "{$filename} -> " . basename($output) . "...";

			$query = "CREATE TABLE info (`name` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '');";
			$db->exec($query);
			$query = "CREATE TABLE keyname (`key` CHAR(255) UNIQUE NOT NULL, `value` CHAR(255) default '');";
			$db->exec($query);
			$query = "CREATE TABLE keydef (`key` CHAR(255) UNIQUE NOT NULL);";
			$db->exec($query);
			$query = "CREATE TABLE chardef (`char` CHAR(255) UNIQUE NOT NULL);";
			$db->exec($query);
			$query = "CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL);";
			$db->exec($query);

			if ($isArray) {
				$query = "CREATE TABLE keydef_special (`key` CHAR(255) UNIQUE NOT NULL)";
				$db->exec($query);
				$query = "CREATE TABLE keydef_shortcode (`key` CHAR(255) UNIQUE NOT NULL)";
				$db->exec($query);
				$query = "CREATE TABLE entry_special (`keydef_special_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)";
				$db->exec($query);
				$query = "CREATE TABLE entry_shortcode (`keydef_shortcode_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)";
				$db->exec($query);
			}

			$db->exec("PRAGMA synchronous = OFF");
			$db->exec("PRAGMA journal_mode = MEMORY");

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