<!-- Start: .../coLab/Resources/include/page/content.inc -->

<div id="toplinkbar">	
	<! Start links...>
	<?php virtual ("links.html"); ?>
	<! ...end links.>
</div>	<!-- end toplinkbar -->

<div id="mainsection">
  <div id="midtitle">
	<table border=0 cellpadding=0 width=100%><tr> <td valign=top>
	<img src="Header.png" align=left alt="<?php echo $desc_title; ?>">
	</td> </tr></table>

	<table border=0 cellpadding=0 width=100%><tr> <td valign=top>
	<td>Group: </b><?php echo $group?></td>
	<td align=center><b>Song: </b><?php echo $song ?></td>
	<td align=right> <b>Duration: </b><?php echo $dur_string; ?> 
	</td> </tr> </table>
	<table border=0 cellpadding=0 width=100%><tr> 
	<td align=left> <i>Created: <?php echo $createtime ?> </i>
	</td>
	<td align=right>
	<i>Updated: <?php echo $updatetime ?> </i>
	</td><tr><td colspan=2><hr>
	</td></tr></table>
  </div>  <! end midtitle>
  <div id="maintext">
  	<br clear=all>
	<?php echo $description; ?>
<!-- End: .../coLab/Resources/include/page/content.inc -->
