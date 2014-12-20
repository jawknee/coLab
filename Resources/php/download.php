<?php
/*
 * A simple interface file - designed to go into each page dir
 * and send us to the master...
 */

global $fun_title;

$dfile = 'HelloNola.mp3';

$file = $_GET["dl_file"];
$dir = $_GET["dl_dir"];


if ( $file != $dfile ) {
	$msg = 'They differ?? ' .  $file . ' - ' .  $dfile;	
}

if (! chdir ($dir) ) {
	echo <<<EOF
	<html><body><h1>OOOPs: cannot chdir to $dir</h1>
	What he said
	</body>
	</html>
EOF;
}

if (! file_exists($file)) {
	echo <<<EOF
	<head><title>No go on $file</title></head>
	<body>
	<h3>Not Found:</h3>
	The file was not found: $file<p>
	phpself: $phpself<p>
	file: $file
	msg: $msg

	</body>
	</html>
EOF;
} else {
    // Set headers
    header("Cache-Control: public");
    header("Content-Description: File Transfer");
    header("Content-Disposition: attachment; filename=$file");
    header("Content-Type: application/zip");
    header("Content-Transfer-Encoding: binary");
    // Read the file from disk
    readfile($file); 
}

?>
