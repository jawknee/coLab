// main code for handling coLab functions...
//
// Sets up and manages various control functions related to playing
// the video and going into fullscreen mode.  Also handles the
// Click! option to click anywhere on a graphic and have the 
// video play from that location.
//
// Uses parseUri - included below.
//
window.onload = function() {

	// ----------------------------------------
	// 	Initial Assignments
	// ----------------------------------------
	// Status
	var playStatus = "Initial";	// values: "Initial", "Playing", "Paused", or "Ended"
	var clickStatus = "Ready";	// values: "Ready", "Down", or "Waiting"
	var fullscreenStatus = "Initial";
	var fullscreenMode = "unset";
	var lastxclick = -1;
	var lastyclick = -1;
	var currentLocation = 0.;
	var baseURL = document.URL
	var parse = parseUri(baseURL);

	// Video
	var video = document.getElementById("video");
	var vcontainer = document.getElementById("video-container");
	var clickbar = document.getElementById("clickbar");
	var clickdiv = document.getElementById("clickdiv");

	// Buttons
	var playButton = document.getElementById("play-pause");
	var muteButton = document.getElementById("mute");
	var fullScreenButton = document.getElementById("full-screen");
	var soundInfoButton = document.getElementById("sound-info-btn");
	var soundInfoEl = document.getElementById("sound-info");
	if ( soundInfoEl ) {
		var soundInfo = document.getElementById("sound-info").value;
	} else {
		soundInfo = "No Information Available.";
	}

	// Locator buttons...
	var locatorText = document.getElementById("locators");
	var numButs = document.getElementById("numbut");
	if (  numButs ) {
		numButs = numButs.value;
	} else {
		numButs = 0;
	}
	var locatorTextString = "";

	// Sliders
	var seekBar = document.getElementById("seek-bar");
	var volumeBar = document.getElementById("volume-bar");
	displayAttrById("volume-bar");
	
	// info
	var infoText = document.getElementById("info");
	var eventlist = ">";
	var clickType = "none";

	// x coordinate info
	// (for now - get this from cookies...)
	var xOffset = document.getElementById("xOffset").value;
	var xStart = document.getElementById("xStart").value;
	var xEnd = document.getElementById("xEnd").value;
	var pageScale = document.getElementById("pageScale").value;
	var screenshotWidth = document.getElementById("screenshotWidth").value;

	var xoff = parseInt(xOffset);
	var xmin = parseInt(xStart);
	var xmax = parseInt(xEnd);
	var pscale = parseFloat(pageScale);
	if ( screenshotWidth != 'None' ) {
		var scrnwide = parseInt(screenshotWidth);
	}
	// media info...
	var duration = document.getElementById("duration").value;
	var mediaWidth = document.getElementById("media_width").value;

	var dur = parseFloat(duration);
	var mdwide = parseInt(mediaWidth);
	
	//  now - let's find our full screen requester...
	if (video.requestFullscreen) {
		fullscreenMode = "Generic";
		var fullscreenRequester = function () { video.requestFullscreen(); }	// Generic
		var fullscreenElement = document.fullscreenElement;
		var fullscreenEnabled = document.fullscreenEnabled;
	} else if (video.mozRequestFullScreen) {
		fullscreenMode = "Mozilla";
		var fullscreenRequester = function () { video.mozRequestFullScreen(); } // Firefox
		var fullscreenElement = document.mozFullScreenElement;
		var fullscreenEnabled = document.mozFullScreenEnabled;
	} else if (video.webkitRequestFullscreen) {
		fullscreenMode = "Webkit";
		var fullscreenRequester = function () { video.webkitRequestFullscreen(); } // Chrome and Safari
		var fullscreenElement = document.webkitFullscreenElement;
		var fullscreenEnabled = document.webkitFullscreenEnabled;
	} else if (video.webkitEnterFullScreen) {
		fullscreenMode = "iOS";
		var fullscreenRequester = function () { video.webkitEnterFullScreen(); } // Chrome and Safari
		var fullscreenElement = document.fullscreenElement;  //  NO!  only a place holder
		var fullscreenEnabled = document.fullscreennabled;  //  NO!  only a place holder
	} else if (video.msRequestFullscreen) {
		fullscreenMode = "Microsoft";
		var fullscreenRequester = function () { video.msRequestFullscreen(); } // MS / IE
		var fullscreenElement = document.msFullscreenElement;
		var fullscreenEnabled = document.msFullscreenEnabled;
	} else {
		fullscreenMode = "None";
	}

	// ----------------------------------------
	//      URL parsing...
	// ----------------------------------------
	// URL "query" values 
	if ( parse.queryKey.time ) {
		timeArray = parse.queryKey.time.split(':');
		console.log("Time array: " + timeArray[0]);
		if ( timeArray[1] ) {	// minutes were specified...
			startTime = parseFloat(timeArray[0]) * 60. + parseFloat(timeArray[1]);
		} else {
			startTime = parseFloat(timeArray[0]); 	// seconds only...
		}
	} else {
		startTime = 0.0;
	}
	console.log("Start time: " + startTime.toFixed(3));
	if ( startTime != 0.0 ) {
		//
		playIt();	// if nothing else, get off that initial screen...
		pauseIt();
		video.currentTime = startTime;
		pauseIt();
	
	}
	//
	//
	// ----------------------------------------
	// 	Info output...
	// ----------------------------------------

	// a little something to keep us informed...
	function postInfo(msg) {
		var infoString = '<b>Status:</b> ' + playStatus + '<br>' +
			'<b>Current:</b> ' + video.currentTime.toFixed(3) + '<br>' +
			'<b>Message:</b> ' + msg + '<br>' +
			'<b>Volume:</b> ' + video.volume.toString() + '<br>' ;
		
		if ( video.muted ) {
			infoString += '<b>Muted</b><br>'
		} else {
			infoString += '<b>Not Muted</b><br>'
		}

		infoString += "<b>video Source:</b> " + video.currentSrc.split('/').pop() + '<br>';
		infoString += "<b>URL:</b> " + baseURL + '<br>';
		infoString += "<b>host:</b> " + parse.host + '<br>';
		infoString += "<b>query:</b> " + parse.query + '<br>';
		infoString += "<b>time:</b> " + parse.queryKey.time + '<br>';
		infoString += "<b>starttime:</b> " + startTime.toFixed(3) + '<br>';
		infoString += "<b>videoWidth:</b> " + video.videoWidth.toString() + '<br>';
		/*
		infoString += "<b>videoDurtn:</b> " + video.duration.toFixed(3) + '<br>';
		infoString += "<b>ActualDurtn:</b> " + dur.toFixed(3) + '<br>';

		infoString += "<b>Last Click:</b> (" + lastxclick.toString() + ', ' + lastyclick.toString()  + ') <br>';
		infoString += "xOffset: " + xOffset.toString() + '<br>';
		infoString += "xStart: " + xStart.toString() + '<br>';
		infoString += "xEnd: " + xEnd.toString() + '<br>';
		infoString += "xmin/max: " + xmin.toString() + ', ' + xmax.toString() + '<br>';
		infoString += "pscale: " + pscale.toFixed(3) + '<br>';
		infoString += "Screenshot: " + screenshotWidth + '<br>';
		infoString += "Screen width: " + screen.width.toString() + '<br>';
		infoString += "Screen height: " + screen.height.toString() + '<br>';
		infoString += "Fullscreen: " + fullscreenStatus + '<br>';
		infoString += "Fullscreen Mode: " + fullscreenMode + '<br>';
		infoString += "<b>Click Type:</b> " + clickType + '<br>';
		//infoString += "<b>Event Name:</b> " + eventlist + '<br>'; 
		*/

		infoText.innerHTML = infoString;
	}

	postInfo("Page loaded.");

	// ----------------------------------------
	// 	Button Pressing / Setting
	// ----------------------------------------
	//
	//  functions to set the icons into the buttons...
	function setPlayButton() {
		if ( video.paused == true ) {
			//playButton.innerHTML = '<img src="/coLab/Resources/Icons/Play_24x24xp_02.png" alt="Play">';
			playButton.innerHTML = '<img src="/coLab/Resources/Icons/Play_24x24btn_03.png" alt="Play">';
			//  also handle full screen where we don't have control...
			if ( playStatus == 'Paused' && video.paused == true ) {
				//video.style.cursor = 'wait';
				video.style.cursor = "url(/coLab/Resources/Cursors/pause_3D.gif), url(/coLab/Resources/Cursors/pause_3D.cur), wait";
			}
		} else {
			playButton.innerHTML = '<img src="/coLab/Resources/Icons/Pause_24x24xp_01.png" alt="Pause">';
			video.style.cursor = 'default';
		}
	}

	setPlayButton();

	if ( muteButton ) {		// temporary - until we update all pages... ?
	function setMuteButton() {
		if (video.muted == false) {
			muteButton.innerHTML = '<img src="/coLab/Resources/Icons/Unmuted_24x24xp_02.png" alt="Mute">';
		} else {
			muteButton.innerHTML = '<img src="/coLab/Resources/Icons/Muted_24x24xp_02.png"" alt="Unmute">';
		}
	}

	setMuteButton();
	}

	function setFSButton() {
		if (fullscreenMode == "None" ) {
			fullScreenButton.innerHTML = '<img src="/coLab/Resources/Icons/NoFullscreen_Gray_24x24xp.png" alt="Fullscreen Unavailable">';
		} else {
			fullScreenButton.innerHTML = '<img src="/coLab/Resources/Icons/Fullscreen_Gray_24x24xp.png" alt="Fullscreen">';
		}
	}

	setFSButton();

	// Set the poster to a new value, based on the string passed in:
	// Poser_<poster_type>.png
	function updatePoster(poster_type) {
		var currentPoster = document.getElementById("video").poster;
		path = currentPoster.split('/');
		poster = path.pop()
		console.log("Update Poster: " + currentPoster + ' - ' + poster);
		poster_name = "Poster_" + poster_type + ".png";
		video.poster = poster_name;


		currentPoster = document.getElementById("video").poster;
		console.log("New poster? " + currentPoster);
	}


	//  start the video playing 
	function playIt() {
		if ( playStatus == "Initial") {
			updatePoster('Waiting');
		}
		video.play();
		playStatus = "Playing";

		// Update the button text to 'Pause'
		//playButton.innerHTML = "Pause";
		setPlayButton();
	}
	// or pause it...
	function pauseIt() {
		// pause it anything else handy...
		video.pause();
		playStatus = "Paused";
		setPlayButton();
	}

	// or toggle...
	function togglePlayPause() {
		// typically a space character:  toggle play status...
		if ( playStatus == "Playing" ) {
			pauseIt();
		} else {
			playIt();
		}
		return
	}

	// ----------------------------------------
	//      Location Buttons - set them up
	// ----------------------------------------
	function handleLocButton(e) {
		// find event - probably overkill, from: 
		// http://www.quirksmode.org/js/events_properties.html
		var targ;
		if (!e) var e = window.event;
		if (e.target) targ = e.target;
		else if (e.srcElement) targ = e.srcElement;
		if (targ.nodeType == 3) // defeat Safari bug
			targ = targ.parentNode;
		
		var btnID = targ.getAttribute("id");
		locID = btnID.replace("LocBtn", "Loc_");	// change name to loc ID
		var locDesc = document.getElementById(locID + "_desc").value;
		if ( locDesc !== 'Unset' ) {
			var locValstring = document.getElementById(locID).value;
			var timeOffset = parseFloat(locValstring);
			video.currentTime = timeOffset;
			playIt();
		}

	}
	function toTimeString(time) {
		// convert the number, in seconds, 
		// into minutes and seconds
		mins = parseInt(time/60);
		secs = time - mins * 60;
		isecs = parseInt(secs);
		frac = secs - isecs;
		secstr = secs.toFixed(0);
		return mins.toFixed(0) + ":" + ('0' + secstr).substr(-2) + '.' + frac.toFixed(3).substr(2);
	}

	//
	// Set up each button - putting a number (or "-" if not
	// set) into each button, and build the locations 
	// text as we go.   Finally - add a handler for each.
	for (i = 1; i <= numButs; i++) {
		if ( locatorTextString == '' ) {
			locatorTextString = "<b>Locations:</b><br>";
		}
		var locVar = "Loc_" + i.toString();
		//console.log("locvar " + locVar);
		var locValstring = document.getElementById(locVar).value;
		var locVal = parseFloat(locValstring);
		//console.log ("loc val " + locVal.toString());
		locVar += "_desc"
		var locDesc = document.getElementById(locVar).value;
		var buttonTextString = locDesc + " (" + toTimeString(locVal)+  ")";

		if ( locDesc == 'Unset' ) {
			btnType="dash";	//  use use a "-" if no value...
		} else {
			btnType=i.toFixed(0);
		}
		//  set the text for the side bar...
		var btnID = "LocBtn" + i.toString();

		var locButton = document.getElementById(btnID);

		if ( locDesc !== 'Unset' ) {
			locatorTextString += btnType + ". "
			locatorTextString += buttonTextString + "<br>"
			locatorText.innerHTML = locatorTextString;
			locButton.title = buttonTextString;
		}

		// Load up the image for this button - also pass the buttonID in - since we're more likely to 
		// click on the "image" rather than the button.
		var buttonGraphic = "/coLab/Resources/Icons/Numerals/Button_" + btnType + ".png";
		locButton.innerHTML = '<img src="' + buttonGraphic + '" title="' +
			buttonTextString + '" id="' + btnID + '" >';
		//  while we're at it - let's set up the even handler for each button...
		locButton.addEventListener("click", function(e) {
			handleLocButton(e);
			});

	}

	// ----------------------------------------
	// 	Event Listeners
	// ----------------------------------------
	//
	// Set up the listeners and functions to handle button
	// clicks and keys
	//
	// Event listener for the play/pause button
	playButton.addEventListener("click", function() {
		if (video.paused == true) {
			playIt();
		} else {
			// Pause the video
			pauseIt();
		}
		postInfo("Play button");
	});

	// Event listener for the mute button
	if ( muteButton ) {	// temporary - until we update all pages... ?
	muteButton.addEventListener("click", function() {
		if (video.muted == false) {
			// Mute the video
			video.muted = true;

		} else {
			// Unmute the video
			video.muted = false;

		}
		// Update the button text
		setMuteButton();
		postInfo("Mute pressed.");
	});
	}

	// Event listener for the full-screen button
	fullScreenButton.addEventListener("click", function() {
		//  Call the requester we found at load time...
		//  unless there isn't one....
		postInfo("FullScreen Button");
		if ( fullscreenMode != "None" ) {
			fullscreenRequester();
			console.log("Requesting full screen for " + fullscreenMode );
		} else {
			alert("Your browser does not support the Full Screen Mode API.");
		}
		//video.removeAttribute("controls");	// no help...
		clickType = 'reset';		// renable document clicks...
	});


	// Event listener for the seek bar
	if ( seekBar ) {	// temporary - until we update all pages... ?
	seekBar.addEventListener("change", function() {
		// Calculate the new time
		currentLocation = video.duration * (seekBar.value / 100);

		// Update the video time
		video.currentTime = currentLocation;
	});

	
	// Update the seek bar as the video plays
	video.addEventListener("timeupdate", function() {
		// Calculate the slider value
		var value = (100 / video.duration) * video.currentTime;

		// Update the slider value
		seekBar.value = value;
		postInfo("update");
	});
	}

	// when video completes, change the play button to "play"
	video.addEventListener("ended", function () {
		// done - just change the play button...
		// Update the button text to 'Play'
		playStatus = "Ended";
		postInfo("Finished.");
		setPlayButton();
	});


	// Pause the video when the seek handle is being dragged
	if ( seekBar ) {	// temporary - until we update all pages... ?
	seekBar.addEventListener("mousedown", function() {
		pauseIt();
	});

	// Play the video when the seek handle is dropped
	seekBar.addEventListener("mouseup", function() {
		video.play();
		setPlayButton();
	});
	}

	// Event listener for the volume bar
	volumeBar.addEventListener("change", function() {
		// Update the video volume
		video.volume = volumeBar.value;
	});

	// Event listeners so we know when we're inside the video...
	// Need this because key events all come from the top level doc
        video.addEventListener("mouseover", function() {
                // indicate we are hovering over the video box...
                videoOver = true;
                console.log("Over the video...");
        }, false);
                
        video.addEventListener("mouseout", function() {
                // indicate we are leaving the video box...
                videoOver = false;
                console.log("Out of the video...");
        }, false);

	// handle clicks on the sound info button...
	soundInfoButton.addEventListener("click", function() {
		// just pop up an alert with the content of the sound-info var...
		alert(soundInfo);
		}
	);

	/*
	// Entering fullscreen mode
	function handleFullscreen (event) {
	    	var state = document.fullScreen || document.mozFullScreen || document.webkitIsFullScreen;
	    	fullscreenStatus = state ? 'FullscreenOn' : 'FullscreenOff';

		postInfo("Fullscreen xition");

		//alert('Fullscreen event: ' + fullscreenStatus);
	
		//video.removeAttribute("controls")
		if ( fullscreenStatus == 'FullscreenOff' ) {
			setPlayButton();
		}
	};

	// Add the full-screen change handlers...
	video.addEventListener('webkitfullscreenchange', handleFullscreen, false );
	video.addEventListener('mozfullscreenchange', handleFullscreen, false );	// Doesn't work... handled in video.click
	video.addEventListener('fullscreenchange', handleFullscreen, false );
	*/

	function checkFullscreenMode () {
		// 
		// Can we do this generically?   Apparently not...
		/*
		if ( fullscreenElement &&  fullscreenElement.nodeName == 'VIDEO'  ) {
			element = fullscreenElement.nodeName;
			msg = 'Your ' + fullscreenMode + ' video is playing in fullscreen - element ' + element ;
			fullscreenStatus = 'FullscreenOn';
		} else {
			msg = 'Your ' + fullscreenMode + ' video is playing in pageview ';
			fullscreenStatus = 'FullscreenOff';
			setPlayButton();
		}
		console.log(msg);
		return;
		*/
		// The screenchange events are not happening consistently - so far now, we test each time
		// we get a click...
		// 
		// Some special handling each style of browser...
		// We set fullscreenState to a Boolean - and then the fullscreenStatus string from there...
		if ( fullscreenMode == "Generic" ) {
			var fullscreenState = document.fullscreenElement &&  document.fullscreenElement.nodeName == 'VIDEO';
		}
		if ( fullscreenMode == 'Mozilla' ) {
			var fullscreenState = document.mozFullScreenElement && document.mozFullScreenElement.nodeName == 'VIDEO';
		}
	
		if ( fullscreenMode == 'Webkit' ) {
			fullscreenState =  document.webkitFullscreenElement &&  document.webkitFullscreenElement.nodeName == 'VIDEO';
		}
		// And likewise with Microsoft / IE
		if ( fullscreenMode == 'Microsoft' ) {
			var fullscreenState = document.msFullscreenElement &&  document.msFullscreenElement.nodeName == 'VIDEO';
		}	
		if ( fullscreenState ) {
			fullscreenStatus = 'FullscreenOn';
		} else {
			fullscreenStatus = 'FullscreenOff';
			setPlayButton();
		}

		msg = "Your " + fullscreenMode + " browser is playing status: " + fullscreenStatus;
		console.log(msg);
	}


	// ----------------------------------------
	// 	Keys...
	// ----------------------------------------
	// What to do with key presses...
	// for now: only the video object, and we're only 
	// handling <space>
	//
	document.addEventListener('keydown', function(e) {
		console.log("Greetings from on key down document... " + e.srcElement);
		if ( ! videoOver ) {
			return;
		}
		if (! e) {
			console.log("Alternate event");
			e = window.event;
		}
		if (e.keyCode == 32) {
			console.log("got a space");
			togglePlayPause();
			return false;
		}
		}, true);

	// ----------------------------------------
	// 	CLICK!
	// ----------------------------------------
	//
	// Handle the button clicks for the video
	// Setup multiple handlers:
	// Currently: video, div, document
	//
	// Use the document click in full screen to get 
	// clicks for some browsers.
	//
	// Clicks are managed - then we call the handler
	// to reposition the video.  Going into and 
	// out of full screen resets which is preferred.
	//
	// Set up handlers for the various clicks..
	// Two each, mousedown and mouse up...
	//
	// video - this is the one we want, if we can get it
	// mouse down
	video.addEventListener('mousedown', function(e) {
		console.log("video mousedown" + clickType);
		eventlist += 'v';
		if ( clickType != 'div' ) {
			handleMouseDown(e);
		}
		clickType = 'video';
		postInfo("Video MouseDown");
		}, false);

	// mouse up
	video.addEventListener('mouseup', function(e) {
		console.log("video mouseup" + clickType);
		eventlist += 'vu';
		if ( clickType == 'video' ) {
			handleMouseUp(e);
			eventlist += '+';
		}
		postInfo("Video MouseUp");
		}, false);

	//  div - possibly redundant   secondary to video
	// mouse down
	clickdiv.addEventListener('mousedown', function(e) {
		console.log("div mousedown" + clickType);
		eventlist += 'd';
		if ( clickType != 'video' ) {
			if ( clickType != 'Doc' ) {
				handleMouseDown(e);
				eventlist += '+';
			}
			clickType = 'div';
		}
		postInfo("Div MouseDown");
		}, false);
	// mouse up
	clickdiv.addEventListener('mouseup', function(e) {
		console.log("div mouseup" + clickType);
		eventlist += 'cu';
		if ( clickType == 'div' ) {
			handleMouseUp(e);
			eventlist += '+';
		}
		postInfo("Click MouseUp");
		}, false);

	
	// click in the whole document - ignore other than in
	// full screen - needed as some video elements do 
	// not pass through clicks.  At least sometimes, the
	// document does.
	// mousedown
	document.addEventListener('mousedown', function(e) {
		console.log("doc MouseDown" + clickType);
		eventlist += 'D';
		if ( clickType != 'video' && clickType != 'div' && fullscreenStatus == 'FullscreenOn' ) {
			clickType = 'Doc';
			handleMouseDown(e);
			eventlist += '+';
		}
		postInfo("Document MouseDown");
		}, false);
	// mousedown
	document.addEventListener('mouseup', function(e) {
		console.log("doc mouseup" + clickType);
		eventlist += 'du';
		if ( clickType == 'Doc' ) {
			handleMouseUp(e);
			eventlist += '+';
		}
		postInfo("Doc MouseUp");
		}, false);

	
	//
	// ----------------------------------------
	// Click!  -  Mouse Juggling...
	// ----------------------------------------
	// To give us some flexibility in the user interface, we handle
	// mouse down and up separately.  We use a timeout after an initial
	// down to let use detect both a held mouse, or a double click  
	// (for now - the same time out:  .5 seconds)
	// 

	// handle the first part of a click, the mouse down - the main point of this exercise...
	function handleMouseDown (event) {
		//
		// Called when we get a click in the video - or possibly the surrounding <div> 
		// calculate where to position the video (audio).
		//
		// get where that click was... 
		lastxclick = event.clientX;
		lastyclick = event.clientY;

		console.log("MouseDown In - click status: " + clickStatus);
		console.log("playStatus: " + playStatus);
		// if we've just started, the first click starts us off...
		if ( playStatus == "Initial") {
			postInfo("Initial Click down");
			updatePoster('Pressed');
			return;
		} 
		/*
		// if we're paused... then just start playing from here...
		if ( playStatus == "Paused" ) {
			clickStatus = "Ready";	 // ignore the mouse up...
			playIt();
			return;	
		}
		*/
			
		//
		// check the full screen mode....
		checkFullscreenMode();
		console.log("Returned fullscreenStatus: " + fullscreenStatus);

		// we may have dropped out of full screen mode - if so, and this
		// was a document click, ignore it and wait for the next click to handle it...
		if ( clickType == 'Doc' && fullscreenStatus != 'FullscreenOn' ) {
			return;
		}

		currentLocation = whereAreWe();


		//   if we're not waiting for a second click...  set a time out..
		if ( clickStatus == "Ready") {
			var timeout=500;	// half a second..
			window.setTimeout(clickTimeout, timeout);
			// Pause the video
			//pauseIt();
			//video.pause();		// stop, but don't change the interface...
			//  move to the click..
			//video.currentTime = currentLocation;
			//video.play();
			clickStatus = "Down";
		} else if ( clickStatus == "Waiting" ) { // second click - pause
			console.log("Second click - pause...");
			pauseIt();
			//video.currentTime = currentLocation;
			clickStatus = "Ready";
		}
		console.log("MouseDown Out - click status: " + clickStatus);

	}
	// Mouse up...
	function handleMouseUp (event) {
		console.log("MouseUp In - click status: " + clickStatus);
		// if we've just started, the first click starts us off...
		if ( playStatus == "Initial") {
			playIt();
			postInfo("Initial Click up");
			console.log("MouseUp Out - clickStatus: " + clickStatus);
			return;
		} 
		//  if "Ready" then we're ignoring this mouse up..  (likely already paused)
		//  likely to change if pop-ups start happening.
		if ( clickStatus == "Ready" ) {
			console.log("MouseUp Out - clickStatus: " + clickStatus);
			return;
		}
		if ( clickStatus == "Down" ) {
			// let's start playing...  but indicate we're 
			// waiting for a possible second click..
			// we may want to locate as well, if we're dragging...
			if ( playStatus != "Paused" ) {
				video.currentTime = currentLocation;
			}
			playIt();
			clickStatus = "Waiting";
		}
		console.log("MouseUp Out - clickStatus: " + clickStatus);
	}	
	// click Timeout - time related mouse function
	function clickTimeout() {
		//
		// do some things based on our status...
		// if the mouse is still down we pause, and 
		// possibly throw up a box...
		// otherwise we just set the clickStatus back
		// to Ready
		console.log("Click timeout In - clickStatus = " + clickStatus);
		if (clickStatus == "Down") {
			pauseIt();
			video.currentTime = currentLocation;
			postInfo("Timeout - paused");
			// this is where we do a pull-down....
		}
		clickStatus = "Ready";	// ignore (for now) the next mouse up...
		console.log("Click timeout Out - clickStatus = " + clickStatus);
	}

	function whereAreWe() {
		// calculate where we are in 
		// the song, based on page / full view...
		// returns location a float: time in seconds from the beginning
		if ( fullscreenStatus == 'FullscreenOn' ) {
			// Full screen mode - this one gets tricky...
			//
			// TBD: determine orientation on iPads...   but no
			// hurry since the full screen mode does not pass
			// events...
			// 
			// First we decide how the video will scale, 
			// based aspect ratio.  Then we calculate the offset,
			// if any, and scale the start and end times.
			vert_ratio = screen.height / video.videoHeight;
			horiz_ratio = screen.width / video.videoWidth;
			// choose the smaller of the two...
	    		ratio = ( vert_ratio < horiz_ratio ) ? vert_ratio : horiz_ratio;
			// now calculate the offsets..
			var offset = screen.width - video.videoWidth * ratio;
			offset = offset / 2;
			if ( screenshotWidth != 'None' ) {
				mdscale = scrnwide / video.videoWidth;
			} else {
				mdscale = mdwide / video.videoWidth; 	// in case we don't get the expected video
			}
			console.log("mdscale: " + mdscale.toString());
			console.log("screenshot: " + screenshotWidth);
			start = xmin * ratio / mdscale;;
			end = xmax * ratio / mdscale;;

			console.log("start: " + start.toFixed(3) + "\nend: " + end.toFixed(3) + 
				"\noffset: " + offset.toFixed(3) + "\nratio: " + ratio.toFixed(3)  +
				"\nMedia Scale: " + mdscale.toFixed(3) +
				"\nVideo Width: " + video.videoWidth.toFixed() +
				"\nx-click: " + lastxclick.toString());
		} else  {	
			// in the web page player, we calculate
			// where we are in the song.   
			//    xval => where we are in the song in on-screen pixels
			//      (ranges from 0 to xlen)
			//    start, end are the scaled start and end offsets w/i graphic
			//    xlen = length of song in pixels:   xmax - xmin
			//
			var offset = xoff;
			var start = xmin / pscale;
			var end = xmax / pscale;
			console.log("\npscale: " + pscale.toString() );
		}
		//  we've got the start, end and length...
		//  where are we in the song....
		var xval = lastxclick - offset - start;
		var xlen = end - start;

		var xvalue = xval.toString();

		var time = dur * (xval / xlen);
		maxtime = dur - 0.25	// no point in setting it exactly at the end...
		if ( time < 0.0 ) {
			time = 0.0;
		} else if ( time > maxtime ) {
			time = maxtime;
		}
		console.log ("---whereAreWe---\nOffset: "  + offset.toString() +
			"\nStart: " + start.toString() +
			"\nEnd: " + end.toString() +
			"\nxval: " + xval.toString() +
			"\nxlen: " + xlen.toString() +
			"\noffset: " + offset.toFixed(3) + 
			"\nVideo Width: " + video.videoWidth.toFixed() +
			"\nx-click: " + lastxclick.toString() +
			"\ntime: " + time.toFixed(3) );
		postInfo("time:" + time.toFixed(3) + ' / ' + xvalue );
		return time;
	}
}

function displayAttrById (id) {
	//   let's see what attributes this element has...
	var element = document.getElementById(id);
	
	console.log("displayAttrById: attr for: " + id);
	Array.prototype.slice.call(element.attributes).forEach(function(item) {
		console.log(item.name + ': '+ item.value);
	});
};

// parseUri 1.2.2
// (c) Steven Levithan <stevenlevithan.com>
// MIT License

function parseUri (str) {
	var	o   = parseUri.options,
		m   = o.parser[o.strictMode ? "strict" : "loose"].exec(str),
		uri = {},
		i   = 14;

	while (i--) uri[o.key[i]] = m[i] || "";

	uri[o.q.name] = {};
	uri[o.key[12]].replace(o.q.parser, function ($0, $1, $2) {
		if ($1) uri[o.q.name][$1] = $2;
	});

	return uri;
};

parseUri.options = {
	strictMode: false,
	key: ["source","protocol","authority","userInfo","user","password","host","port","relative","path","directory","file","query","anchor"],
	q:   {
		name:   "queryKey",
		parser: /(?:^|&)([^&=]*)=?([^&]*)/g
	},
	parser: {
		strict: /^(?:([^:\/?#]+):)?(?:\/\/((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?))?((((?:[^?#\/]*\/)*)([^?#]*))(?:\?([^#]*))?(?:#(.*))?)/,
		loose:  /^(?:(?![^:@]+:[^:@\/]*@)([^:\/?#.]+):)?(?:\/\/)?((?:(([^:@]*)(?::([^:@]*))?)?@)?([^:\/?#]*)(?::(\d*))?)(((\/(?:[^?#](?![^?#\/]*\.[^?#\/.]+(?:[?#]|$)))*\/?)?([^?#\/]*))(?:\?([^#]*))?(?:#(.*))?)/
	}
};

