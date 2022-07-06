<?php
/**
 * array30
 * https://github.com/gontera/array30
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 27 September, 2021
 * @package module
 */


$mode = $mode ?? '';
if ($mode == 'phrase') {
	parsePhrase($srcPath);
}
else {
	cloneFiles($rootPath, $srcPath);
}

function parsePhrase($srcPath) {
	$raw = explode("\n", file_get_contents($srcPath));

	foreach ($raw as $line) {
		$line = trim($line);
		// $row = explode(" ", $line);
		$row = preg_split('/\s+/', $line);

		$pinyin = array_shift($row) ?? "";
		$phrase = array_shift($row) ?? "";
		$weight = 0;

		if (empty($phrase)) {
			continue;
		}

		echo $phrase . "\t" . $weight . "\t" . $pinyin . "\n";
	}
}


// echo $srcPath;
// echo $rootPath;

function cloneFiles($rootPath, $srcPath) {

	$files = glob($srcPath . '/*/*.cin', GLOB_NOSORT);
	// natsort($filenames);

	$dir = $srcPath . '/OpenVanilla/';
	$files = glob($dir . '*.cin', GLOB_NOSORT);
	foreach ($files as $path) {
		// $filename = str_replace($dir, '', $path);
		if (strpos($path, 'special') !== false) {
			$from = str_replace($srcPath, '', $path);
			$to = "table/array-special.cin";
			if (copy($path, $rootPath . '/' . $to)) {
				echo "{$from} -> {$to}\n";
			}
		}
		else if (strpos($path, 'shortcode') !== false) {
			$from = str_replace($srcPath, '', $path);
			$to = "table/array-shortcode.cin";
			if (copy($path, $rootPath . '/' . $to)) {
				echo "{$from} -> {$to}\n";
			}
		}
		else if (strpos($path, 'big') !== false) {
			$from = str_replace($srcPath, '', $path);
			$to = "table/array30.cin";
			if (copy($path, $rootPath . '/' . $to)) {
				echo "{$from} -> {$to}\n";
			}
		}
		else {
			$from = str_replace($srcPath, '', $path);
			echo "{$from} -> ???\n";
		}
	}


	$dir = $srcPath . '/OkidoKey/';
	$files = glob($dir . '*.cin', GLOB_NOSORT);
	foreach ($files as $path) {
		if (strpos($path, 'regular') !== false) {
			$from = str_replace($srcPath, '', $path);
			$to = "table/array30_OkidoKey.cin";
			if (copy($path, $rootPath . '/' . $to)) {
				echo "{$from} -> {$to}\n";
			}
		}
		else if (strpos($path, 'big') !== false) {
			$from = str_replace($srcPath, '', $path);
			// echo "{$from} -> skipped";
			$to = "table/array30_OkidoKey-big.cin";
			if (copy($path, $rootPath . '/' . $to)) {
				echo "{$from} -> {$to}\n";
			}
		}
		else {
			$from = str_replace($srcPath, '', $path);
			echo "{$from} -> ???\n";
		}
	}

}