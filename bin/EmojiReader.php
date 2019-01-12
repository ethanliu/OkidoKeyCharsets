<?php
/**
 * Extract emoji from https://unicode.org/emoji/charts/emoji-list.html and convert to SQLite or json
 *
 * @author Ethan Liu <ethan@creativecrap.com>
 * @copyright Creativecrap.com
 */

// if (PHP_SAPI !== "cli") {
// 	die("");
// }

// include_once "./gat.php";
// use \Statickidz\GoogleTranslate;

include_once __DIR__ . "/database.php";

Class Reader {

	// public $test = 100;
	public $test = -1;
	public $listPath = "";
	public $jsonPath = "";
	public $dbPath = "";

	private $data = [];
	private $words = [];

	function __construct() {
		$this->getWords();
	}

	private function chr_utf8($n, $f = 'C*'){
		return $n<(1<<7)?chr($n):($n<1<<11?pack($f,192|$n>>6,1<<7|191&$n):
		($n<(1<<16)?pack($f,224|$n>>12,1<<7|63&$n>>6,1<<7|63&$n):
		($n<(1<<20|1<<16)?pack($f,240|$n>>18,1<<7|63&$n>>12,1<<7|63&$n>>6,1<<7|63&$n):'')));
	}

	private function emoji($value) {
		return $this->chr_utf8(hexdec(ltrim($value, 'U+')));
	}

	// private function _t($text, $target = 'zh_TW') {
	//
	// 	$source = 'en';
	// 	// $target = 'zh_TW';
	// 	// $target = 'zh_CN';
	// 	// $text = 'test';
	//
	// 	$trans = new GoogleTranslate();
	// 	$result = $trans->translate($source, $target, $text);
	//
	// 	// echo $result . "\n";
	// 	return $result;
	// }

	// database

	function getChardefId($db, $value) {
		return $db->getOne("SELECT rowid FROM chardef WHERE char = :value", [":value" => $value]) ?? 0;
	}

	function getKeydefId($db, $value) {
		return $db->getOne("SELECT rowid FROM keydef WHERE key = :value", [":value" => $value]) ?? 0;
	}

	function addChardef($db, $value) {
		$db->exec("INSERT INTO chardef (`char`) VALUES (:value)", [":value" => $value]);
	}

	function addKeydef($db, $value) {
		$db->exec("INSERT INTO keydef (`key`) VALUES (:value)", [":value" => $value]);
	}

	function addKeyChar($db, $key_id, $char_id) {
		$db->exec("INSERT INTO entry (`keydef_id`, `chardef_id`) VALUES (:k, :c)", [":k" => $key_id, ":c" => $char_id]);
	}

	// interface

	function build() {
		if (empty($this->dbPath)) {
			return false;
		}

		// $json = json_decode(file_get_contents($this->jsonPath));
		// if (empty($json)) {
		// 	return false;
		// }
		$json = $this->data;

		@unlink($this->dbPath);

		$db = new Database($this->dbPath);
		$db->exec("PRAGMA synchronous = OFF");
		$db->exec("PRAGMA journal_mode = MEMORY");

		$db->exec("CREATE TABLE keydef (`key` CHAR(255) UNIQUE NOT NULL)");
		$db->exec("CREATE TABLE chardef (`char` CHAR(255) UNIQUE NOT NULL)");
		$db->exec("CREATE TABLE entry (`keydef_id` INTEGER NOT NULL, `chardef_id` INTEGER NOT NULL)");

		$db->exec("BEGIN TRANSACTION");

		foreach ($json as $unicode => $keywords) {
			// echo $unicode . "\n";
			$chardef_id = 0;
			$keydef_id = 0;
			$chardef_id = $this->getChardefId($db, $unicode);

			if (!$chardef_id) {
				$this->addChardef($db, $unicode);
				$chardef_id = $this->getChardefId($db, $unicode);
			}

			foreach ($keywords as $keyword) {
				// echo $keyword . "\n";
				$keydef_id = $this->getKeydefId($db, $keyword);
				if (!$keydef_id) {
					$this->addKeydef($db, $keyword);
					$keydef_id = $this->getKeydefId($db, $keyword);
				}
				$this->addKeyChar($db, $keydef_id, $chardef_id);
			}
		}

		$db->exec("COMMIT TRANSACTION");

		$db->exec('vacuum;');
		$db->close();
	}


	function parse() {
		$contents = file_get_contents($this->listPath);
		$pattern = '/^(\d+)\n(.*)\n\n(.*)\n(.*)/m';
		preg_match_all($pattern, $contents, $matches, PREG_SET_ORDER, 0);

		$accents = array('À', 'Á', 'Â', 'Ã', 'Ä', 'Å', 'Æ', 'Ç', 'È', 'É', 'Ê', 'Ë', 'Ì', 'Í', 'Î', 'Ï', 'Ð', 'Ñ', 'Ò', 'Ó', 'Ô', 'Õ', 'Ö', 'Ø', 'Ù', 'Ú', 'Û', 'Ü', 'Ý', 'ß', 'à', 'á', 'â', 'ã', 'ä', 'å', 'æ', 'ç', 'è', 'é', 'ê', 'ë', 'ì', 'í', 'î', 'ï', 'ñ', 'ò', 'ó', 'ô', 'õ', 'ö', 'ø', 'ù', 'ú', 'û', 'ü', 'ý', 'ÿ', 'Ā', 'ā', 'Ă', 'ă', 'Ą', 'ą', 'Ć', 'ć', 'Ĉ', 'ĉ', 'Ċ', 'ċ', 'Č', 'č', 'Ď', 'ď', 'Đ', 'đ', 'Ē', 'ē', 'Ĕ', 'ĕ', 'Ė', 'ė', 'Ę', 'ę', 'Ě', 'ě', 'Ĝ', 'ĝ', 'Ğ', 'ğ', 'Ġ', 'ġ', 'Ģ', 'ģ', 'Ĥ', 'ĥ', 'Ħ', 'ħ', 'Ĩ', 'ĩ', 'Ī', 'ī', 'Ĭ', 'ĭ', 'Į', 'į', 'İ', 'ı', 'Ĳ', 'ĳ', 'Ĵ', 'ĵ', 'Ķ', 'ķ', 'Ĺ', 'ĺ', 'Ļ', 'ļ', 'Ľ', 'ľ', 'Ŀ', 'ŀ', 'Ł', 'ł', 'Ń', 'ń', 'Ņ', 'ņ', 'Ň', 'ň', 'ŉ', 'Ō', 'ō', 'Ŏ', 'ŏ', 'Ő', 'ő', 'Œ', 'œ', 'Ŕ', 'ŕ', 'Ŗ', 'ŗ', 'Ř', 'ř', 'Ś', 'ś', 'Ŝ', 'ŝ', 'Ş', 'ş', 'Š', 'š', 'Ţ', 'ţ', 'Ť', 'ť', 'Ŧ', 'ŧ', 'Ũ', 'ũ', 'Ū', 'ū', 'Ŭ', 'ŭ', 'Ů', 'ů', 'Ű', 'ű', 'Ų', 'ų', 'Ŵ', 'ŵ', 'Ŷ', 'ŷ', 'Ÿ', 'Ź', 'ź', 'Ż', 'ż', 'Ž', 'ž', 'ſ', 'ƒ', 'Ơ', 'ơ', 'Ư', 'ư', 'Ǎ', 'ǎ', 'Ǐ', 'ǐ', 'Ǒ', 'ǒ', 'Ǔ', 'ǔ', 'Ǖ', 'ǖ', 'Ǘ', 'ǘ', 'Ǚ', 'ǚ', 'Ǜ', 'ǜ', 'Ǻ', 'ǻ', 'Ǽ', 'ǽ', 'Ǿ', 'ǿ', 'Ά', 'ά', 'Έ', 'έ', 'Ό', 'ό', 'Ώ', 'ώ', 'Ί', 'ί', 'ϊ', 'ΐ', 'Ύ', 'ύ', 'ϋ', 'ΰ', 'Ή', 'ή');
		$regular = array('A', 'A', 'A', 'A', 'A', 'A', 'AE', 'C', 'E', 'E', 'E', 'E', 'I', 'I', 'I', 'I', 'D', 'N', 'O', 'O', 'O', 'O', 'O', 'O', 'U', 'U', 'U', 'U', 'Y', 's', 'a', 'a', 'a', 'a', 'a', 'a', 'ae', 'c', 'e', 'e', 'e', 'e', 'i', 'i', 'i', 'i', 'n', 'o', 'o', 'o', 'o', 'o', 'o', 'u', 'u', 'u', 'u', 'y', 'y', 'A', 'a', 'A', 'a', 'A', 'a', 'C', 'c', 'C', 'c', 'C', 'c', 'C', 'c', 'D', 'd', 'D', 'd', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'E', 'e', 'G', 'g', 'G', 'g', 'G', 'g', 'G', 'g', 'H', 'h', 'H', 'h', 'I', 'i', 'I', 'i', 'I', 'i', 'I', 'i', 'I', 'i', 'IJ', 'ij', 'J', 'j', 'K', 'k', 'L', 'l', 'L', 'l', 'L', 'l', 'L', 'l', 'l', 'l', 'N', 'n', 'N', 'n', 'N', 'n', 'n', 'O', 'o', 'O', 'o', 'O', 'o', 'OE', 'oe', 'R', 'r', 'R', 'r', 'R', 'r', 'S', 's', 'S', 's', 'S', 's', 'S', 's', 'T', 't', 'T', 't', 'T', 't', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'W', 'w', 'Y', 'y', 'Y', 'Z', 'z', 'Z', 'z', 'Z', 'z', 's', 'f', 'O', 'o', 'U', 'u', 'A', 'a', 'I', 'i', 'O', 'o', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'U', 'u', 'A', 'a', 'AE', 'ae', 'O', 'o', 'Α', 'α', 'Ε', 'ε', 'Ο', 'ο', 'Ω', 'ω', 'Ι', 'ι', 'ι', 'ι', 'Υ', 'υ', 'υ', 'υ', 'Η', 'η');

		foreach ($matches as $match) {

			if ($this->test > 0) {
				$this->test--;
				if ($this->test === 0) {
					break;
				}
			}

			// $serial = intval($match[1]);
			// $unicodes = explode(' ', str_replace("U+", "\u", $match[2]));
			// $unicodes = explode(' ', str_replace("U+", "", $match[2]));
			$unicodes = str_replace("U+", "", $match[2]);
			// $unicodes = $this->emoji($unicodes);
			$longName = trim($match[3]);
			// $shortNames = array_unique(explode('|', str_replace(["“", "”"], "" , $match[4])));

			$shortNames = explode("|", $match[4]);
			$shortNames = array_values(array_unique(array_filter(array_map(function($value) use ($accents, $regular) {
				$value = trim(str_replace(["“", "”", "’"], ["", "", "'"], $value));
				if (strpos($value, ' ')) {
					return null;
				}
				// $value2 = iconv('UTF-8', 'ISO-8859-1//TRANSLIT//IGNORE', $value);
				$value2 = str_replace($accents, $regular, $value);
				// echo "{$value} => {$value2}\n";
				return $value2;
			}, $shortNames))));

			$this->data[$unicodes] = $shortNames;

			foreach ($shortNames as $name) {
				if (isset($this->words[$name])) {
					$this->data[$unicodes] = array_merge($this->data[$unicodes], $this->words[$name]);
				}
			}

			$this->data[$unicodes] = array_values(array_unique($this->data[$unicodes]));

			// $this->words = array_merge($this->words, $shortNames);
			// echo "{$unicodes} > " . implode(", ", $shortNames) . "\n";
			// if (count($unicodes) > 1) {
			// 	// ignore sequences
			// 	continue;
			// }

			// $value = "";
			// foreach ($unicodes as $unicode) {
			// 	$value = "\\u{" . $unicode . "}";
			// }
		}

		// $this->words = array_values(array_unique($this->words, SORT_STRING));
		// asort($this->words, SORT_NATURAL);
	}

	function json() {
		return json_encode($this->data, JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE);
	}

	function words() {
		return $this->words;
	}

	function getWords() {
		$path = __DIR__ . "/emoji-words.txt";
		$contents = explode("\n", file_get_contents($path));
		foreach ($contents as $line) {
			$line = preg_replace('/\s+/', "\t", $line);
			$items = explode("\t", $line);
			$key = array_shift($items);
			// var_dump($items);
			$this->words[$key] = $items;
		}

		// var_dump($this->words);
		// exit;
	}

}
