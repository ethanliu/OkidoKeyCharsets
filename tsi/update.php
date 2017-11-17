<?php
$url = "https://github.com/openvanilla/McBopomofo/raw/master/Source/Data/BPMFMappings.txt";
$contents = file_get_contents($url);
$contents = strip_tags($contents);
// var_dump($contents);
file_put_contents("./tsi.txt", $contents);

