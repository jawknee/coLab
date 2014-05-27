window.onload = function() {

	// ----------------------------------------
	// 	Initial Assignments
	// ----------------------------------------
	// Status
	var status = "Initial";
	var fullscreenStatus = "Initial";
	var fullscreenMode = "unset";
	var lastxclick = -1;
	var lastyclick = -1;

	// Video
	var video = document.getElementById("video");
	var vcontainer = document.getElementById("video-container");
	var clickbar = document.getElementById("clickbar");
	var clickdiv = document.getElementById("clickdiv");

	// Buttons
	var playButton = document.getElementById("play-pause");
	var muteButton = document.getElementById("mute");
	var fullScreenButton = document.getElementById("full-screen");

	// Sliders
	var seekBar = document.getElementById("seek-bar");
	var volumeBar = document.getElementById("volume-bar");
	
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
	

	//  First - let's find our full screen requester...
	var fullscreenProperty = 'unset';
	if (video.requestFullscreen) {
		var fullscreenRequester = function () { video.requestFullscreen(); }	// Generic
		fullscreenMode = "Generic";
		fullscreenProperty = document.fullscreenEnabled;
	} else if (video.mozRequestFullScreen) {
		var fullscreenRequester = function () { video.mozRequestFullScreen(); } // Firefox
		fullscreenMode = "Mozilla";
		fullscreenProperty = document.mozFullScreenEnabled;
	} else if (video.webkitRequestFullscreen) {
		var fullscreenRequester = function () { video.webkitRequestFullscreen(); } // Chrome and Safari
		fullscreenMode = "Webkit";
		fullscreenProperty = document.webkitFullscreenEnabled;
	} else if (video.webkitEnterFullScreen) {
		var fullscreenRequester = function () { video.webkitEnterFullScreen(); } // Chrome and Safari
		fullscreenMode = "iOS";
		fullscreenProperty = document.fullscreenEnabled;  //  NO!  only a place holder
	} else if (video.msRequestFullscreen) {
		var fullscreenRequester = function () { video.msRequestFullscreen(); } // MS / IE
		fullscreenMode = "Microsoft";
		fullscreenProperty = document.msFullscreenEnabled;
	} else {
		fullscreenMode = "None";
	}

	// ----------------------------------------
	// 	Info output...
	// ----------------------------------------

	// a little something to keep us informed...
	function postInfo(msg) {
		var infoString = '<b>Status:</b> ' + status + '<br>' +
			'<b>Current:</b> ' + video.currentTime.toFixed(3) + '<br>' +
			'<b>Message:</b> ' + msg + '<br>' +
			'<b>Volume:</b> ' + video.volume.toString() + '<br>' ;
		if ( video.muted ) {
			infoString += '<b>Muted</b><br>'
		} else {
			infoString += '<b>Not Muted</b><br>'
		}

		infoString += "<b>video Source:</b> " + video.currentSrc.split('/').pop() + '<br>';
		infoString += "<b>videoWidth:</b> " + video.videoWidth.toString() + '<br>';
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
		infoString += "<b>Event Name:</b> " + eventlist + '<br>';
		infoString += "<b>Click Type:</b> " + clickType + '<br>';

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
			playButton.innerHTML = '<img src="/coLab/Resources/Icons/Play_24x24xp_02.png" alt="Play">';
		} else {
			playButton.innerHTML = '<img src="/coLab/Resources/Icons/Pause_24x24xp_01.png" alt="Pause">';
		}
	}

	setPlayButton();

	function setMuteButton() {
		if (video.muted == false) {
			muteButton.innerHTML = '<img src="/coLab/Resources/Icons/Unmuted_24x24xp_02.png" alt="Mute">';
		} else {
			muteButton.innerHTML = '<img src="/coLab/Resources/Icons/Muted_24x24xp_02.png"" alt="Unmute">';
		}
	}

	setMuteButton();

	function setFSButton() {
		if (fullscreenMode == "None" ) {
			fullScreenButton.innerHTML = '<img src="/coLab/Resources/Icons/NoFullScreen_24x24xp_01.png" alt="Mute">';
		} else {
			fullScreenButton.innerHTML = '<img src="/coLab/Resources/Icons/FullScreen_24x24xp_01.png" alt="Unmute">';
		}
	}

	setFSButton();

	// If set to the "Poster_Start.png" value, change
	// the poster to "Poster_Wait.png"
	function updatePoster() {

		var currentPoster = document.getElementById("video").poster;
		path = currentPoster.split('/');
		poster = path.pop()
		console.log("Update Poster: " + currentPoster + ' - ' + poster);
		if ( poster == "Poster_Start.png" ) {
			video.poster = "Poster_Waiting.png" ;
		}
		currentPoster = document.getElementById("video").poster;
		console.log("New poster? " + currentPoster);
	}


	//  start the video playing 
	function playIt() {
		if ( status == "Initial") {
			updatePoster();
		}
		video.play();
		status = "Playing";

		// Update the button text to 'Pause'
		//playButton.innerHTML = "Pause";
		setPlayButton();
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
			video.pause();
			status = "Paused";

			// Update the button text to 'Play'
			setPlayButton();
		}
		postInfo("Play button");
	});

	// Event listener for the mute button
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
	seekBar.addEventListener("change", function() {
		// Calculate the new time
		var time = video.duration * (seekBar.value / 100);

		// Update the video time
		video.currentTime = time;
	});

	
	// Update the seek bar as the video plays
	video.addEventListener("timeupdate", function() {
		// Calculate the slider value
		var value = (100 / video.duration) * video.currentTime;

		// Update the slider value
		seekBar.value = value;
		postInfo("update");
	});

	// when video completes, change the play button to "play"
	video.addEventListener("ended", function () {
		// done - just change the play button...
		// Update the button text to 'Play'
		status = "Ended";
		postInfo("Finished.");
		setPlayButton();
	});


	// Pause the video when the seek handle is being dragged
	seekBar.addEventListener("mousedown", function() {
		video.pause();
	});

	// Play the video when the seek handle is dropped
	seekBar.addEventListener("mouseup", function() {
		video.play();
		setPlayButton();
	});

	// Event listener for the volume bar
	volumeBar.addEventListener("change", function() {
		// Update the video volume
		video.volume = volumeBar.value;
	});


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
	}

	// Add the full-screen change handlers...
	video.addEventListener('webkitfullscreenchange', handleFullscreen, false );
	video.addEventListener('mozfullscreenchange', handleFullscreen, false );	// Doesn't work... handled in video.click
	video.addEventListener('fullscreenchange', handleFullscreen, false );

	function checkFullscreenMode () {
		//
		// Some special handling for Mozilla - it does not appear to be 
		// using mozfullscreenchange - so we test for it here...
		if ( fullscreenMode == "Generic" ) {
			if ( document.fullscreenElement &&  document.fullscreenElement.nodeName == 'VIDEO'  ) {
				console.log('Your Generic video is playing in fullscreen');
				fullscreenStatus = 'FullscreenOn';
			} else {
				console.log('Your Generic video is playing in pageview');
				fullscreenStatus = 'FullscreenOff';
				setPlayButton();
			}
		}
		if ( fullscreenMode == 'Mozilla' ) {
			if ( document.mozFullScreenElement && document.mozFullScreenElement.nodeName == 'VIDEO') {
				console.log('Your Mozilla video is playing in fullscreen');
				fullscreenStatus = 'FullscreenOn';
			} else {
				console.log('Your Mozilla video is playing in pageview');
				fullscreenStatus = 'FullscreenOff';
				setPlayButton();
			}
		}
	
		if ( fullscreenMode == 'Webkit' ) {
			if ( document.webkitFullscreenElement &&  document.webkitFullscreenElement.nodeName == 'VIDEO'  ) {
				console.log('Your webkit video is playing in fullscreen');
				fullscreenStatus = 'FullscreenOn';
			} else {
				console.log('Your webkit video is playing in pageview');
				fullscreenStatus = 'FullscreenOff';
				setPlayButton();
			}
		}
		// And likewise with Microsoft / IE
		if ( fullscreenMode == 'Microsoft' ) {
			if ( document.msFullscreenElement &&  document.msFullscreenElement.nodeName == 'VIDEO'  ) {
				console.log('Your MS/IE video is playing in fullscreen');
				fullscreenStatus = 'FullscreenOn';
			} else {
				console.log('Your MS/IE video is playing in pageview');
				fullscreenStatus = 'FullscreenOff';
				setPlayButton();
			}
		}
	}



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
	// Set up handlers for the varrious clicks..
	//
	// video - this is the one we want, if we can get it
	video.addEventListener("click", function(e) {
		console.log("video click" + clickType);
		eventlist += 'v';
		if ( clickType != 'div' ) {
			handleClick(e);
			eventlist += '+';
		}
		clickType = 'video';
		postInfo("Video Click");
		}, true);
	//
	//  div - possibly redundant   secondary to video
	clickdiv.addEventListener("click", function(e) {
		console.log("div click" + clickType);
		eventlist += 'd';
		if ( clickType != 'video' ) {
			if ( clickType != 'Doc' ) {
				handleClick(e);
				eventlist += '+';
			}
			clickType = 'div';
		}
		postInfo("Div Click");
		}, true);
	
	// click in the whole document - ignore other than in
	// full screen - needed as some video elements to 
	// not pass through clicks.  At least sometimes, the
	// document does.
	document.addEventListener("click", function(e) {
		console.log("doc click" + clickType);
		eventlist += 'D';
		if ( clickType != 'video' && clickType != 'div' && fullscreenStatus == 'FullscreenOn' ) {
			clickType = 'Doc';
			handleClick(e);
			eventlist += '+';
		}
		postInfo("Document Click");
		}, false);
	
	// handle the click - the main point of this exercise...
	function handleClick (event) {
		//
		// Called when we get a click in the video - or possibly the surrounding <div> 
		// calculate where to position the video (audio).
		//
		// get where that click was... 
		lastxclick = event.clientX;
		lastyclick = event.clientY;

		// if we've just started, the first click starts us off...
		if ( status == "Initial") {
			playIt();
			postInfo("Initial Click");
			return;
		} 
		//
		// check the full screen mode....
		checkFullscreenMode();

		// we may have dropped out of full screen mode - if so, and this
		// was a document click, ignore it and wait for the next click to handle it...
		if ( clickType == 'Doc' && fullscreenStatus != 'FullscreenOn' ) {
			return
		}

		// calculate where we are in 
		// the song, based on page / full view...
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
		console.log ("---Time---\nOffset: "  + offset.toString() +
			"\nStart: " + start.toString() +
			"\nEnd: " + end.toString() +
			"\nxval: " + xval.toString() +
			"\nxlen: " + xlen.toString() +
			"\noffset: " + offset.toFixed(3) + 
			"\nVideo Width: " + video.videoWidth.toFixed() +
			"\nx-click: " + lastxclick.toString() +
			"\ntime: " + time.toFixed(3) );

		// Pause the video
		//video.pause();
		//  move to the click..
		video.currentTime = time;
		// and start playing again - but only if we were playing..
		//if ( status == "Playing" || fullscreenStatus == 'FullscreenOn' ) {
		if ( status == "Paused" || fullscreenStatus == 'FullscreenOn' ) {
			playIt();
		}
		postInfo("time:" + time.toFixed(3) + ' / ' + xvalue );
	}

}
