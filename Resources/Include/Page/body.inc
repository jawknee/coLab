<!-- /Volumes/iMac 2TB/Software/coLab/Resources/include/page/body.inc -->
</head>
<body>

	<! Good old jQuery >
	<script type="text/javascript" src="/coLab/Resources/jquery-1.11.1.min.js"></script>
	<! Our main javascript to drive the video - and most everything else >
	<script type= "text/javascript" src="/coLab/Resources/video_engine.js"></script>
	<! the ContextJS package for working context menus >
	<script type="text/javascript" src="/coLab/Resources/context.js"></script>

	<!--   Menu Header -->
	<div id="container" style="height: 100%; width: 100%; overflow: hidden;">
	<div class="sidebar_l">
	<?php virtual ($groupURL . "/Shared/mostrecent.html"); ?>
	<p><hr><P>
	<!--#include virtual="<?php echo $groupURL; ?>/Shared/projectlist.html" -->
	<?php virtual ($groupURL . "/Shared/projectlist.html"); ?>
	</div> <! End sidebar>
	<div class="sidebar_r">
	<!--#include virtual="/coLab/Resources/News.html" -->
	<?php virtual ("/coLab/Resources/News.html"); ?>
	<!--#include virtual="<?php echo $groupURL; ?>/Shared/News.html" -->
	<?php virtual ($groupURL . "/Shared/News.html"); ?>
	<!--#include virtual="<?php echo $groupURL; ?>/Shared/rightbar.html" -->
	<?php virtual ($groupURL . "/Shared/rightbar.html"); ?>
	<p id="locators"></p>
	<p>
	<button type="button" id="sound-info-btn" title="Sound Info">Sound Info</button>
	<input type="hidden" id="sound-info" value="<?php echo $soundinfo; ?>">
	<hr><br>
	<p id="info"></p>	<! A paragraph for displaying...  info from javascript.>
	</div> <! End right sidebar>
	<div id="Logo" class="logo"><img src="/coLab/Resources/CoLab_Logo3D.png" height=50 width=50></div> 
	<! end logo>
	<!div id="Content" class="main" style="height: 97%; overflow: auto ">

