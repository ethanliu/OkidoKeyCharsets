<?php
/**
 * Common functions
 *
 * @author Ethan Liu <***REMOVED***>
 * @copyright Creativecrap.com
 */



function sqlite_escape_string($string){
	return SQLite3::escapeString($string);
}


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
	$query = "INSERT INTO chardef{$suffix} (`char`) VALUES (?);";
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

function addKeyChar($db, $key_id, $char_id, $suffix = "") {
	if ($key_id < 1 || $char_id < 1) {
		return false;
	}

	$query = "INSERT INTO entry{$suffix} (`keydef{$suffix}_id`, `chardef_id`) VALUES (?, ?)";
	$st = $db->prepare($query);
	$st->bindParam(1, $key_id, SQLITE3_INTEGER);
	$st->bindParam(2, $char_id, SQLITE3_INTEGER);
	$st->execute();
}
