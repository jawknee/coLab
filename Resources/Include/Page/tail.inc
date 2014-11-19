<!-- /Volumes/iMac 2TB/Software/coLab/Resources/include/page/head.inc -->
	<hr>
	Enter your comments here:<br>
		
	<form method=POST action="/coLab/bin/postcomments.cgi">
	Your name: <input type="text" name="Commenter" ><br>
	<input type="hidden" name="page" value="!name!">
	<input type="hidden" name="desc_title" value="!desc_title!">
	<textarea name="Text" rows=7 cols=80 id="CommentBox"></textarea>
	<br>

	<input type="submit" value="Add your comment">
	</form>
	<p><hr><p>
	<h3>Comments:</h3>
	<!--#include virtual="Comments.log" -->
	<?php virtual ("Comments.log"); ?>
	<p>
	<br>
	<div class=copyright>
	&copy; Catharsis Studios West 2014
	</div><! end of copyright>
	<!--#include virtual="links.html" -->
	<?php virtual ("links.html"); ?>
	<p>&nbsp;<p>
	</td></tr></table>
	<font size=1>
	Page type: <?php echo $page_type; ?> - php
	</font>
	</div>	<! middle content>
	</div>	<! container >

</body>
</html>
