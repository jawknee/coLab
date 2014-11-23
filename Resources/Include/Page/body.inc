<!-- Start: /coLab/Resources/include/page/body.inc -->
<body>
    <div id="Master">

<!  ----    Banner ---->
<div id="banner" > <! start of banner>
	<table width=80% border=0 cellpadding=0 class="banner_txt">
	  <td align="center" ><a href="<?php echo $groupURL?>/index.shtml" title="Always a nice place to go...">Home</a></td>

	  <td align="center" ><a href="<?php echo $groupURL?>/Shared/WhatsNew/index.shtml" title="The place to be, if you want to be somewhere else.">What's&nbsp;New</a></td>
	  <td align="center" ><a href="<?php echo $groupURL?>/Shared/Nav/index.shtml" title="How to get to where you need go.">Nav</a></td>
	  <td align="center" ><a href="<?php echo $groupURL?>/Shared/Archive/index.shtml" title="What have we been up to...">Archive</a></td>
	  <td align="center" ><a href="<?php echo $groupURL?>/Shared/Help/index.shtml" title="Hopefully, the help you need.">Help</a></td>
	</tr></table>
<br>
</div>	<! end of banner>

	<div id="container" >

	<div id="sidebar_l" class="sidebar_l">
	<?php virtual ($groupURL . "/Shared/mostrecent.html"); ?>
	<p><hr><P>
	<!--#include virtual="<?php echo $groupURL; ?>/Shared/projectlist.html" -->
	<?php virtual ($groupURL . "/Shared/projectlist.html"); ?>
	<p><hr><P>
	<!--#include virtual="<?php echo $groupURL; ?>/Shared/News.html" -->
	<?php virtual ($groupURL . "/Shared/News.html"); ?>
	<?php virtual ("/coLab/Resources/News.html"); ?>
	</div> <! End sidebar>

	<div id="sidebar_r" class="sidebar_r">
	<div id="coLabLogo" class="logo"><img src="/coLab/Resources/CoLab_Logo3D.png" height=50 width=50></div> 
	<! end logo>
	<?php virtual ("/coLab/Resources/Alert.html"); ?>
	<?php virtual ("/coLab/Resources/WelcomeMsg.html"); ?>
	<!--#include virtual="<?php echo $groupURL; ?>/Shared/rightbar.html" -->
	<!--#include virtual="/coLab/Resources/News.html" -->
	<?php virtual ($groupURL . "/Shared/rightbar.html"); ?>
	<p id="locators"></p>
	<p>
	<button type="button" id="sound-info-btn" title="Sound Info">Sound Info</button>
	<input type="hidden" id="sound-info" value="<?php echo $soundinfo; ?>">
	<hr><br>
	<p id="info"></p>	<! A paragraph for displaying...  info from javascript.>
	<table align="right" border=0><tr><td>
	<a href="http://colorfilter.wickline.org/colorblind/filter/button"
	target="_blank"><img
	alt="See your web site through colorblind eyes with the colorblind web
	page filter."
	src="http://colorfilter.wickline.org/colorfilter_button.gif" width="88"
	height="31"></a><br>Colorblind Safe
	</td></tr></table>

	</div> <! End right sidebar>

	<div id="Content" >
	  <div id=toptitle>
		<img src="Title.png" id="fundesc" alt="$fun_title" >
	  </div id=toptitle>


<!-- End: /coLab/Resources/include/page/body.inc -->
