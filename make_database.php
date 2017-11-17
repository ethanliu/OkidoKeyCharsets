<?php
/**
 *
 *
 * @author Ethan Liu <ethan@creativecrap.com>
 * @copyright Creativecrap.com
 */

include dirname(__FILE__) . "/config.php";
include dirname(__FILE__) . "/functions.php";


$propertyNames = ["%selkey", "%ename", "%cname", "%tcname", "%scname", "%endkey", "%encoding"];
$mapNames = ["%keyname", "%chardef"];
$isArray = false;

$filenames = glob('./DataTables/*.cin', GLOB_NOSORT);
// $filenames = glob('./DataTables/array*.cin', GLOB_NOSORT);

foreach ($filenames as $path) {

	// $path = './DataTables/array30.cin';
	$filename = str_replace('./DataTables/', '', $path);
	if (in_array($filename, $excludeDatables)) {
		// echo "Exclude: {$filename}\n";
		continue;
	}

	if (strpos($filename, "array") !== false) {
		$isArray = true;
	}
	else {
		$isArray = false;
	}

	$output = "./Databases/{$filename}.db";
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

	echo "{$filename} -> {$output}...";

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

		if (in_array($key, $propertyNames)) {
			$query = "INSERT INTO info (`name`, `value`) VALUES (?, ?);";
			$st = $db->prepare($query);
			$_key = str_replace('%', '', $key);
			$st->bindParam(1, $_key, SQLITE3_TEXT);
			$st->bindParam(2, $value, SQLITE3_TEXT);
			$st->execute();
			// echo "\n{$query} {$_key} {$value}";
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
				$query = "INSERT INTO keyname (`key`, `value`) VALUES (?, ?);";
				$st = $db->prepare($query);
				$st->bindParam(1, $key, SQLITE3_TEXT);
				$st->bindParam(2, $value, SQLITE3_TEXT);
				@$st->execute();
				// echo "\n{$query} {$key} {$value}";
			}
			else if ($section == '%chardef') {
				$keydefRowId = getKeydefId($db, $key);

				if (!$keydefRowId) {
					addKeydef($db, $key);
					$keydefRowId = getKeydefId($db, $key);
				}

				$chardefRowId = getChardefId($db, $value);

				if (!$chardefRowId) {
					addChardef($db, $value);
					$chardefRowId = getChardefId($db, $value);
				}

				addKeyChar($db, $keydefRowId, $chardefRowId);
			}
			else {
				echo "Unknown section: {$line}\n";
			}
		}
	}

	$db->exec("COMMIT;");

	if ($isArray) {

		$keydefRowId = 0;
		$chardefRowId = 0;

		$db->exec("BEGIN TRANSACTION");

		foreach (['array-special.cin', 'array-shortcode.cin'] as $filename) {
			echo "{$filename}...";
			$path = './DataTables/' . $filename;
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

				$keydefRowId = getKeydefId($db, $key, $suffix);

				if (!$keydefRowId) {
					addKeydef($db, $key, $suffix);
					$keydefRowId = getKeydefId($db, $key, $suffix);
				}

				$chardefRowId = getChardefId($db, $value);

				if (!$chardefRowId) {
					addChardef($db, $value);
					$chardefRowId = getChardefId($db, $value);
				}

				addKeyChar($db, $keydefRowId, $chardefRowId, $suffix);

			}
		}

		$db->exec("COMMIT;");
	}

	$db->close();

	// $db->open();
	// $db->exec('vacuum;');

	echo "[done]\n";
	// exit;
}