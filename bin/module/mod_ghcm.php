<?php
/**
 * ghcm
 *
 * https://github.com/zeylei/ghcm
 *
 * @author Ethan Liu
 * @copyright Creativecrap.com, 13 October, 2020
 * @package module
 */

$raw = explode("\n", file_get_contents($srcPath));

$prepend = true;
$partial = false;

$mode = 'cin';
// $mode = 'lexicon';

$header = <<<'EOH'
#
# 矧码 (ghcm)
# https://github.com/zeylei/ghcm
#
# 方案名称：矧码
# 方案作者：矧可射思
# 更新日期：{{version}}
#
# 本仓库中的矧码码表与官方 QQ 群 (461618919) 同步更新。
# 由作者矧可射思授权，任何人皆可以修改、复制、转发，以及免费内建此词库（包括收费使用）。
# 学习矧码请加 QQ 群 (461618919)。
#
# ==========
#
# 此 cin 表格由 SM.dict.yaml 转换
# 由于部份符号为 rime 另行定义，因此未能直接于 cin 表格中实现，此档仅包含「,」键符号。
# 而「i」键原定义为直出「，」而非字根，但为统一输入行为，仍先将「i」键列为字根。
#
#
%ename ghcm
%cname 矧码
%encoding UTF-8
%selkey 1ex\\234890
%keyname begin
a	a
b	b
c	c
d	d
e	e
f	f
g	g
h	h
i	i
j	j
k	k
l	l
m	m
n	n
o	o
p	p
q	q
r	r
s	s
t	t
u	u
v	v
w	w
x	x
y	y
z	z
.	.
,	,
;	;
/	/
%keyname end
%chardef begin
,	、
,	；
,	#
EOH;

$footer = "%chardef end\n";

parse($raw, $mode, $header, $footer, $partial);

function parse($raw, $mode = '', $header = '', $footer = '', $partial = false) {

	$parsing = false;
	$tag = "...";
	$version = date("Y-m-d");
	$content = "";

	foreach ($raw as $line) {
		$line = trim($line);
		// if (strpos($line, "version:") !== false) {
		// 	$version = trim(str_replace(["version:", "\""], "", $line));
		// 	continue;
		// }

		if ($line === $tag) {
			$parsing = true;
			continue;
		}

		if (!$parsing) {
			continue;
		}

		// keep #
		// echo "before: " . $line . "\n";
		// $line = trim(preg_replace('/#(.?)*/', '', $line));
		// echo "after: " . $line . "\n";

		if (empty($line)) {
			continue;
		}

		$row = explode("\t", $line);
		if (empty($row)) {
			continue;
		}

		if (count($row) < 2) {
			var_dump($row);
			die($line);
		}

		$phrase = trim($row[0]);
		$radical = trim(str_replace(" ", "", $row[1]));
		$weight = isset($row[2]) ? intval($row[2]) : 0;

		if ($mode == 'cin') {
			if ($partial && mb_strlen($phrase) > 1) {
				continue;
			}
			$content .= "{$radical}\t{$phrase}\n";
		}
		else if ($mode == 'lexicon') {
			if ($partial && mb_strlen($phrase) < 2) {
				continue;
			}
			$content .= "{$phrase}\t{$weight}\t{$radical}\n";
		}
		else {
			echo "Unknown mode";
			exit;
			// $content .= "{$radical}\t{$phrase}\n";
			// $content .= "{$phrase}\t{$weight}\t{$radical}\n";
		}
	}

	$header = str_replace("{{version}}", $version, $header);

	echo $header;
	echo $content;
	echo $footer;
}