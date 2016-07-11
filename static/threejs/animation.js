var SCREEN_WIDTH = window.innerWidth;
var SCREEN_HEIGHT = window.innerHeight;
var container, stats;
var camera, fpCamera, scene, renderer, controls, cameraTarget;
var firstPerson, started, displayTranslation, paused, cancelled, done = false;

var skinnedMesh;

var modelUrl = '../static/res/model/model2.js'; // where the model is located (for local testing)
var baseUrls = [{name:'blinking', path:'init'}, {name:'idle', path:'init'}];       // these are loaded along with the model at the beginning
var urls = [];  // here will go all clips for the translation

// animation stuff
var mixer,clips; // make them global for testing

var clock = new THREE.Clock();

//testing
var sorted, firstStep, continuousStep, finalStep = false;
var fadeCounter = 1;

init();
animate();

function init() {

    clips = new Array;

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
    $.getJSON(modelUrl, function(json){

        var matLoader = new THREE.ObjectLoader(); // this loader will be used to parse JSON textures into THREE textures

        // the following sequence is analogous to the source code
        matLoader.texturePath = modelUrl.substring( 0, modelUrl.lastIndexOf( '/' ) + 1 );
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

    loader.load(modelUrl, function ( object ) {

        skinnedMesh = new THREE.SkinnedMesh(object.children[0].geometry, new THREE.MeshFaceMaterial(materials));

        scene.add(skinnedMesh);

        //helper = new THREE.SkeletonHelper( skinnedMesh );
        //helper.material.linewidth = 3;
        //scene.add( helper );

        mixer = new THREE.AnimationMixer(skinnedMesh);    // set up the mixer

        setupAnimations(baseUrls);   // we initalise the base url
    });
}

// the next function is to test the concatenation/mixing
function setupAnimations(urlArray){
    //urls = ['blinking', 'idle','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];  // array containing all animations required for the clip

    var counter = 0;

    for(var i = 0; i < urlArray.length; i++){
        (function(i) {
            console.log(urlArray[i].name);
            var url = '../static/res/animations/' + urlArray[i].path + '/' + urlArray[i].name + '.js';  // (for local testing)

            $.getJSON(url, function (json) {
                clip = THREE.AnimationClip.parseAnimation(json.animations[0], json.bones);

                counter ++;

                updateClipList(clip, i);

                if (counter == urlArray.length) {    // once we have loaded all the clips, go on to modify them9
                    if(!started) nextStep();
                    else {
                        console.log('done loading new', clips, urls);
                        displayTranslation = true;
                    }
                }
            });
        })(i);
    }
}

function updateClipList(clip, index){
    //console.log(index, clip.name);
    if(!started) {      // if we are still loading the initial animations
        clips.splice(index, 0, clip);   // insert object
    }
    else{
        clips.splice(index+2, 0, clip);   // insert object 2 indexes further
    }
    //console.log(clips);
}

function nextStep(){
    //console.log(clips);

    // play idle and blinking first
    mixer.clipAction(clips[0]).play();  // play blinking and idle
    mixer.clipAction(clips[1]).play();

    //console.log("started");
}

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    fpCamera.aspect = window.innerWidth / window.innerHeight;
    fpCamera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

// WE CAN EITHER USE THE KEYBOARD FOR TESTING
// function handleKeyDown(event) {
//     if (event.keyCode == 66) { //66 is "b"
//         window.isBDown = true;
//     }
//
//     if(event.keyCode == 86){
//         if(firstPerson) firstPerson = false;
//         else firstPerson = true;
//     }
// }
//
// window.addEventListener('keydown', handleKeyDown, false);

// OR WE CAN USE ONSCREEN BUTTONS

function resetClipAndUrlArrays(){
    urls = [];      // reset animations
    clips.length = 2;   // remove all elements except the first two (idle and blinking)
}

function playAnimationSequence(){

    /** first step **/
    if(firstStep){
        console.log("at first step");
        // set up the next clip to be interpolated
        mixer.clipAction(clips[fadeCounter+1]).setLoop(THREE.LoopOnce);
        mixer.clipAction(clips[fadeCounter+1]).reset();
        mixer.clipAction(clips[fadeCounter+1]).play();
        mixer.clipAction(clips[fadeCounter]).crossFadeTo(mixer.clipAction(clips[fadeCounter+1]), 0.6, false);

        fadeCounter++;
        firstStep = false;
        continuousStep = true;
    }

    if(continuousStep){
        if(urls.length > 1) {  // if we only have to play 1 animation, we skip the middle step
            if (mixer.clipAction(clips[fadeCounter]).time > (clips[fadeCounter].duration - 0.1)) {
                //console.log("at continuous step", fadeCounter);
                mixer.clipAction(clips[fadeCounter]).paused = true;  // pause current clip
                // set up next clip
                if(clips[fadeCounter].name == clips[fadeCounter+1].name){
                    clips[fadeCounter+1].name += '_1';  // if the same letter repeats, we need to change its name
                    console.log(clips[fadeCounter+1].name);
                }
                mixer.clipAction(clips[fadeCounter + 1]).setLoop(THREE.LoopOnce);
                mixer.clipAction(clips[fadeCounter + 1]).reset();
                mixer.clipAction(clips[fadeCounter + 1]).play();
                mixer.clipAction(clips[fadeCounter]).crossFadeTo(mixer.clipAction(clips[fadeCounter + 1]), 0.6, false);

                if (fadeCounter == urls.length) {   // if we reached the end of the animations, go to final step
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
        if(mixer.clipAction(clips[fadeCounter]).time > (clips[fadeCounter].duration-0.1)) { // this line is identical
            console.log("at final step");
            mixer.clipAction(clips[fadeCounter]).paused = true;
            mixer.clipAction(clips[1]).reset();     // assuming idle is the second clip ALWAYS
            mixer.clipAction(clips[fadeCounter]).crossFadeTo(mixer.clipAction(clips[1]), 0.6, false);

            finalStep = false;
            done = true; // this way we also set the start button back
        }
    }
}

function animate() {

    requestAnimationFrame( animate );

    if(displayTranslation){ // for testing, will normally be activated once the animation sequence has been formed
        console.log('starting');
        fadeCounter = 1;
        firstStep = true;
        displayTranslation = false;    // avoid repeating this multiple times
    }

    playAnimationSequence();

    if(mixer) {mixer.update(clock.getDelta());

        // should move all of this somewhere else
        if(firstStep || continuousStep || finalStep) {
            if (paused) {
                mixer.clipAction(clips[0]).paused = true;      // also stop the blinking : will have to apply to all animations (facial expressions etc)
                mixer.clipAction(clips[fadeCounter]).paused = true;
            }
            else {
                mixer.clipAction(clips[0]).paused = false;      // put back blinking
                mixer.clipAction(clips[fadeCounter]).paused = false;
            }
        }
        if(cancelled){
            firstStep = false;
            continuousStep = false;
            finalStep = true;
            paused = false;     // stop the pause before going back to idle
            cancelled = false;
            done = true;
            started = false;
        }
        
        if(done){
            // set the first button back to start
            document.getElementById('start-pause-play').innerHTML = 'start';
            // hide the cancel button
            document.getElementById('cancel').style.visibility = 'hidden';
            done = false;
            started = false;
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

/// MAIN PAGE RELATED STUFF

$('#swap-camera').on('click', function() {
    firstPerson = !firstPerson;
});

$('#start-pause-play').on('click', function() {

    var text = '';

    if (this.innerHTML == 'start') {

        console.log("clicked start");

        //this.innerHTML = 'pause';
        // get the text from the textbox and send it to python
        $.getJSON('/_process_text', {
            input_text: $('input[name="input_text"]').val()
        }, function(data) {

            console.log(data);

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
    }
    else {
        paused = !paused;
        if (this.innerHTML == 'pause') this.innerHTML = 'play';
        else this.innerHTML = 'pause';
    }
    // remember that on first click we make 'cancel' visible
    //document.getElementById('cancel').style.visibility = 'visible';
});

$('#cancel').on('click', function() {
    cancelled = true;
    this.style.visibility = 'hidden';
    //paused = !paused;
});