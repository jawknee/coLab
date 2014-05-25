window.onload = function() {

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
	var duration = document.getElementById("duration").value;
	var xOffset = document.getElementById("xOffset").value;
	var xStart = document.getElementById("xStart").value;
	var xEnd = document.getElementById("xEnd").value;
	var pageScale = document.getElementById("pageScale").value;

	var dur = parseFloat(duration);
	var xoff = parseInt(xOffset);
	var xmin = parseInt(xStart);
	var xmax = parseInt(xEnd);
	var pscale = parseFloat(pageScale);

	//  First - let's find our full screen requester...
	if (video.requestFullscreen) {
		var fullscreenRequester = function () { video.requestFullscreen(); }	// Generic
		fullscreenMode = "Generic";
	} else if (video.mozRequestFullScreen) {
		var fullscreenRequester = function () { video.mozRequestFullScreen(); } // Firefox
		fullscreenMode = "Mozilla";
	} else if (video.webkitRequestFullscreen) {
		var fullscreenRequester = function () { video.webkitRequestFullscreen(); } // Chrome and Safari
		fullscreenMode = "Webkit";
	} else if (video.msRequestFullscreen) {
		var fullscreenRequester = function () { video.msRequestFullscreen(); } // MS / IE
		fullscreenMode = "Microsoft";
	} else {
		fullscreenMode = "None";
	}


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

		infoString += "<b>videoWidth:</b> " + video.videoWidth.toString() + '<br>';
		infoString += "<b>videoDurtn:</b> " + video.duration.toFixed(3) + '<br>';
		infoString += "<b>ActualDurtn:</b> " + dur.toFixed(3) + '<br>';

		infoString += "<b>Last Click:</b> (" + lastxclick.toString() + ', ' + lastyclick.toString()  + ') <br>';
		infoString += "xOffset: " + xOffset.toString() + '<br>';
		infoString += "xStart: " + xStart.toString() + '<br>';
		infoString += "xEnd: " + xEnd.toString() + '<br>';
		infoString += "xmin/max: " + xmin.toString() + ', ' + xmax.toString() + '<br>';
		infoString += "Screen width: " + screen.width.toString() + '<br>';
		infoString += "Screen height: " + screen.height.toString() + '<br>';
		infoString += "Fullscreen: " + fullscreenStatus + '<br>';
		infoString += "Fullscreen Mode: " + fullscreenMode + '<br>';
		infoString += "<b>Event Name:</b> " + eventlist + '<br>';
		infoString += "<b>Click Type:</b> " + clickType + '<br>';

		infoText.innerHTML = infoString;
	}

	// let's get the info up to date...
	postInfo("Page loaded.");
	function setPlayButton() {
		if ( video.paused == true ) {
			playButton.innerHTML = '<img src="/coLab/Resources/Icons/Play_24x24xp_01.png" alt="Play">';
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



	function playIt() {
		video.play();
		status = "Playing";

		// Update the button text to 'Pause'
		//playButton.innerHTML = "Pause";
		setPlayButton();
	}

	// Event listener for the play/pause button
	playButton.addEventListener("click", function() {
		if (video.paused == true) {
			playIt();
		} else {
			// Pause the video
			video.pause();
			status = "Paused";

			// Update the button text to 'Play'
			//playButton.innerHTML = "Play";
			setPlayButton();
		}
		postInfo("Play button");
	});


	// a click in the vicinity of the graphic - 
	// position play based on that...
	clickdiv.addEventListener("click", function(e) {
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

	video.addEventListener("click", function(e) {
		eventlist += 'v';
		if ( clickType != 'div' ) {
			handleClick(e);
			eventlist += '+';
		}
		clickType = 'video';
		postInfo("Video Click");
		}, true);
	
	// document?
	document.addEventListener("click", function(e) {
		eventlist += 'D';
		if ( clickType != 'video' && clickType != 'div' ) {
			clickType = 'Doc';
			handleClick(e);
			eventlist += '+';
		}
		postInfo("Document Click");
		}, false);
	

	function handleClick (event) {
		//
		// Called when we get a click in the video - or possibly the surrounding 
		// <div> calculate where to position the video (audio).
		//
		// get where that click was... 
		lastxclick = event.clientX;
		lastyclick = event.clientY;

		if ( status == "Initial") {
			playIt();
			postInfo("Initial Click");
			return
		} 
		if ( fullscreenMode == 'Mozilla' ) {
			if (document.mozFullScreenElement && document.mozFullScreenElement.nodeName == 'VIDEO') {
				console.log('Your Mozilla video is playing in fullscreen');
				fullscreenStatus = 'FullscreenOn';
			} else {
				console.log('Your Mozilla video is playing in pageview');
				fullscreenStatus = 'FullscreenOff';
			}
		}
				


		// calculate where we are in 
		// the song, based on page / full view...
		if ( fullscreenStatus == 'FullscreenOn' ) {
			// Full screen mode - this one gets tricky...
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
			start = xmin * ratio;
			end = xmax * ratio;

			var debug = 'yes';
			if ( debug == 'yes' ) {
				alert ("start: " + start.toFixed(3) + "\nend: " + end.toFixed(3) + 
					"\noffset: " + offset.toFixed(3) + "\nratio: " + ratio.toFixed(3)  +
					"\nx-click: " + lastxclick.toString());
			}

		} else {	
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
		}
		//  we've got the start, end and length...
		//  where are we in the song....
		var xval = lastxclick - offset - start;
		var xlen = end - start;

		var xvalue = xval.toString();

		var time = dur * (xval / xlen);
		maxtime = dur - 0.5	// no point in setting it exactly at the end...
		if ( time < 0.0 ) {
			time = 0.0;
		} else if ( time > maxtime ) {
			time = maxtime;
		}

		// Pause the video
		video.pause();
		//  move to the click..
		video.currentTime = time;
		// and start playing again - but only if we were playing..
		if ( status == "Playing" ) {
			playIt();
		}
		postInfo("time:" + time.toFixed(3) + ' / ' + xvalue );
	}

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
			alert("Your browser does not support the Full Screen Mode API.")
		}
		video.removeAttribute("controls")
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
		//postInfo("update");
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
	
		video.removeAttribute("controls")
	}

	// Add the full-screen change handlers...
	video.addEventListener('webkitfullscreenchange', handleFullscreen, false );
	video.addEventListener('mozfullscreenchange', handleFullscreen, false );	// Doesn't work... handled in video.click
	video.addEventListener('fullscreenchange', handleFullscreen, false );

}
