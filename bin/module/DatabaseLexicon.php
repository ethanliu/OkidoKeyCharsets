<?php
/**
 *
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 12 January, 2021
 * @package default
 */

echo "Build Lexicon Database\n\n";

// load pronunciation
// $pronunciation = [];
// $contents = explode("\n", file_get_contents("lexicon/pronunciation.txt"));
// foreach ($contents as $row) {
// 	$items = explode("\t", $row);
// 	$phrase = isset($items[0]) ? trim($items[0]) : "";
// 	$pinyin = isset($items[1]) ? trim($items[1]) : "";
// 	if (empty($phrase) || empty($pinyin)) {
// 		continue;
// 	}
// 	$pronunciation[$phrase][] = strtolower($pinyin);
// }


function createDatabase($db, $path) {
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

		// if (isset($pronunciation[$phrase])) {
		// 	foreach ($pronunciation[$phrase] as $p) {
		// 		if (strcmp($pinyin, $p) !== 0) {
		// 			// echo "change: {$phrase} {$pinyin} -> {$p}\n";
		// 			$pinyin = $p;
		// 			break;
		// 		}
		// 	}
		// }

		if (!empty($pinyin)) {
			$db->exec("INSERT OR IGNORE INTO pinyin (pinyin) VALUES (:pinyin)", [":pinyin" => $pinyin]);
		}

		$pinyin_id = $db->getOne("SELECT rowid FROM pinyin WHERE pinyin = :pinyin", [":pinyin" => $pinyin]) ?? 0;
        $db->exec("INSERT OR IGNORE INTO lexicon (phrase, weight, pinyin_id) VALUES (:phrase, :weight, :pinyin_id)", [":phrase" => $phrase, ":weight" => $weight, ":pinyin_id" => $pinyin_id]);
	}

	$db->exec("COMMIT TRANSACTION");
	$db->exec('vacuum');

	$db->exec('CREATE UNIQUE INDEX pinyin_index ON pinyin (pinyin)');
	$db->exec('CREATE UNIQUE INDEX lexicon_index ON lexicon (phrase)');
}

$json = [
	"version" => date("YmdHis"),
	"resources" => [],
	"splits" => [],
];

$updateJsonFile = true;

if (empty($argv)) {
	$filenames = glob(self::$baseDir . 'lexicon/*.csv', GLOB_NOSORT);
	natsort($filenames);
}
else {
	$updateJsonFile = false;
	foreach ($argv as $path) {
		if (file_exists($path)) {
			$filenames[] = $path;
		}
	}
}

foreach ($filenames as $path) {
	$filename = basename($path);
	$output = self::$baseDir . "db/lexicon-{$filename}.db";
	// @unlink($output);

	echo "{$filename} -> " . basename($output) . "...";

	if (!file_exists($output)) {
		$db = new Database($output);
		createDatabase($db, $path);
		echo "[" . color("updated", "green") . "]";
	}
	else {
		$db = new Database($output);
		echo "[" . color("skipped", "gray") . "]";
	}

	if (!file_exists($path . ".txt")) {
		echo "{$filename} -> [txt missing]\n";
		continue;
	}

	$description = explode("\n", file_get_contents($path . ".txt"));
	if (empty($description)) {
		echo "{$filename} -> [" . color(".txt file missing", "red") . "]\n";
	}
	else {
		$name = array_shift($description);
		$description = trim(implode("\n", $description));
		$description .= "\n\n詞庫範例\n=======\n";

		$w = $db->getOne("SELECT MAX(weight) FROM lexicon");
		$cond = ($w > 0) ? " ORDER BY weight DESC LIMIT 100" : " ORDER BY RANDOM() LIMIT 10";

		// $sql = "SELECT phrase, pinyin FROM lexicon, pinyin WHERE lexicon.pinyin_id = pinyin.rowid ORDER BY RANDOM() LIMIT 10";
		$sql = "SELECT phrase, pinyin, weight FROM lexicon, pinyin WHERE lexicon.pinyin_id = pinyin.rowid" . $cond;
		$result = $db->getAll($sql);
		shuffle($result);
		$result = array_slice($result, 0, 10);
		usort($result, function($l, $r) {
			return $l["pinyin"] <=> $r["pinyin"];
		});
		// print_r($result);
		foreach ($result as $row) {
			$description .= $row["phrase"] . " " . $row["pinyin"] . "\n";
		}

		$item = [
			"name" => $name,
			"db" => "db/lexicon-{$filename}.db",
			"description" => $description,
		];

		$json["resources"][] = $item;

		// init splits
		// $json['splits'][$filename] = ["github" => 0, "gitee" => 0];
		$json['splits']["lexicon-{$filename}.db"] = [];
	}


	$db->close();

	echo "\n";
}

if ($updateJsonFile) {
	$jsonPath = self::$baseDir . "Lexicon.json";
	$f = fopen($jsonPath, "w") or die("Unable to create file.");
	fwrite($f, json_encode($json, JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT));
	fclose($f);
}

echo "...version: {$json['version']}\n\n";
