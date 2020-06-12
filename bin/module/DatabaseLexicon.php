<?php
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
	$db->exec('vacuum;');
}

$json = ["version" => time(), "resources" => []];

$filenames = glob(self::$baseDir . 'lexicon/*.csv', GLOB_NOSORT);
natsort($filenames);

foreach ($filenames as $path) {
	$filename = basename($path);
	$output = self::$baseDir . "db/lexicon-{$filename}.db";
	// @unlink($output);

	$db = new Database($output);
	echo "{$filename} -> " . basename($output) . "...";

	if (!file_exists($output)) {
		createDatabase($db, $path);
		echo "[new]";
	}
	else {
		echo "[exists]";
	}

	$description = explode("\n", file_get_contents($path . ".txt"));
	if (empty($description)) {
		echo "{$filename} -> [txt missing]\n";
	}
	else {
		$name = array_shift($description);
		$description = trim(implode("\n", $description));
		$description .= "\n\n詞庫範例\n=======\n";

		$sql = "SELECT phrase, pinyin FROM lexicon, pinyin WHERE lexicon.pinyin_id = pinyin.rowid ORDER BY RANDOM() LIMIT 10";
		$result = $db->getAll($sql);
		foreach ($result as $row) {
			$description .= $row["phrase"] . " " . $row["pinyin"] . "\n";
		}

		$json["resources"][] = [
			"name" => $name,
			"db" => "db/lexicon-{$filename}.db",
			"description" => $description,
		];
	}


	$db->close();

	echo "\n";
}

$jsonPath = self::$baseDir . "Lexicon.json";
$f = fopen($jsonPath, "w") or die("Unable to create file.");
fwrite($f, json_encode($json, JSON_UNESCAPED_UNICODE));
fclose($f);
echo "...version: {$json['version']}\n\n";
