var SCREEN_WIDTH = window.innerWidth;
var SCREEN_HEIGHT = window.innerHeight;
var container, stats;
var camera, fpCamera, scene, renderer, controls, cameraTarget;
var firstPerson, started, displayTranslation, paused, cancelled, done = false;

var skinnedMesh;

// animation stuff
var mixer,manual_clips, non_manual_clips; // make them global for testing
var animation_speed = 1.0;  // standard speed -> will be 1 for everything and 1.5 for the signs that seem a bit slow

var clock = new THREE.Clock();

var Interface = new INTERFACE();
var URL = new URLS();

//testing
var sorted, firstStep, continuousStep, finalStep = false;
var fadeCounter = 1;

init();
animate();

function init() {

    manual_clips = new Array;

    container = document.createElement( 'div' );
    document.body.appendChild( container );

    // SCENE

    scene = new THREE.Scene();

    // cameraHelper = new THREE.CameraHelper(fpCamera);
    // scene.add(cameraHelper);

    // LIGHTS

    var light = new THREE.DirectionalLight( 0xaabbff, 0.3 );
    light.position.x = 300;
    light.position.y = 250;
    light.position.z = 500;
    scene.add( light );

    light = new THREE.DirectionalLight( 0xaabbff, 0.3 );
    light.position.x = 0;
    light.position.y = 250;
    light.position.z = 0;
    scene.add( light );

    // var sphereSize = 1;
    // var pointLightHelper = new THREE.DirectionalLightHelper( light, sphereSize );
    // scene.add( pointLightHelper );

    var ambient = new THREE.AmbientLight( 0x404040 ); // soft white light
    scene.add( ambient );

    // SKYDOME

    var vertexShader = document.getElementById( 'vertexShader' ).textContent;
    var fragmentShader = document.getElementById( 'fragmentShader' ).textContent;
    var uniforms = {
        topColor: 	 { type: "c", value: new THREE.Color( 0x0077ff ) },
        bottomColor: { type: "c", value: new THREE.Color( 0xffffff ) },
        offset:		 { type: "f", value: 400 },
        exponent:	 { type: "f", value: 0.6 }
    };
    uniforms.topColor.value.copy( light.color );

    var skyGeo = new THREE.SphereGeometry( 4000, 32, 15 );
    var skyMat = new THREE.ShaderMaterial( {
        uniforms: uniforms,
        vertexShader: vertexShader,
        fragmentShader: fragmentShader,
        side: THREE.BackSide
    } );

    var sky = new THREE.Mesh( skyGeo, skyMat );
    scene.add( sky );

    // RENDERER

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
    container.appendChild( renderer.domElement );

    renderer.gammaInput = true;
    renderer.gammaOutput = true;

    // STANDARD CAMERA

    camera = new THREE.PerspectiveCamera( 30, SCREEN_WIDTH / SCREEN_HEIGHT, 1, 10000 );
    camera.position.set(0, 5, 10 );
    //camera.up.set(0,0,1);
    cameraTarget = new THREE.Mesh( new THREE.CubeGeometry(0,0,0)); // so that the camera follows the head correctly
    cameraTarget.position.y = 4;

    // FIRST PERSON CAMERA

    fpCamera = new THREE.PerspectiveCamera( 80, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 10000);
    fpCamera.position.set(0, 3.7, 0.15 );
    fpCamera.lookAt(new THREE.Vector3(0,0,10));

    // CONTROLS

    controls = new THREE.OrbitControls( camera, renderer.domElement );
    controls.minDistance = 7;   // reduce zooming options (so that we cannot see inside the model)
    controls.maxDistance = 15;
    controls.maxPolarAngle = 0.9 * Math.PI / 2;

    controls.update();

    // STATS
    stats = new Stats();
    container.appendChild( stats.domElement );

    // MODEL
    $.getJSON(URL.model, function(json){

        var matLoader = new THREE.ObjectLoader(); // this loader will be used to parse JSON textures into THREE textures

        // the following sequence is analogous to the source code
        matLoader.texturePath = URL.model.substring( 0, URL.model.lastIndexOf( '/' ) + 1 );
        var images = matLoader.parseImages(json.images);
        var textures = matLoader.parseTextures(json.textures, images);
        var threeMaterials = matLoader.parseMaterials(json.materials, textures);

        /** EVERYTHING ELSE BELOW WORKS FINE **/
        // first load all the materials needed (as ObjectLoader does not support multiple materials)

        var materials = [];
        for(var mat = 0; mat < json.geometries[0].materials.length; mat++){
            var name = json.geometries[0].materials[mat].DbgName;
            var material;
            for(var id in threeMaterials){
                if(threeMaterials[id].name == name){
                    material = threeMaterials[id];
                    break;
                }
            }
            materials.push(new THREE.MeshPhongMaterial(material));
            materials[mat].skinning = true;
            materials[mat].side = THREE.DoubleSide; // make all faces double sided (messes up for some)
        }
        loadModel(materials);
    });
    window.addEventListener( 'resize', onWindowResize, false );
}

function loadModel(materials){
    var loader = new THREE.ObjectLoader();
    loader.load(URL.model, function ( object ) {
        skinnedMesh = new THREE.SkinnedMesh(object.children[0].geometry, new THREE.MeshFaceMaterial(materials));
        scene.add(skinnedMesh);
        //helper = new THREE.SkeletonHelper( skinnedMesh );
        //helper.material.linewidth = 3;
        //scene.add( helper );
        mixer = new THREE.AnimationMixer(skinnedMesh);    // set up the mixer
        setupAnimations(URL.base);   // we initalise the base url (the other two will obviously be empty)
    });
}

// the next function is to test the concatenation/mixing
function setupAnimations(urlArray){
    //urls = ['blinking', 'idle','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];  // array containing all animations required for the clip
    // first do the manual features
    var counter = 0;
    for(var i = 0; i < urlArray.length; i++) {
        (function (i) {
            console.log(urlArray[i].name);
            var animations_url = '../static/res/animations/' + urlArray[i].path + '/' + urlArray[i].name + '.js';
            $.getJSON(animations_url, function (json) {
                clip = THREE.AnimationClip.parseAnimation(json.animations[0], json.bones);
                if (urlArray[i].path == 'numbers' || urlArray[i].path == 'alphabet'){
                    mixer.clipAction(clip).timeScale = 1.5;
                }
                counter++;
                updateManualClipList({clip: clip, index: urlArray[i].index}, i);
                if (counter == urlArray.length) {    // once we have loaded all the manual_clips, go on to modify them
                    if (!started) playInit();
                    else {
                        if (URL.non_manual_names.length > 0) { // if no non manuals are needed, skip this step
                            console.log('done loading manual', manual_clips);
                            setupNonManual();
                        }
                        else {
                            console.log('done loading manual', manual_clips);
                            displayTranslation = true;
                        }
                    }
                }
            });
        })(i);
    }
}

// this function sets up the non-manual animations for the clips
function setupNonManual(){
    var counter = 0;
    for(var i = 0; i < URL.non_manual_names.length; i++) {
        (function (i) {
            var animations_url = '../static/res/animations/non-manual/' + URL.non_manual_names[i] + '.js';
            $.getJSON(animations_url, function (json) {
                console.log('gonna load clip');
                console.log(json.animations);
                clip = THREE.AnimationClip.parseAnimation(json.animations[0], json.bones);
                counter++;
                updateNonManualClipList(clip);
                if (counter == URL.non_manual_names.length) {    // once we have loaded all the non_manual_clips, go on to the next step
                    console.log('done loading non manual', non_manual_clips);
                    displayTranslation = true;
                }
            });
        })(i);
    }
}

function updateManualClipList(clip, index){
    if(!started) {      // if we are still loading the initial animations
        manual_clips.splice(index, 0, clip);   // insert object
    }
    else{
        manual_clips.splice(index+2, 0, clip);   // insert object 2 indexes further
    }
}

function updateNonManualClipList(clip){

    NON_MAN_VARS.clips_list.push(clip);       // used to keep track of playing status

    for (i = 0; i<non_manual_clips.length; i++){
        for (j = 0; j<non_manual_clips[i].start.length; j++){     // start
            if (non_manual_clips[i].start[j] == clip.name) {
                non_manual_clips[i].start[j] = clip;      // replace with clip object
            }
        }
        for (j = 0; j<non_manual_clips[i].end.length; j++){   // end
            if (non_manual_clips[i].end[j] == clip.name) {
                non_manual_clips[i].end[j] = clip;      // replace with clip object
            }
        }
    }
}

function playInit(){
    // play idle and blinking first
    mixer.clipAction(manual_clips[0].clip).play();  // play blinking and idle
    mixer.clipAction(manual_clips[1].clip).play();
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    fpCamera.aspect = window.innerWidth / window.innerHeight;
    fpCamera.updateProjectionMatrix();
    renderer.setSize( window.innerWidth, window.innerHeight );
}

function resetClipAndUrlArrays(){
    URL.reset();      // reset animation urls
    manual_clips.length = 2;   // remove all elements except the first two (idle and blinking)
    NON_MAN_VARS.clips_list = [];
}

function playAnimationSequence(){

    /** first step **/
    if(firstStep){
        console.log("at first step");

        // set up the next clip to be interpolated
        mixer.clipAction(manual_clips[fadeCounter+1].clip).setLoop(THREE.LoopOnce);
        mixer.clipAction(manual_clips[fadeCounter+1].clip).timeScale *= animation_speed;        // set to speed with general
        mixer.clipAction(manual_clips[fadeCounter+1].clip).reset();
        mixer.clipAction(manual_clips[fadeCounter+1].clip).play();
        mixer.clipAction(manual_clips[fadeCounter].clip).crossFadeTo(mixer.clipAction(manual_clips[fadeCounter+1].clip), 0.6, false);

        // set interface changes
        colorGloss();

        fadeCounter++;
        firstStep = false;
        continuousStep = true;
    }

    if(continuousStep){
        if(URL.manual.length > 1) {  // if we only have to play 1 animation, we skip the middle step

            // TEMPORARY REMOVE LATER
            // REMEMBER TO PAUSE LIKE BELOW FOR NON MANUAL CLIPS

            // if the current clip has reached the end we pause it to have time to fade to the next one
            if (mixer.clipAction(manual_clips[fadeCounter].clip).time > (manual_clips[fadeCounter].clip.duration - 0.1)) {
                mixer.clipAction(manual_clips[fadeCounter].clip).paused = true;  // pause current clip

                // if the same letter repeats, we need to change its name
                if(manual_clips[fadeCounter].clip.name == manual_clips[fadeCounter+1].clip.name){
                    manual_clips[fadeCounter+1].clip.name += '_1';
                    console.log(manual_clips[fadeCounter+1].clip.name);
                }

                // setup next clip like in first step
                mixer.clipAction(manual_clips[fadeCounter + 1].clip).setLoop(THREE.LoopOnce);
                mixer.clipAction(manual_clips[fadeCounter+1].clip).timeScale *= animation_speed;        // set to speed with general
                mixer.clipAction(manual_clips[fadeCounter + 1].clip).reset();
                mixer.clipAction(manual_clips[fadeCounter + 1].clip).play();
                mixer.clipAction(manual_clips[fadeCounter].clip).crossFadeTo(mixer.clipAction(manual_clips[fadeCounter + 1].clip), 0.6, false);

                // set interface changes
                colorGloss();

                if (fadeCounter == URL.manual.length) {   // if we reached the end of the animations, go to final step
                    continuousStep = false;
                    finalStep = true;
                }
                fadeCounter++;
            }
        }
        else{
            continuousStep = false;
            finalStep = true;
        }
    }

    /** final step **/
    if(finalStep){

        // pause clip to have time to fade
        if(mixer.clipAction(manual_clips[fadeCounter].clip).time > (manual_clips[fadeCounter].clip.duration-0.1)) { // this line is identical
            console.log("at final step");
            mixer.clipAction(manual_clips[fadeCounter].clip).paused = true;
            mixer.clipAction(manual_clips[1].clip).reset();     // assuming idle is the second clip ALWAYS
            mixer.clipAction(manual_clips[fadeCounter].clip).crossFadeTo(mixer.clipAction(manual_clips[1].clip), 0.6, false);

            // set interface changes
            Interface.resetAllGloss();

            playNonManualSequence(NON_MAN_VARS.current_index+1);        // last step to finish off then stop

            finalStep = false;
            done = true; // this way we also set the start button back
        }
    }
}

function playNonManualSequence(sign_index){

    if (sign_index != NON_MAN_VARS.current_index){      // if we change sign
        console.log('sign_index '+sign_index);
        nonManualLoop(sign_index);                                // go through the non manual loop to set clips
        NON_MAN_VARS.current_index = sign_index;        // update sign index
    }

}

function nonManualLoop(sign_index){

    if (sign_index < non_manual_clips.length && sign_index >= 0) {
        // for any clip that begins at this point (given by the clip index that is playing)
        var clips = non_manual_clips[sign_index].start;
        for (i = 0; i < clips.length; i++) {
            mixer.clipAction(clips[i]).reset();
            mixer.clipAction(clips[i]).setLoop(THREE.LoopOnce);
            mixer.clipAction(clips[i]).play();
        }
    }

    sign_index--;   // go down one to access the ending feature from the previous sign

    if (sign_index >= 0) {
        // for any clip ending at this point
        clips = non_manual_clips[sign_index].end;
        for (i = 0; i < clips.length; i++) {
            console.log('stopping '+clips[i].name);
            mixer.clipAction(clips[i]).fadeOut(0.5);
        }
    }
}

function checkStatusNonManualClips(){
    var clips = NON_MAN_VARS.clips_list;
    for (i = 0; i < clips.length; i++){
        if (mixer.clipAction(clips[i]).time > (clips[i].duration - 0.1)) {
            mixer.clipAction(clips[i]).paused = true;  // pause current clip
        }
    }
}

function animate() {

    requestAnimationFrame( animate );

    if(displayTranslation){ // for testing, will normally be activated once the animation sequence has been formed
        console.log('starting');

        Interface.disableSpinner('cssload-container');  // stop loading

        // begin fadeCounter for manual clips
        fadeCounter = 1;
        firstStep = true;
        displayTranslation = false;    // avoid repeating this multiple times
    }

    playAnimationSequence();

    if(mixer) {
        mixer.update(clock.getDelta());

        // should move all of this somewhere else
        if(firstStep || continuousStep || finalStep) {
            if (paused) {
                mixer.clipAction(manual_clips[0].clip).paused = true;      // also stop the blinking : will have to apply to all animations (facial expressions etc)
                mixer.clipAction(manual_clips[fadeCounter].clip).paused = true;
            }
            else {
                mixer.clipAction(manual_clips[0].clip).paused = false;      // put back blinking
                mixer.clipAction(manual_clips[fadeCounter].clip).paused = false;
            }

            if (!finalStep && NON_MAN_VARS.clips_list.length > 0) {      // no point in doing this if the lists are empty){
                playNonManualSequence(manual_clips[fadeCounter].index); // get the current clip index and pass it
                checkStatusNonManualClips();        // for pausing
            }

        }

        // if cancelled reset all variables to initial state
        if(cancelled){
            resetAllManualVars();
        }

        // reset variables to first state
        if(done){
            Interface.play_pause_button.pause();     // set back to play
            done = false;
            started = false;
            console.log(paused, cancelled, done, started);
        }
    }

    camera.lookAt(cameraTarget.position);
    render();
    stats.update();
}

function render() {
    if(firstPerson) {
        renderer.render(scene, fpCamera);
    }
    else{
        renderer.render(scene, camera);
    }
}

function resetAllManualVars(){
    firstStep = false;
    continuousStep = false;
    finalStep = true;
    paused = false;     // stop the pause before going back to idle
    cancelled = false;
    done = true;
    started = false;
}

function colorGloss(){
    //console.log(fadeCounter);
    Interface.highlightGloss(fadeCounter-1);    // temporary solution for accessing the div id,
    Interface.resetGloss(fadeCounter-2);        // could also set the id directly to match fadeCounter?
}

/// INTERFACE RELATED STUFF

$('#translate').on('click', function() {

    console.log("clicked start");

    var text = $('input[name="input_text"]').val();

    // start loading animation

    if (Interface.current_text != text) {

        Interface.enableSpinner('cssload-container');

        Interface.current_text = text; // update text

        // get the text from the textbox and send it to python
        $.getJSON('/_process_text', {
            input_text: text
        }, function (data) {

            console.log(data);

            Interface.setGloss('bsl', data.result[0]);     // print the result on screen (gloss)

            // once the animations starts playing we set the button to pause
            //Interface.play_pause_button.pause();

            // use data.result[1] for the rest
            console.log(data.result, URL.manual);

            resetClipAndUrlArrays();

            manual = data.result[1][0];
            non_manual_names = data.result[1][1];
            non_manual = data.result[1][2];
            modifiers = data.result[1][3];

            for (i = 0; i < manual.length; i++) {
                URL.manual.push(JSON.parse(manual[i]));  // convert json object from string representation to json object (could be different length)
            }

            URL.non_manual_names = JSON.parse(non_manual_names).anims;  // convert json object from string representation to json object (could be different length)

            for (i = 0; i < non_manual.length; i++) {
                URL.non_manual.push(JSON.parse(non_manual[i]));
                URL.modifiers.push(JSON.parse(modifiers[i]));
            }
            console.log(URL.manual, URL.non_manual_names, URL.non_manual, URL.modifiers);

            non_manual_clips = URL.non_manual;
            Interface.gloss_length = URL.manual.length;

            started = true;
            setupAnimations(URL.manual);

        });
    }
    else {
        console.log('text is the same');
        started = true;
        displayTranslation = true;
    }
});

$('#swap').on('click', function() {
    firstPerson = !firstPerson;
});

$('#stop').on('click', function() {
    if(started){
        cancelled = true;
        //Interface.play_pause_button.pause(); // set back the play icon
    }
});

$('#play-pause').on('click', function(){
    // will add if (animation.playing) {  or something, otherwise you cant switch or click
    if(started) {
        paused = !paused;
        console.log(paused);
        Interface.play_pause_button.switch();   // switch icons
    }
});