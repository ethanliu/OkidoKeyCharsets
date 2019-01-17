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
	var $openDataBasePath = __DIR__ . "/../tmp/Open_Data/";

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

		$keydef = $this->getKeydef();
		$version = date("Y/m/d H:i:s", time());

		$tmp = [];
		$data = "# version: {$version}
# 本注音表格資料來源取自全字庫中文標準交換碼 https://www.cns11643.gov.tw
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
					// $tmp["symbol"][] = ",,\t{$char}";
				}
				else {
					// var_dump($phonetic[$code]);exit;
					foreach ($phonetic[$code] as $bpmf) {
						$chardef = $this->toChardef($bpmf, $keydef);
						$key = mb_substr($chardef, 0, 1);

						if (!isset($tmp[$key])) {
							$tmp[$key] = [];
						}

						// $char .= "\t{$code}";
						$tmp[$key][] = "{$chardef}\t{$char}";
					}
				}
			}

			// if ($code == "3-313A") {
			// 	echo "fin";
			// 	// exit;
			// 	break;
			// }
		}

		$orders = ["radical", "1", "q", "a", "z", "2", "w", "s", "x", "3", "e", "d", "c", "4", "r", "f", "v", "5", "t", "g", "b", "6", "y", "h", "n", "7", "u", "j", "m", "8", "i", "k", ",", "9", "o", "l", ".", "0", "p", ";", "/", "-", "symbol"];

		foreach ($orders as $key) {
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
		$cnsPhoneticPath = $this->openDataBasePath . "Properties/CNS_phonetic.txt";
		$cnsUnicodeBmpPath = $this->openDataBasePath . "MapingTables/Unicode/CNS2UNICODE_Unicode BMP.txt";
		$cnsUnicode2Path = $this->openDataBasePath . "MapingTables/Unicode/CNS2UNICODE_Unicode 2.txt";
		$cnsUnicode15Path = $this->openDataBasePath . "MapingTables/Unicode/CNS2UNICODE_Unicode 15.txt";

		$data = [];
		if ($phonetic) {
			$contents = explode("\n", file_get_contents($cnsPhoneticPath));
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
			$paths = [$cnsUnicodeBmpPath, $cnsUnicode2Path, $cnsUnicode15Path];
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