<!-- Start: .../coLab/Resources/include/page/video.inc -->
<div id="video-container">

<video  id="video" poster="Poster_Start.png" width="640" height="480">
<!-- The following line is replaced with the full complement of html5 video codecs for this page... -->
 <?php echo $html5_source; ?>
  <!-- Fall back for non-html5 browsers, (WinXP/IE8, e.g.) simple mp4 embed tag -->
  <br>
  <embed src="<?php echo $name; ?>-media-Small.mp4" autostart="false" height="480" width="640" /><br>
  <font size=-2>
  <i>Your browser does not support html5 - using mp4 plug-in</i>
  </font>
</video>

<!-- Video Controls -->
<div id="video-controls">
  <span title="Play/Pause">
    <button type="button" style="vidbarbutton" id="play-pause">P</button>
   </span>
   <?php echo $locator_buttons; ?>

   <input type="range" id="volume-bar" min="0" max="1" step="0.1" value="1">
   <span title="FullScreen">
	<button type="button" id="full-screen">FS</button>
    </span>
 </div> <! video-controls>

</div> <! video-container>
