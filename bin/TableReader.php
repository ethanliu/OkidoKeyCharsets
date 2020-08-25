<?php
/**
 * CIN Table Reader
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 24 August, 2020
 * @package class
 */

Class Chardef {
	public $key = "";
	public $value = "";
	function __construct($key, $value) {
		$this->key = $key;
		$this->value = $value;
	}
}

Class TableReader {
	public $info = [];
	public $keynames = [];
	public $data = [];
	public $description = '';

	private $headerOnly = false;
	private $path = "";

	private $propertyNames = ["%selkey", "%ename", "%cname", "%tcname", "%scname", "%endkey", "%encoding"];
	private $mapNames = ["%keyname", "%chardef"];

	function __construct($path, $headerOnly = false) {
		$this->path = $path;
		$this->headerOnly = $headerOnly;
		$this->parse();
		// $this->description();
	}

	function description() {
		var_dump($this->description);
		var_dump($this->info);
		var_dump($this->keynames);
		var_dump($this->data);
	}

	function parse() {
		if (!file_exists($this->path)) {
			die("File Not Found.");
		}

		$section = '';
		$contents = explode("\n", file_get_contents($this->path));

		foreach ($contents as $line) {
			$_line = trim(preg_replace('/#(.?)*/', '', $line));
			if (empty($_line)) {
				if (empty($section)) {
					$_line = trim(str_replace(['#', '　'], '', $line));
					$this->description .= $_line . "\n";
				}
				continue;
			}

			$line = preg_replace('/[ ]{2,}|[\t]/', ' ', $_line);
			if (empty($line)) {
				continue;
			}

			$rows = mb_split('[[:space:]]', $line, 2);
			if (count($rows) != 2) {
				continue;
			}

			$key = trim($rows[0]);
			$value = trim($rows[1]);

			if (in_array($key, $this->propertyNames)) {
				$_key = str_replace('%', '', $key);
				// echo "info: {$_key} -> {$value}\n";
				$this->info[$_key] = $value;
			}
			else if (in_array($key, $this->mapNames)) {
				if ($value == 'begin') {
					if ($key == '%chardef' && $this->headerOnly) {
						// die("head only exit");
						return;
					}
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
					// self::addKeyname($db, $key, $value);
					// echo "{$section}: {$key} -> {$value}\n";
					$this->keynames[$key] = $value;
				}
				else if ($section == '%chardef') {
					// echo "{$section}: {$key} -> {$value}\n";
					// entry
					$this->data[] = new Chardef($key, $value);
				}
				else {
					// echo "Unknown section: {$line}\n";
				}
			}

			// exit;
		}

	}

}