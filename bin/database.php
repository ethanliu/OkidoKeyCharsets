<?php
/**
 * Database Interface
 *
 * @author Ethan Liu <ethan@creativecrap.com>
 * @copyright Creativecrap.com
 **/

define('DEBUG', 0);

class Database {
	var $db = null;

	public function __construct($path) {
		$this->db = new PDO("sqlite:" . $path);
		$this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	}

	public function close() {
		$this->db = null;
	}

	public function showError($error) {
		die($error);
		exit;
	}

	public function quote($string) {
		return $this->db->quote($string);
	}

	public function prepare($sql, $param = array()) {

		try {
			$stmt = $this->db->prepare($sql);
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		// bind value
		if (!empty($param)) {
			foreach ($param as $key => $value) {
				$stmt->bindValue($key, $value, PDO::PARAM_STR);
			}
		}

		return $stmt;
	}

	public function exec($sql, $param = array()) {
		try {
			$stmt = $this->prepare($sql, $param);
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		try {
			$stmt->execute();
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}
		return $stmt;
	}

	public function lastInsertId() {
		$id = $this->db->lastInsertId();
		return $id;
	}

	public function getOne($sql, $param = array()) {
		try {
			$stmt = $this->prepare($sql, $param);
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		try {
			$stmt->execute();
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		$result = $stmt->fetch();
		return $result[0];
	}

	public function getRow($sql, $param = array()) {
		try {
			$stmt = $this->prepare($sql, $param);
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		try {
			$stmt->execute();
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		$stmt->setFetchMode(PDO::FETCH_ASSOC);
		$result = $stmt->fetch(PDO::FETCH_ASSOC);
		return $result;
	}

	public function getAll($sql, $param = array()) {
		try {
			$stmt = $this->prepare($sql, $param);
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		try {
			$stmt->execute();
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}
		$stmt->setFetchMode(PDO::FETCH_ASSOC);
		$result = $stmt->fetchAll(PDO::FETCH_ASSOC);
		return $result;
	}

	public function getAssoc($sql, $param = array()) {
		try {
			$stmt = $this->prepare($sql, $param);
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		try {
			$stmt->execute();
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		//$result = $stmt->fetchAll(PDO::FETCH_COLUMN|PDO::FETCH_GROUP);
		$stmt->setFetchMode(PDO::FETCH_ASSOC);
		$result = $stmt->fetchAll(PDO::FETCH_ASSOC);

		// since FETCH_KEY_PAIR only support for 1 pair
		if (!empty($result)) {
			$rows = array();
			$keys = array_keys($result[0]);
			foreach ($result as $row) {
				$key = $row[$keys[0]];
				unset($row[$keys[0]]);
				if (count($row) > 1) {
					$rows[$key] = $row;
				}
				else {
					$rows[$key] = implode('', $row);
				}
			}
			$result = $rows;
		}

		return $result;
	}

	public function getOffset($sql, $param, $offset = 0, $limit = 25) {
		if (!is_array($param)) {
			if (isset($offset)) {
				$limit = $offset;
			}
			$offset = $param;
			$param = array();
		}

		$sql .= " LIMIT {$limit} OFFSET {$offset}";

		try {
			$stmt = $this->prepare($sql, $param);
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		try {
			$stmt->execute();
		}
		catch (PDOException $e) {
			$error = (DEBUG) ? $e->getMessage() : '';
			$this->showError($error);
		}

		$stmt->setFetchMode(PDO::FETCH_ASSOC);
		$result = $stmt->fetchAll(PDO::FETCH_ASSOC);
		return $result;
	}
}


