<?php
$DEBUGGING = True;
$TRACECOUNT = 0;
// imported from http://motoma.io/turning-on-php-debugging-and-error-messages/
if($DEBUGGING)
{
    error_reporting(E_ALL);
    ini_set('display_errors', True);
}
 
function trace($message)
{ 
    global $DEBUGGING;
    global $TRACECOUNT;
    if($DEBUGGING)
    {
        echo '<hr />;'.$TRACECOUNT++.'<code>'.$message.'</code><hr />';
    }
}
 
function tarr($arr)
{
    global $DEBUGGING; 
    global $TRACECOUNT; 
    if($DEBUGGING) 
    { 
        echo '<hr />'.$TRACECOUNT++.'<code>'; 
        print_r($arr); 
        echo '</code><hr />'; 
    } 
} 
 
?>