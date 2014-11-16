<?php 
	/*
	 * coLab_master.php
	 * This is the main php script - all pages point here,
	 * then the script builds the web page based on the 
	 * data local the file original path.
	 */
	$phpself = $_SERVER['PHP_SELF'];  // e.g., /coLab/Group/Test/Page/HelloNola/index.php  (symlink to:)
	$fullpath = __FILE__;			  // e.g., /Volumes/iMac 2TB/Software/coLab/Resources/php/coLab_master.php 
	// build paths to places we need
	$path_parts = explode('/', $fullpath);
	$n_parts = count($path_parts);
	$root_parts = $n_parts - 5; 		// number of segments to the coLab parent dir
	$dlim = '/';		# path separator
	$coLab_root = '';
	foreach (range(1, $root_parts) as $i) {
		$coLab_root = $coLab_root . $dlim . $path_parts[$i];
	}
	$code_path = $coLab_root . $dlim . 'coLab' .  $dlim . 'Code';
	$py2php_path = $code_path . $dlim . 'py2php.py';
	
	$page_include_dir = $coLab_root;
	foreach (array('coLab', 'Resources', 'Include', 'Page') as $part) {
		$page_include_dir = $page_include_dir . $dlim . $part;
	}
	

	$page_home = $coLab_root . dirname($phpself);	// includes the leading '/coLab' from phpself
	$data_path = $page_home . $dlim . 'data';	
	
	// escape these as the paths may have spaces...
	$page_data_cmd = escapeshellarg($py2php_path) . ' ' . escapeshellarg($data_path);
	#$result = exec($page_data_cmd, &$data_results);
	$data_results = `$page_data_cmd`;
	eval($data_results);
	
	// Build meta-data - locator button tags:
	$locator_buttons = '<span>';
	foreach (range(1, $numbuts+1) as $button) {
		$btn = (string)$button;
		$locator_buttons = $locator_buttons . '<button type="button" id="LocBtn' . $btn . '">' . $btn . '</button>';
	}
	$locator_buttons = $locator_buttons . '</span>';
	
	$headinclude = $page_include_dir . $dlim . 'head.inc';
	include($headinclude);
	$groupURL = '/coLab/Group/' . $group;
	$bodyinclude = $page_include_dir . $dlim . 'body.inc';
	include($bodyinclude);
	$bannerinclude = $page_include_dir . $dlim . 'banner.inc';
	include($bannerinclude);
	echo <<<EOF
	<div id="Content" class="main" style="height: 97%; overflow: auto ">
EOF;
	$videoinclude = $page_include_dir . $dlim . 'video.inc';
	include($videoinclude);
	$contentinclude = $page_include_dir . $dlim . 'content.inc';
	include($contentinclude);

	echo <<<EOF
	<h2>coLab Master</h2>
	Our path is: $local_path
	<p>
	PHP_SELF: is: $phpself <br>
	fullpath: $fullpath <br>
	nprts: $n_parts <br>
	coLab_root: $coLab_root<br>
	page_home: $page_home<br>
	data_path: $data_path<br>
	page_data_cmd: $page_data_cmd<br>
	head_include: $headinclude<br>
	banner_include: $bannerinclude<br>
	<p>
	data:
	<p> <hr> <p>
	$fun_title
	<p> <hr> <p>
	$data_results

	<p> <hr> <p>
	
	Onward...
EOF;

	$tailinclude = $page_include_dir . $dlim . 'tail.inc';
	include($tailinclude);
	
?>
