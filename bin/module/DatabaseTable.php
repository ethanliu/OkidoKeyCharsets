<?php
/**
 *
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 12 January, 2021
 * @package default
 */

echo "Generate Database\n\n";

// $charIgnoreMode = "s2t";
// $ignoreChars = self::loadTongwenDictionary($charIgnoreMode, "char");
// var_dump($ignoreChars);
$filenames = [];

if (empty($argv)) {
	// $filenames = glob(self::$baseDir . 'table/*.cin', GLOB_NOSORT);
	$filenames = glob(self::$baseDir . 'table/*.cin');
	// natsort($filenames);
}
else {
	foreach ($argv as $path) {
		if (file_exists($path)) {
			$filenames[] = $path;
		}
	}
}

foreach ($filenames as $path) {
	// $path = './DataTables/array30.cin';
	$filename = basename($path);
	if (in_array($filename, self::$excludeDatables)) {
		// echo "Exclude: {$filename}\n";
		continue;
	}

	$isArray = (strpos($filename, "array30") !== false) ? true : false;

	$output = self::$baseDir . "db/{$filename}.db";
	if (file_exists($output)) {
		echo "{$filename} -> [" . color("skipped", "gray") . "]\n";
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

	$table = new TableReader($path);
	$keydefRowId = 0;
	$chardefRowId = 0;

	$db->exec("BEGIN TRANSACTION");

	foreach ($table->info as $key => $value) {
		self::addInfo($db, $key, $value);
	}

	foreach ($table->keynames as $key => $value) {
		self::addKeyname($db, $key, $value);
	}

	foreach ($table->data as $item) {
		$key = trim($item->key);
		$value = trim($item->value);

		// if ($skipSC && in_array($value, $words)) {
		// 	// echo "skip: {$value}\n";
		// 	continue;
		// }

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

			$table = new TableReader($path);
			$keydefRowId = 0;
			$chardefRowId = 0;

			foreach ($table->data as $item) {
				$key = trim($item->key);
				$value = trim($item->value);

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

	echo "[" . color("updated", "green") . "]\n";
	// exit;
}


