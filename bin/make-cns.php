<?php
/**
 * bpmf-cns builder
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com
 * @package default
 */


// https://www.cns11643.gov.tw/
// https://data.gov.tw/dataset/5961

// ---------------------------------------------------
// 「CNS_phonetic.txt」為全字庫的注音資料表格
// ---------------------------------------------------
// 第一個欄位：CNS字碼(字面-編碼)
// 第二個欄位：該CNS字碼的注音屬性(以注音符號表示)

// 「Unicode」資料夾中含3個對照表
// CNS2UNICODE_Unicode BMP.txt為CNS對Unicode 第0(BMP)字面的對照表
// CNS2UNICODE_Unicode 2.txt為CNS對Unicode 第2字面的對照表
// CNS2UNICODE_Unicode 15.txt為CNS對Unicode 第15字面的對照表
//
// 其中每個對照表
// 第一個欄位：CNS字碼(字面-編碼)
// 第二個欄位：Unicode碼位(16進位)，若是四位數則表示第0(BMP)字面，若是五位數則第一個數字表示第幾字面
// PS：欄位之間以 Tab 隔開
//

include __DIR__ . "/portable-utf8.php";

class Builder {
	var $cnsPhoneticPath = __DIR__ . "/../tmp/Open_Data/Properties/CNS_phonetic.txt";
	var $cnsUnicodeBmpPath = __DIR__ . "/../tmp/Open_Data/MapingTables/Unicode/CNS2UNICODE_Unicode BMP.txt";
	var $cnsUnicode2Path = __DIR__ . "/../tmp/Open_Data/MapingTables/Unicode/CNS2UNICODE_Unicode 2.txt";
	var $cnsUnicode15Path = __DIR__ . "/../tmp/Open_Data/MapingTables/Unicode/CNS2UNICODE_Unicode 15.txt";

	var $includeSymbol = false;

	var $orders = ["radical", "common", "1", "q", "a", "z", "2", "w", "s", "x", "3", "e", "d", "c", "4", "r", "f", "v", "5", "t", "g", "b", "6", "y", "h", "n", "7", "u", "j", "m", "8", "i", "k", ",", "9", "o", "l", ".", "0", "p", ";", "/", "-", "symbol"];

	var $symbols = [
		"。" => "`.",
		"，" => "`,",
		"、" => "`'",
		"；" => "`;",
		"：" => "`:",
		"「" => "`[2",
		"」" => "`]2",
		"『" => "`[3",
		"』" => "`]3",
		"（" => "`(",
		"）" => "`)",
		"？" => "`?",
		"！" => "`!",
		// "─" => "",
		"…" => "`-7",
		"《" => "`<3",
		"》" => "`>3",
		"〈" => "`<2",
		"〉" => "`>2",
		"．" => "`.5",
		"—" => "`-5",
		"～" => "`~",
	];

	function __construct() {
	}

	function main() {

		$commonWords = include __DIR__ . "/words-common.php";
		$keydef = $this->getKeydef();
		$version = date("Y/m/d H:i:s", time());

		$tmp = [];
		$tmp["common"] = [];
		$tmp["radical"] = [];
		$tmp["symbol"] = [];

		$data = "# version: {$version}
# 本注音表格資料來源取自全字庫中文標準交換碼 https://www.cns11643.gov.tw
# 不包含未能賦予注音的字元，如標點符號、日文、藏文等等字元，
# 並以字根、常用字，注音順序、符號 (若包含) 順序重新排序。
#
# 本資料「常用字」欄係指民國 71 年 9 月 1 日教育部公告的「常用國字標準字體表」所收錄之常用字。
# 如：一、丁、七、三、下、丈、上等等，共計 4808 個常用字。
#
%gen_inp
%ename\tPhoneticCNS
%cname\t全字庫注音
%selkey\t123456789
%endkey\t3467
%keyname begin
";

		foreach ($keydef as $key => $def) {
			$data .= "{$def}\t{$key}\n";
			$tmp["radical"][] = "{$def}\t{$key}";
		}
		$data .= "%keyname end\n%chardef begin\n";

		$phonetic = $this->getData(true);
		$table = $this->getData(false);

		foreach ($table as $code => $items) {
			foreach ($items as $char) {
				// echo "{$code}: {$char}\n";

				if (!isset($phonetic[$code])) {
					// $char .= "\t{$code}";
					if ($this->includeSymbol) {
						$tmp["symbol"][] = ",,\t{$char}";
					}
				}
				else {
					$isCommonWord = in_array($char, $commonWords) ? true : false;
					foreach ($phonetic[$code] as $bpmf) {
						$chardef = $this->toChardef($bpmf, $keydef);
						$key = $isCommonWord ? "common" : mb_substr($chardef, 0, 1);
						// if ($isCommonWord) {
						// 	echo "{$chardef}\t{$bpmf}\t{$char}\n";
						// }

						if (!isset($tmp[$key])) {
							$tmp[$key] = [];
						}

						// $char .= "\t{$code}";
						$tmp[$key][] = "{$chardef}\t{$char}";
					}
				}
			}

		}

		foreach ($this->orders as $key) {
			if (!isset($tmp[$key])) {
				continue;
			}
			sort($tmp[$key], SORT_NATURAL);
			$data .= implode("\n", $tmp[$key]) . "\n";
		}

		$data .= "%chardef end\n";
		echo $data;
	}

	function getData($phonetic = true) {

		$data = [];
		if ($phonetic) {
			$contents = explode("\n", file_get_contents($this->cnsPhoneticPath));
			foreach ($contents as $line) {
				$items = explode("\t", $line);
				$items[0] = trim($items[0]);
				$items[1] = trim($items[1]);

				if (strpos($items[1], "˙") === 0) {
					$items[1] = str_replace("˙", "", $items[1]) . "˙";
				}

				$data[$items[0]][] = $items[1];
				// $data[] = $items;
			}
		}
		else {
			$paths = [$this->cnsUnicodeBmpPath, $this->cnsUnicode2Path, $this->cnsUnicode15Path];
			foreach ($paths as $path) {
				$contents = explode("\n", file_get_contents($path));
				foreach ($contents as $line) {
					$items = explode("\t", $line);
					$items[0] = trim($items[0]);
					$items[1] = trim($items[1]);

					$items[1] = utf8_chr($items[1]);

					$data[$items[0]][] = $items[1];
				}
			}
		}

		return $data;
	}

	function getKeydef($suffix = "") {
		$data = [];

		// $suffix = "-hsu";

		$path = __DIR__ . "/../charset/bpmf{$suffix}.charset.json";
		$json = json_decode(file_get_contents($path), true);

		foreach ($json[0]["charsets"] as $row) {
			preg_match_all("/\[(.*?[^:])(:{1}(.*?|))?\]/", $row, $matches, PREG_SET_ORDER);
			foreach ($matches as $match) {
				if (!isset($match[3])) {
					continue;
				}
				$keys = mb_strlen($match[3]) > 1 ? utf8_split($match[3]) : [$match[3]];
				foreach ($keys as $key) {
					$data[$key] = strtolower($match[1]);
				}
			}
		}

		return $data;
	}

	function toChardef($bpmf = "", $chardef = []) {
		$keydef = "";
		$chars = utf8_split($bpmf);

		foreach ($chars as $char) {
			$keydef .= isset($chardef[$char]) ? $chardef[$char] : '';
		}

		return $keydef;
	}

}

$builder = new Builder();
$builder->main();