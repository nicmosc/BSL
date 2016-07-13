var SCREEN_WIDTH = window.innerWidth;
var SCREEN_HEIGHT = window.innerHeight;
var container, stats;

var camera, fpCamera, controls, cameraTarget;

var clock = new THREE.Clock();

var Engine = new ENGINE();
var Interface = new INTERFACE();        // to access the front end

Engine.init(SCREEN_HEIGHT, SCREEN_WIDTH);

function init() {

    window.addEventListener( 'resize', onWindowResize, false );
}

/// INTERFACE RELATED STUFF

$('#translate').on('click', function() {

    var text = '';

    console.log("clicked start");

    // start loading animation
    Interface.enableSpinner('cssload-container');

    // get the text from the textbox and send it to python
    $.getJSON('/_process_text', {
        input_text: $('input[name="input_text"]').val()
    }, function(data) {

        console.log(data);

        Interface.setGloss('bsl', data.result);     // print the result on screen
        Interface.disableSpinner('cssload-container');  // stop loading: will move this somewhere else when animations are working

        // once the animations starts playing we set the button to pause
        Interface.play_pause_button.pause();

        // if(JSON.stringify(data.result) != JSON.stringify(urls)) {
        //     console.log(data.result, urls);
        //     resetClipAndUrlArrays();    // not necessary if the sentence is the same exactly (we can just check urls)
        //     for(i = 0; i < data.result.length; i++){
        //         urls.push(JSON.parse(data.result[i]));  // convert json object from string representation to json object
        //     }
        //     console.log(urls);
        //     started = true;
        //     setupAnimations(urls);
        // }
        // else{
        //     displayTranslation = true;
        //     console.log("text is still the same");
        // }
    });

    // else {
    //     paused = !paused;
    //     if (this.innerHTML == 'pause') this.innerHTML = 'play';
    //     else this.innerHTML = 'pause';
    // }
    // remember that on first click we make 'cancel' visible
    //document.getElementById('cancel').style.visibility = 'visible';
});

$('#swap').on('click', function() {
    firstPerson = !firstPerson;
});

$('#stop').on('click', function() {
    cancelled = true;
    Interface.play_pause_button.play(); // set back the play icon
    //paused = !paused;
});

$('#play-pause').on('click', function(){
    // will add if (animation.playing) {  or something, otherwise you cant switch or click
    Interface.play_pause_button.switch();   // switch icons
});