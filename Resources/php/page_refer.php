<?php
/*
 * A simple interface file - designed to go into each page dir
 * and send us to the master...
 */

//  Where are we?   Build some paths...
$phpself = $_SERVER['PHP_SELF'];  // e.g., /coLab/Group/Test/Page/HelloNola/pageref.php
$fullpath = __FILE__;			  // e.g., /Volumes/iMac 2TB/Software/coLab/Group/TestPage/HelloNola/pageref.php

// build path to the master script...
$path_parts = explode('/', $fullpath);
$n_parts = count($path_parts);
$master_parts = array_slice($path_parts, 1, $nparts-5);
$master_parts[] = "Resources";
$master_parts[] = "php";
$master_parts[] = "coLab_master.php";
$dlim = '/';		# path separator

$coLab_master = '';
foreach ($master_parts as $i) {
	$coLab_master .= $dlim . $i;
}

#echo "coLab_master: " . $coLab_master;

include($coLab_master)

?>
