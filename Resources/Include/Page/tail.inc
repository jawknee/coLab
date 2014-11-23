<!-- Start: .../coLab/Resources/include/page/tail.inc -->
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

	<?php virtual ("links.html"); ?>
	<p>&nbsp;<p>
	<font size=1>
	Page type: <?php echo $page_type; ?> - <a href="./index.shtml">php</a>
	</font>
	</div>	<! end maintext>
	</div>  <! end mainsection> 
	</div>	<! end Content >
    </div>  <! end container>
    </div>  <!-- end of Master -->
</body>
</html>
<!-- End: .../coLab/Resources/include/page/tail.inc -->
