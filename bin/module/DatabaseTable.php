<?php
echo "Generate Database\n\n";
$skipSC = false;
$words = [];
if ($skipSC) {
	$words = include(__DIR__ . "/ref/words-hans.php");
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
