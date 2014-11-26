<?php
	/*
	 * coLab_master.php
	 * This is the main php script - all pages point here,
	 * then the script builds the web page based on the 
	 * data local the file original path.
	 */
	function inc_name($name) {
		//
		// just simplify building the include file name
		global $page_include_dir, $dlim;
		return $page_include_dir . $dlim . $name;
	}

	// an array that takes a size, and returns the "next" size down...
	// Used by function next_size
	$size_map = array(
	 '4k-Ultra-HD' => "HiDef",
	 'Super-HD' => "HiDef",
	 'Super-HD-Letterbox' => "Large",
	 'HiDef' => "Medium",
	 'HD-Letterbox' => "Small",
	 'Large' => "Small",
	 'Medium' => "Small",
	 'Small' => "Tiny",
	 'Tiny' => "Micro",
	 'Micro' => '',
	);

	function next_size($size) {
		 // return the next size...
		global $size_map;
		if ( $size == 'Small') {
			return '';
		} else {
			return $size_map[$size];
		}
	}
	
	function time_format($time) {
		// format for a scaled time string
		// Produces a useable sting based on $time in seconds.
		if ( $time < 60 ) {
			return sprintf("%2.3f secs", $test);
		}
		$minutes = (int) ($time / 60);
		$seconds = (int) ($time - ($minutes * 60 ));
		
		if ( $minutes < 60 ) {
			return sprintf("%d:%02.0f", $minutes, $seconds);
		}
		$hours = (int) ($minutes / 60);
		$minutes = $minutes - ($hours * 60);
		return sprintf("%2d:%02d:%02.0f", $hours, $minutes, $seconds);
	}
	

	//  Where are we?   Build some paths...
	if ( $phpself == "" ) {
		$phpself = $_SERVER['PHP_SELF'];  // e.g., /coLab/Group/Test/Page/HelloNola/index.php  (symlink to:)
	}
	$fullpath = __FILE__;			  // e.g., /Volumes/iMac 2TB/Software/coLab/Resources/php/coLab_master.php 
	// build paths to places we need
	$path_parts = explode('/', $fullpath);
	$n_parts = count($path_parts);
	$root_parts = $n_parts - 5; 		// number of segments to the coLab parent dir
	$dlim = '/';		# path separator
	$coLab_root = '';
	foreach (range(1, $root_parts) as $i) {
		$coLab_root .= $dlim . $path_parts[$i];
	}
	$code_path = $coLab_root . $dlim . 'coLab' .  $dlim . 'Code';
	$py2php_path = $code_path . $dlim . 'py2php.py';
	
	// Build the path to the Page include dir
	$page_include_dir = $coLab_root;
	foreach (array('coLab', 'Resources', 'Include', 'Page') as $part) {
		$page_include_dir .= $dlim . $part;
	}
	
	$page_home = $coLab_root . dirname($phpself);	// includes the leading '/coLab' from phpself
	$data_path = $page_home . $dlim . 'data';	
	
	// Read the page's data file, converted to php assignments - then evaluate
	// escape these as the paths may have spaces...
	$page_data_cmd = escapeshellarg($py2php_path) . ' ' . escapeshellarg($data_path);
	$data_results = `$page_data_cmd`;	# re
	eval($data_results);
	// At this point the page data vars are all in the env.
	//
	// do some format manipulation
	$dur_string = time_format($duration);
	
	if (version_compare(phpversion(), '5.2.0', '>')) {
		//$format = "Y-m-d h:i:s A T";
		$format = "M j, Y";
		date_default_timezone_set("America/Los_Angeles");
		$createtime = date_format(date_create($createtime), $format);
		$updatetime = date_format(date_create($updatetime), $format);
	}
	
	// Build meta-data - locator button tags:
	$locator_buttons = '<span>';
	if ( !isset($numbuts)) {
		$numbuts = 5;
		$nobutdef = True;
	} else {
		$nobutdef = False;
	}
	foreach (range(1, $numbuts) as $button) {
		$btn = (string)$button;
		$locator_buttons .= '<button type="button" id="LocBtn' . $btn . '">' . $btn . '</button>';
	}
	$locator_buttons .= '</span>';
	
	$groupURL = '/coLab/Group/' . $group;
	
	// The all important, html5-source tags...
	// Kind of the heart of the whole thing...
	$media_codecs = array(
		'ogg' => 'theora, vorbis',
		'mp4' => 'avc1.42E01E, mp4a.40.2',
		'webm' => 'vp8.0, vorbis');
	// list of type we're using...
	#$media_list = array( 'mp4', 'ogg', 'webm' );
	$media_list = array( 'mp4', 'webm' );

	$html5_source = '';

	$size = $media_size;	# start with the size of this video...
	while ( $size != '' ) {
		foreach ($media_list as $type) {
			$codecs = $media_codecs[$type];
			$html5_source .= <<<EOF
				<source src="$name-media-$size.$type" type='video/$type'; codecs="$codecs">

EOF;
			# Now - move down to the next size...
		}
		$size = next_size($size);
	}	

	
	include(inc_name('head.inc'));
	include(inc_name('body.inc'));
	//include(inc_name('banner.inc'));

	include(inc_name('video.inc'));
	include(inc_name('content.inc'));
	/*
	 * Generate the locator button info...
	 */
	echo <<<EOF
	 <!-- Locator button info -->
			<input type="hidden" id="numbut" value="$numbuts">

EOF;

	foreach (range(1, $numbuts) as $i) {
		$varname = "Loc_" . (string)$i;

		if ( $nobutdef ) {	// no button defined - old page...
			$value = 0.0;
		} else {
			$pvar = "\$" . $varname;
			eval("\$value = \"$pvar\";");
		}
		
		echo <<<EOF
	    <input type="hidden" id="$varname" class="locId" value="$value">

EOF;
		$varname .= '_desc';	# get the description...
		if ( $nobutdef ) {	// no button defined - old page...
			$value = "Unset";
		} else {
			$pvar = "\$" . $varname;
			eval("\$value = \"$pvar\";");
		}

		echo <<<EOF
		<input type="hidden" id="$varname" value="$value">

EOF;
	}

	echo <<<EOF
	<!-- End locator button info -->

EOF;
	// Geometry - hidden tags that tell the javascript how
	// to manuever for media clicks...
	//
	// We need a couple of (4) bits - these calls to 
	// colab_geo will return them.
	$clGeo_path = $code_path . $dlim . 'clGeo.py';
	$clGeo_cmd = escapeshellarg($clGeo_path) . ' ' . $media_size;
	$offset_cmd = $clGeo_cmd . ' -o';
	$xOffset = `$offset_cmd` + 0;	# add zero to get rid of the newline...
	
	$pgview_cmd = $clGeo_cmd . ' -p';
	$pgview_width = `$pgview_cmd` + 0;
	
	$mwidth_cmd = $clGeo_cmd . ' -w';
	$media_width = `$mwidth_cmd` + 0;

	$mheight_cmd = $clGeo_cmd . ' -h';
	$media_height = `$mheight_cmd` + 0;

	if ($use_soundgraphic) {
		# there is no screen shot - use the media size...
		$pgview_scale = (float)$media_width / $pgview_width;
		$screenshot_width = "None";
		# open loop alert: calculating the image borders as per imagemaker...
		# triple open loop alert: see above

		$factor_cmd = $clGeo_cmd . ' -f';
		$adjust_factor = `$factor_cmd` + 0;

		$left_cmd = $clGeo_cmd . ' -l';
		$xStart = (int)(`$left_cmd` + 0) * $adjust_factor;
		$right_cmd = $clGeo_cmd . ' -r';
		$xEnd = (int)( $media_width - ( (`$right_cmd` + 0 ) * $adjust_factor) );
		/*
		*/
	}
	else {
		$pgview_scale = (float)$screenshot_width / $pgview_width;
	}
	
	include(inc_name('geometry.inc'));

	echo <<<EOF
	<!--  Internal Debug fun...  specific to the php rendering...
	<p><hr>Debug<hr><p>
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
	end php debug -->
EOF;

	include(inc_name('tail.inc'));
	
?>
