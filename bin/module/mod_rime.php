<?php
/**
 * bossy - convert cin key(\s\t)?value to value(\t)key format
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 29 August, 2021
 * @package module
 */

$base = new TableReader($srcPath, false);
foreach ($base->data as $item) {
	echo "{$item->value}\t{$item->key}\n";
}
