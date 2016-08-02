var SCREEN_WIDTH = window.innerWidth;
var SCREEN_HEIGHT = window.innerHeight;
var container, stats;
var camera, scene, renderer, controls, camera_target;
// var fpCamera;
var first_person, started, display_translation, paused, cancelled, done = false;  // animation loop variables

var skinned_mesh;    // holds the model

// animation stuff
var mixer, manual_clips, non_manual_clips; // make them global for testing
var animation_speed = 1.0;  // standard speed -> will be 1 for everything and 1.5 for the signs that seem a bit slow
var interpolation_speed = 0.5;

var clock = new THREE.Clock();

var Interface = new INTERFACE();
var URL = new URLS();

// non-manual variable holders
NON_MAN_VARS = {
    current_index: -1,
    clips_list: []
};

CAM_VARS = {
    position: {x: 0, y: 5, z: 10},
    fov: 30,
    near: 1,
    targetZ: 0,
    targetY: 4,
    controls_enabled: true
};

FPS_CAM_VARS = {
    position: {x: 0, y: 3.5, z: 0.15},
    fov: 80,
    near: 0.1,
    targetZ: 10,
    targetY: 0,
    controls_enabled: false
};

// for swaping camera
var position_tween, camera_tween, target_tween;
var auto_cam = false;  // for automatic camera
var swap_counter = 1;

//testing
var sorted, firstStep, continuousStep, finalStep = false;
var fadeCounter = 1;

init();
animate();

function init() {

    manual_clips = new Array;

    container = document.createElement('div');
    document.body.appendChild(container);

    // SCENE

    scene = new THREE.Scene();

    // LIGHTS

    var light = new THREE.DirectionalLight(0xaabbff, 0.3);
    light.position.x = 300;
    light.position.y = 250;
    light.position.z = 500;
    scene.add(light);

    light = new THREE.DirectionalLight(0xaabbff, 0.3);
    light.position.x = 0;
    light.position.y = 250;
    light.position.z = 0;
    scene.add(light);

    var ambient = new THREE.AmbientLight(0x404040); // soft white light
    scene.add(ambient);

    // SKYDOME

    var vertexShader = document.getElementById('vertexShader').textContent;
    var fragmentShader = document.getElementById('fragmentShader').textContent;
    var uniforms = {
        topColor: {type: "c", value: new THREE.Color(0x0077ff)},
        bottomColor: {type: "c", value: new THREE.Color(0xffffff)},
        offset: {type: "f", value: 400},
        exponent: {type: "f", value: 0.6}
    };
    uniforms.topColor.value.copy(light.color);

    var skyGeo = new THREE.SphereGeometry(4000, 32, 15);
    var skyMat = new THREE.ShaderMaterial({
        uniforms: uniforms,
        vertexShader: vertexShader,
        fragmentShader: fragmentShader,
        side: THREE.BackSide
    });

    var sky = new THREE.Mesh(skyGeo, skyMat);
    scene.add(sky);

    // RENDERER

    renderer = new THREE.WebGLRenderer({antialias: true});
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(SCREEN_WIDTH, SCREEN_HEIGHT);
    container.appendChild(renderer.domElement);

    renderer.gammaInput = true;
    renderer.gammaOutput = true;

    // STANDARD CAMERA
    camera = new THREE.PerspectiveCamera(CAM_VARS.fov, SCREEN_WIDTH / SCREEN_HEIGHT, CAM_VARS.near, 10000);
    camera.position.set(0, CAM_VARS.position.y, CAM_VARS.position.z);

    camera_target = new THREE.Mesh(new THREE.CubeGeometry(0, 0, 0)); // so that the camera follows the head correctly
    camera_target.position.y = 4;

    // CONTROLS

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.minDistance = 7;   // reduce zooming options (so that we cannot see inside the model)
    controls.maxDistance = 15;
    controls.maxPolarAngle = 0.9 * Math.PI / 2;

    controls.update();

    // STATS
    stats = new Stats();
    container.appendChild(stats.domElement);

    // MODEL
    $.getJSON(URL.model, function (json) {

        var matLoader = new THREE.ObjectLoader(); // this loader will be used to parse JSON textures into THREE textures

        // the following sequence is analogous to the source code
        matLoader.texturePath = URL.model.substring(0, URL.model.lastIndexOf('/') + 1);
        var images = matLoader.parseImages(json.images);
        var textures = matLoader.parseTextures(json.textures, images);
        var threeMaterials = matLoader.parseMaterials(json.materials, textures);

        /** EVERYTHING ELSE BELOW WORKS FINE **/
        // first load all the materials needed (as ObjectLoader does not support multiple materials)

        var materials = [];
        for (var mat = 0; mat < json.geometries[0].materials.length; mat++) {
            var name = json.geometries[0].materials[mat].DbgName;
            var material;
            for (var id in threeMaterials) {
                if (threeMaterials[id].name == name) {
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
    window.addEventListener('resize', onWindowResize, false);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function loadModel(materials) {
    var loader = new THREE.ObjectLoader();
    loader.load(URL.model, function (object) {
        skinned_mesh = new THREE.SkinnedMesh(object.children[0].geometry, new THREE.MeshFaceMaterial(materials));
        scene.add(skinned_mesh);
        //helper = new THREE.SkeletonHelper( skinnedMesh );
        //helper.material.linewidth = 3;
        //scene.add( helper );
        mixer = new THREE.AnimationMixer(skinned_mesh);    // set up the mixer
        setupAnimations(URL.base);   // we initalise the base url (the other two will obviously be empty)
    });
}

// the next function is to test the concatenation/mixing
function setupAnimations(urlArray) {
    total_signs = urlArray.length;
    can_be_signed = total_signs;   // determines how many words in the resulting sentence can be signed, if more than some number cannot, we don't sign anything

    var promises_ = [];
    counter = 0;

    for (i = 0; i < total_signs; i++) {
        // $.getJSON returns a promise
        var animations_url = '../static/res/animations/' + urlArray[i].path + '/' + urlArray[i].name + '.js';
        promises_.push($.getJSON(animations_url));
    }
    whenDoneLoading(promises_, urlArray);
}

function whenDoneLoading(promises, urls) {
    // Combine all promises
    $.when.apply($, promises).then(function () {
        console.log("done loading promises", arguments);
        var clip;
        if (promises.length == 1){     // if we only need one animation
            clip = THREE.AnimationClip.parseAnimation(arguments[0].animations[0], arguments[0].bones);
            manual_clips.push({clip: clip, index: urls[0].index});
        }
        else {
            for (i = 0; i < arguments.length; i++) {
                clip = THREE.AnimationClip.parseAnimation(arguments[i][0].animations[0], arguments[i][0].bones);
                manual_clips.push({clip: clip, index: urls[i].index});
                //console.log(clip, arguments[i]);
            }
        }

        if (!started) {
            playInit();
            initScreen(false);
        }
        else {
            if (estimateIfCanSign(total_signs, can_be_signed)) {     // if we have enough data to sign
                if (URL.non_manual_names.length > 0) { // if no non manuals are needed, skip this step
                    console.log('done loading manual, next non-manual', manual_clips);
                    setupNonManual();
                }
                else {
                    console.log('done loading manual', manual_clips);
                    display_translation = true;
                }
            }
            else {      // otherwise say we cant and show gloss with highlighted gloss in red (those which are unknown)
                console.log('cannot display', manual_clips);
                for (i = 0; i < total_signs; i++) {
                    if (manual_clips[i + 2].clip.name == 'unknown_0') {
                        try {
                            Interface.highlightGloss(i, false);
                        } catch (e){
                            if (e instanceof TypeError){
                                console.log("cannot find gloss id in html "+i);
                            }
                        }
                    }
                }
                // display message
                flashScreen(true,'CANNOT DISPLAY');
                Interface.disableSpinner('cssload-container');  // stop loading
            }
        }
    }, function () {  // if any of the animations cannot be found we throw an error and replace the
        // not found json with the unknown
        console.log('error', promises, urls);
        for (i = 0; i < promises.length; i++) {
            if (promises[i].status == 404) {

                //console.log(urls[i].path.replace('/verbs',''));
                if(urls[i].path.substr( - 5) == 'verbs'){           // if the verb can't be found, try in the nouns as it may be there to avoid being repeated
                    urls[i].path = urls[i].path.replace('verbs','');
                    promises[i] = $.getJSON('../static/res/animations/' + urls[i].path + urls[i].name + '.js');
                }
                else {
                    can_be_signed -= 1;
                    promises[i] = $.getJSON('../static/res/animations/init/unknown_0.js');
                }
            }
        }
        whenDoneLoading(promises, urls);
    });
}

// this function sets up the non-manual animations for the clips
function setupNonManual() {
    counter = 0;
    URL.non_manual_names.forEach(function (url, i) {
        var animations_url = '../static/res/animations/non-manual/' + url + '.js';
        $.getJSON(animations_url, function (json) {
            clip = THREE.AnimationClip.parseAnimation(json.animations[0], json.bones);
            updateNonManualClipList(clip);
            counter += 1;
            if (counter == URL.non_manual_names.length) {    // once we have loaded all the non_manual_clips, go on to the next step
                console.log('done loading non manual', non_manual_clips);
                display_translation = true;
            }
        });
    });
}

function updateNonManualClipList(clip) {

    NON_MAN_VARS.clips_list.push(clip);       // used to keep track of playing status

    for (i = 0; i < non_manual_clips.length; i++) {
        for (j = 0; j < non_manual_clips[i].start.length; j++) {     // start
            if (non_manual_clips[i].start[j] == clip.name) {
                non_manual_clips[i].start[j] = clip;      // replace with clip object
            }
        }
        for (j = 0; j < non_manual_clips[i].end.length; j++) {   // end
            if (non_manual_clips[i].end[j] == clip.name) {
                non_manual_clips[i].end[j] = clip;      // replace with clip object
            }
        }
    }
}

function estimateIfCanSign(total, can_sign) {
    //console.log(total, can_sign);

    // if more than 30% of the sentene cannot be signed we don't show anything
    // if translate is pressed again the signs will be played anyway
    ratio = can_sign / total;
    //console.log(ratio);
    return ratio >= 0.3;
}

function playInit() {
    // play idle and blinking first
    mixer.clipAction(manual_clips[0].clip).play();  // play blinking and idle
    mixer.clipAction(manual_clips[1].clip).play();
}

function resetClipAndUrlArrays() {
    URL.reset();      // reset animation urls
    manual_clips.length = 2;   // remove all elements except the first two (idle and blinking)
    NON_MAN_VARS.clips_list = [];
}

function playAnimationSequence() {

    /** first step **/
    if (firstStep) {
        console.log("at first step");

        // set up the next clip to be interpolated
        mixer.clipAction(manual_clips[fadeCounter + 1].clip).setLoop(THREE.LoopOnce);
        mixer.clipAction(manual_clips[fadeCounter + 1].clip).reset();
        mixer.clipAction(manual_clips[fadeCounter + 1].clip).play();
        // set modifiers (needs to be done here)
        modifierLoop(manual_clips[fadeCounter + 1]);

        mixer.clipAction(manual_clips[fadeCounter].clip).crossFadeTo(mixer.clipAction(manual_clips[fadeCounter + 1].clip), interpolation_speed, false);

        // set interface changes
        colorGloss(fadeCounter);

        fadeCounter++;
        firstStep = false;
        continuousStep = true;
    }

    if (continuousStep) {
        if (URL.manual.length > 1) {  // if we only have to play 1 animation, we skip the middle step
            
            // if the current clip has reached the end we pause it to have time to fade to the next one
            if (mixer.clipAction(manual_clips[fadeCounter].clip).time > (manual_clips[fadeCounter].clip.duration - 0.1)) {
                mixer.clipAction(manual_clips[fadeCounter].clip).paused = true;  // pause current clip

                // if the same letter repeats, we need to change its name
                if (manual_clips[fadeCounter].clip.name == manual_clips[fadeCounter + 1].clip.name) {
                    manual_clips[fadeCounter + 1].clip.name += '_1';
                    //console.log(manual_clips[fadeCounter + 1].clip.name);
                }

                // setup next clip like in first step
                mixer.clipAction(manual_clips[fadeCounter + 1].clip).setLoop(THREE.LoopOnce);
                mixer.clipAction(manual_clips[fadeCounter + 1].clip).reset();
                mixer.clipAction(manual_clips[fadeCounter + 1].clip).play();

                // set modifiers (needs to be done here)
                modifierLoop(manual_clips[fadeCounter + 1]);

                // check if word is a compound I like lions and cats.

                var comp_counter = checkIfCompound();  // returns {counter, interpolation}

                mixer.clipAction(manual_clips[fadeCounter].clip).crossFadeTo(mixer.clipAction(manual_clips[fadeCounter + 1].clip), interpolation_speed, false);

                // set interface changes
                colorGloss(comp_counter);

                if (fadeCounter == URL.manual.length) {   // if we reached the end of the animations, go to final step
                    continuousStep = false;
                    finalStep = true;
                }
                fadeCounter++;
            }
        }
        else {
            continuousStep = false;
            finalStep = true;
        }
    }

    /** final step **/
    if (finalStep) {

        // pause clip to have time to fade
        if (mixer.clipAction(manual_clips[fadeCounter].clip).time > (manual_clips[fadeCounter].clip.duration - 0.1)) { // this line is identical
            console.log("at final step");
            mixer.clipAction(manual_clips[fadeCounter].clip).paused = true;
            mixer.clipAction(manual_clips[1].clip).reset();     // assuming idle is the second clip ALWAYS
            mixer.clipAction(manual_clips[fadeCounter].clip).crossFadeTo(mixer.clipAction(manual_clips[1].clip), interpolation_speed, false);

            // set interface changes
            Interface.resetAllGloss();

            if (auto_cam && first_person) {
                swapCamera();
            }

            finalStep = false;
            done = true; // this way we also set the start button back
        }
    }
}

function checkIfCompound(){

    var counter = fadeCounter;

    if (URL.manual[counter-1].compound && Interface.gloss_index != URL.manual[counter-1].index){    // if the word is a compound (same word)

        counter -= URL.manual[counter-1].compound_index;
        console.log("is compound", URL.manual[counter-1], manual_clips[fadeCounter+1].clip);

        Interface.gcd_has_changed = true;
        mixer.clipAction(manual_clips[fadeCounter+1].clip).setEffectiveTimeScale(animation_speed*1.7);
        mixer.clipAction(manual_clips[fadeCounter+2].clip).setEffectiveTimeScale(animation_speed*1.7);
    }
    else{
        if (Interface.gcd_has_changed) {
            Interface.gloss_counter_diff++;
            Interface.gcd_has_changed = false;
        }
    }

    Interface.gloss_index = URL.manual[counter-1].index;

    return counter - Interface.gloss_counter_diff;
}

function playNonManualSequence(sign_index) {

    if (sign_index != NON_MAN_VARS.current_index) {      // if we change sign
        //console.log('sign_index ' + sign_index);
        nonManualLoop(sign_index);                                // go through the non manual loop to set clips
        NON_MAN_VARS.current_index = sign_index;        // update sign index
    }
}

function nonManualLoop(sign_index) {

    if (sign_index < non_manual_clips.length && sign_index >= 0) {
        // for any clip that begins at this point (given by the clip index that is playing)
        var clips = non_manual_clips[sign_index].start;
        var clip_names = [];
        for (i = 0; i < clips.length; i++) {
            mixer.clipAction(clips[i]).reset();
            mixer.clipAction(clips[i]).setLoop(THREE.LoopOnce);
            mixer.clipAction(clips[i]).play();

            clip_names.push(clips[i].name);
        }
        if (clip_names.length > 0) {
            Interface.showNonManual(clip_names, 500 / animation_speed);        // show the non manual features being used at this time
        }
    }

    sign_index--;   // go down one to access the ending feature from the previous sign

    if (sign_index >= 0) {
        // for any clip ending at this point
        clips = non_manual_clips[sign_index].end;
        for (i = 0; i < clips.length; i++) {
            //console.log('stopping '+clips[i].name);
            mixer.clipAction(clips[i]).fadeOut(interpolation_speed);
        }
    }
}

function checkStatusNonManualClips() {
    var clips = NON_MAN_VARS.clips_list;
    for (i = 0; i < clips.length; i++) {
        if (mixer.clipAction(clips[i]).time > (clips[i].duration - 0.1)) {
            mixer.clipAction(clips[i]).paused = true;  // pause current clip
        }
    }
}

function modifierLoop(clip) {
    mod_list = URL.modifiers[clip.index].modifiers;
    if (mod_list.length > 0) {  // if there is a modifier applied to the sign at this index, apply it
        //console.log("modifier " +sign_index+ ' '+mod_list);
        for (i = 0; i < mod_list.length; i++) {
            //console.log(manual_clips[fadeCounter]);
            applyModifier(mod_list[i], clip.clip);
        }
        Interface.showNonManual(mod_list, 500 / animation_speed);
    }
}

// if a modifier applies to this sign, we check the mod type and change the clip
function applyModifier(mod, clip) {
    // uses the TWEEN library

    var tween = new TWEEN.Tween(mixer.clipAction(clip));
    var duration = (clip.duration - 0.3) * 1000 / animation_speed;    // milliseconds

    //console.log(mod, clip, duration, mixer.clipAction(clip).timeScale, tween);

    if (mod == 'cp') {       // comparartive = small hold at the beginning and sign faster
        mixer.clipAction(clip).paused = true;
        mixer.clipAction(clip).timeScale = 0.2 * animation_speed;
        tween.to({timeScale: animation_speed * 1.5}, duration)
            .delay(duration / 3)
            .easing(TWEEN.Easing.Quadratic.InOut)
            //.onUpdate(function() {console.log("tween changed "+this.timeScale);} )
            .start(); // interpolate to a faster timescale for the duration of the clip - 0.3
    }
    else if (mod == 'sp') {  // superlative = long hold and sign even faster
        mixer.clipAction(clip).paused = true;
        mixer.clipAction(clip).timeScale = 0.1 * animation_speed;
        tween.to({timeScale: animation_speed * 1.7}, duration)
            .delay(duration / 1.5)
            .easing(TWEEN.Easing.Quartic.InOut)
            //.onUpdate(function() {console.log("tween changed "+this.timeScale);} )
            .start(); // interpolate to a faster timescale for the duration of the clip - 0.3
    }
    else if (mod == 'pause') {   // hold at the end of the clip
        console.log('pause detected');
        //mixer.clipAction(clip).duration = clip.duration+2.0;  // add some more delay
        clip.duration += 0.2 / animation_speed;
    }
}

// only gets called when we change the speed
function updateSpeed(speed) {
    //console.log('updating speed');
    for (i = 0; i < manual_clips.length; i++) {
        // this is because of a mistake during the animations
        //console.log(i);
        s = speed;
        if (i > 1) {
            if (URL.manual[i - 2].path == 'numbers' || URL.manual[i - 2].path == 'alphabet') {
                s = speed * 1.6;
            }
        }
        mixer.clipAction(manual_clips[i].clip).setEffectiveTimeScale(s);
    }
    for (i = 0; i < NON_MAN_VARS.clips_list.length; i++) {
        mixer.clipAction(NON_MAN_VARS.clips_list[i]).setEffectiveTimeScale(speed);
    }
    updateInterpolation(speed);
}

function updateInterpolation(speed) {
    if (speed > 1.5) {   // we keep the standard interpolation for anything higher than 1.0
        interpolation_speed = 0.3;
    }
    else if (speed < 0.5) {
        interpolation_speed = 3.0;
    }
    else {   // else we calculate the correct speed (should be 1.0 for speed = 0.5)
        interpolation_speed = 0.5 / speed;
    }
}

function autoChangeCamera(counter) {
    if (swap_counter != counter) {
        if (URL.manual[counter].path == 'alphabet' && !first_person) { // if the sign is fingerspelled, switch to fpv
            swapCamera(500);
        }
        else if (URL.manual[counter].path != 'alphabet' && first_person) {
            swapCamera(500);
        }
        swap_counter = counter;
    }
}

function swapCamera(speed_) {

    var speed = (speed_ !== undefined) ? speed_ : 1500;     // default value

    first_person = !first_person;

    var toWhat;

    // initalise tweening vars
    position_tween = new TWEEN.Tween(camera.position);
    camera_tween = new TWEEN.Tween(camera);
    target_tween = new TWEEN.Tween(camera_target.position);

    if (first_person) {
        toWhat = FPS_CAM_VARS;
        flashScreen(false, 'First Person');
    }
    else {
        toWhat = CAM_VARS;
        flashScreen(false, 'Default View');
    }

    controls.enabled = toWhat.controls_enabled;
    position_tween.to({x: toWhat.position.x, y: toWhat.position.y, z: toWhat.position.z}, speed).start();
    camera_tween.to({near: toWhat.near, fov: toWhat.fov}, speed).start();
    target_tween.to({z: toWhat.targetZ}, speed)
        .onUpdate(function () {
            onWindowResize();
        }).start();
    //.onComplete(renderer.setSize( window.innerWidth, window.innerHeight));
}

/*********** MAIN ANIMATION LOOP ************/
function animate() {

    requestAnimationFrame(animate);

    if (display_translation) { // for testing, will normally be activated once the animation sequence has been formed
        console.log('starting');

        Interface.disableSpinner('cssload-container');  // stop loading

        // begin fadeCounter for manual clips
        fadeCounter = 1;

        updateSpeed(animation_speed);   // update before playing to be sure

        firstStep = true;
        display_translation = false;    // avoid repeating this multiple times
    }

    playAnimationSequence();

    if (mixer) {
        mixer.update(clock.getDelta());

        // should move all of this somewhere else
        if (firstStep || continuousStep || finalStep) {
            if (paused) {
                mixer.clipAction(manual_clips[0].clip).paused = true;      // also stop the blinking : will have to apply to all animations (facial expressions etc)
                mixer.clipAction(manual_clips[fadeCounter].clip).paused = true;
            }
            else {
                mixer.clipAction(manual_clips[0].clip).paused = false;      // put back blinking
                mixer.clipAction(manual_clips[fadeCounter].clip).paused = false;
            }

            if (auto_cam) {
                autoChangeCamera(fadeCounter - 2);
            }

            if (NON_MAN_VARS.clips_list.length > 0) {      // no point in doing this if the lists are empty){
                playNonManualSequence(manual_clips[fadeCounter].index); // get the current clip index and pass it
                checkStatusNonManualClips();        // for pausing
            }
        }

        // if cancelled reset all variables to initial state
        if (cancelled) {
            resetAllManualVars();
            resetNonManual();
        }

        // reset variables to first state
        if (done) {
            Interface.play_pause_button.pause();     // set back to play
            Interface.resetGcd();
            resetNonManual();
            done = false;
            started = false;
        }
    }
    render();
}

function render() {
    camera.lookAt(camera_target.position);
    renderer.render(scene, camera);
    stats.update();
    TWEEN.update();     // for the modifiers we use TWEEN
}

function resetAllManualVars() {
    firstStep = false;
    continuousStep = false;
    finalStep = true;
    paused = false;     // stop the pause before going back to idle
    cancelled = false;
    done = true;
    started = false;

    resetNonManual();
}

// when cancelled or done with the animation loop,
function resetNonManual() {
    var clips = NON_MAN_VARS.clips_list;
    for (i = 0; i < clips.length; i++) {
        mixer.clipAction(clips[i]).crossFadeTo(mixer.clipAction(manual_clips[1].clip), interpolation_speed, false);  // fade out at the end to be sure
    }
}

function colorGloss(counter) {
    // if current gloss is unknown
    var exists = true;
    var compound = false;
    if (manual_clips[fadeCounter + 1].clip.name.indexOf('unknown_0') > -1) {   // check if name is (or contains unknown_0, in case it is repeated)
        exists = false
    }
    if (URL.manual[fadeCounter-1].compound){
        compound = true;
    }

    Interface.highlightGloss(counter - 1, exists, compound);    // temporary solution for accessing the div id, (we go back one because of the idle and blinking)
    Interface.resetGloss(counter - 2);        // could also set the id directly to match fadeCounter?
}
function flashScreen(flash, str) {
    var colour = "#333333";
    if (flash) {
        $('.flash').fadeIn(100).delay(200).fadeOut(200);
        colour = "#ff0000";
    }

    $('#notification-text').html(str)
        .css("color", colour)
        .fadeIn(100).delay(2000).fadeOut(400);
}

function initScreen(status) {
    if (status) {
        $('#curtain').show();
        $('#notification-text').html("<span style='color: #ffffff'>Loading model...</span>").show();
    }
    else {
        $('#curtain').fadeOut(500);
        $('#notification-text').fadeOut(500);
    }
}

/// INTERFACE RELATED STUFF

$('#translate').on('click', function () {
    beginTranslate();
});

function beginTranslate(){
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

            // use data.result[1] for the rest

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
        display_translation = true;
    }
}

$('#swap').on('click', function () {
    //firstPerson = !firstPerson;
    swapCamera();
});

$('#stop').on('click', function () {
    if (started) {
        cancelled = true;
    }
});

$('#play-pause').on('click', function () {
    // will add if (animation.playing) {  or something, otherwise you cant switch or click
    if (started) {
        paused = !paused;
        Interface.play_pause_button.switch();   // switch icons
    }
});

// EXAMPLE SENTENCES SELECTION
$('#select').on('click', function (event) {
    // open the drop down menu with options and fill the English field with the selected sentence
    //$('.sub-menu').show().animate();
    $('.sub-menu').toggle('fast');

    $('ul.sub-menu li').unbind().click(function () {
        $(this).parents('ul.sub-menu').hide('fast');

        var text = $(this).text();
        $('#english').val(text);
        $("#translate").attr("class","button");

        return false;
    });

    // for hiding the menu once we've clicked outside
    $(window).one('click', function () {
        $('.sub-menu').hide('fast');
    });
    event.stopPropagation();
});

/** INFO MENU JS **/

$('#info-button').on('click', function () {
    $('.overlay').slideToggle('fast');
    $('#close').show();
});

$('a#showdir').on('click', function () {
    // temporary
    if (Interface.available_signs_show) {
        $('#dir-result').html('');
        Interface.available_signs_show = false;
    }
    else {
        $.getJSON('/_print_dir', function (data) {
            result = data.result;
            var number_of_signs = 0;
            var string_res = '';//'<b>Total signs: '+result.length+'</b><br/>';
            var sub = false;
            for (i = 0; i < result.length; i++) {
                if (result[i].trim() == 'verbs/') {}// do nothing
                else if (result[i].substr(-1) == '/') {
                    string_res += '<br/><b>' + result[i] + '</b><br/>';
                    sub = true;
                }
                else {
                    if (sub) {
                        string_res += result[i] + ', ';
                        sub = false;
                    }
                    else string_res += result[i].trim() + ', ';
                    number_of_signs++;
                }
            }
            string_res = '<b>Total signs: '+number_of_signs+'</b><br/>'+string_res;
            //console.log(string_res);
            $('#dir-result').html(string_res);
            Interface.available_signs_show = true;
        });
    }
});

/** OPTIONS MENU JS **/

$('#options').on('click', function () {
    $('.overlay-menu').slideToggle('fast');
    $('#close').show();
});

$('#close').on('click', function(){
    closeMenus();
});

function closeMenus(){
    $('.overlay-menu').slideUp('fast');
    $('.overlay').slideUp('fast');
    $('#close').hide();
}

// JSLIDER
var slider = new Slider('#ex1', {
    formatter: function (value) {
        animation_speed = value.toFixed(1);
        updateSpeed(animation_speed);
        $('#speed').html(animation_speed);
    }
});

$('#non-man-help').on('click', function () {
    Interface.show_non_manual = this.checked;
});

$('#auto-camera').on('click', function () {
    auto_cam = this.checked;
});

/** for checking spelling/correctness */
//on keyup, start the countdown
Interface.$input.on('keyup', function () {
    clearTimeout(Interface.typingTimer);
    Interface.typingTimer = setTimeout(doneTyping, Interface.doneTypingInterval);
});

//on keydown, clear the countdown
Interface.$input.on('keydown', function (e) {
    if (e.keyCode == 13 || e.which == 13 ){
        if (Interface.can_begin_translate) beginTranslate();
    }
    else {
        Interface.$input.css('color', 'black');
        clearTimeout(Interface.typingTimer);
    }
});

$(document).on('keydown', function(e){
    if (e.keyCode == 27 || e.which == 27) {      // if we're in a menu
        closeMenus();
    }
});

//user is "finished typing," do something
function doneTyping() {
    var txt = Interface.$input.val();
    //console.log(txt);
    if (endsWith(txt,".") || endsWith(txt,"!") || endsWith(txt,"?")){
        Interface.can_begin_translate = true;
        $("#translate").attr("class","button");
    }
    else {
        Interface.can_begin_translate = false;
        Interface.$input.css('color', 'red');
        $("#translate").attr("class","button disabled");
        flashScreen(false, "Missing punctuation");
    }
}

$(document).ready(function () {
    initScreen(true);
});

function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}