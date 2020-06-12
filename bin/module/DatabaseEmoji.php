<?php
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
