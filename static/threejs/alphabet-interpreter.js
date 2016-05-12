var SCREEN_WIDTH = window.innerWidth;
var SCREEN_HEIGHT = window.innerHeight;

var container, stats;
var camera, scene, renderer, controls, cameraTarget, helper;

var skinnedMesh;

// for local testing use '../static/res/ ... etc .. '
// for flask testing use ''

//var modelUrl = '../static/res/model/model.js';  // where the model is located (for local testing)

var modelUrl = '../static/res/model/model.js';

// animation stuff
var mixer,clips, urls; // make them global for testing

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

    // CAMERA

    camera = new THREE.PerspectiveCamera( 30, SCREEN_WIDTH / SCREEN_HEIGHT, 1, 10000 );
    camera.position.set(0, 5, 10 );
    //camera.up.set(0,0,1);
    cameraTarget = new THREE.Mesh( new THREE.CubeGeometry(0,0,0)); // so that the camera follows the head correctly
    cameraTarget.position.y = 4;

    controls = new THREE.OrbitControls( camera );
    controls.update();

    // SCENE

    scene = new THREE.Scene();

    // CONTROLS

    controls = new THREE.OrbitControls( camera );
    controls.maxPolarAngle = 0.9 * Math.PI / 2;
    controls.enableZoom = false;

    // LIGHTS

    var light = new THREE.DirectionalLight( 0xaabbff, 0.3 );
    light.position.x = 300;
    light.position.y = 250;
    light.position.z = 500;
    scene.add( light );

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
        var modelMaterials = [];
        for(var i = 0; i < json.geometries.length; i++){

            var materials = [];

            for(var mat = 0; mat < json.geometries[i].materials.length; mat++){
                var name = json.geometries[i].materials[mat].DbgName;

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

            modelMaterials.push(materials);
        }
        loadModel(modelMaterials);
    });

    window.addEventListener( 'resize', onWindowResize, false );

}

function loadModel(materials){

    var loader = new THREE.ObjectLoader();

    loader.load(modelUrl, function ( object ) {

        for(var i = 0; i < object.children.length; i++) {   // there are two children in this test (body, eyes), now only 1 lol

            skinnedMesh = new THREE.SkinnedMesh(object.children[i].geometry, new THREE.MeshFaceMaterial(materials[i]));

            scene.add(skinnedMesh);

            helper = new THREE.SkeletonHelper( skinnedMesh );
            helper.material.linewidth = 3;
            //scene.add( helper );

            setupAnimations();
        }
    });
}

// the next function is to test the concatenation/mixing
function setupAnimations(){
    urls = ['blinking', 'idle','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'];  // array containing all animations required for the clip

    mixer = new THREE.AnimationMixer(skinnedMesh);    // set up the mixer

    var counter = 0;

    for(var i = 0; i < urls.length; i++){
        (function(i) {
            var url = '../static/res/animations/alphabet/' + urls[i] + '.js';  // (for local testing)

            $.getJSON(url, function (json) {
                clip = THREE.AnimationClip.parseAnimation(json.animations[0], json.bones);

                counter ++;

                updateClipList(clip, i);

                if (counter == urls.length) {    // once we have loaded all the clips, go on to modify them9
                    nextStep();
                }
            });
        })(i);
    }
}

function updateClipList(clip, index){
    console.log(index, clip.name);
    clips.splice(index, 0, clip);   // insert object
    //console.log(clips);
}

function nextStep(){
    console.log(clips);

    // play idle and blinking first
    mixer.clipAction(clips[0]).play();  // play blinking and idle
    mixer.clipAction(clips[1]).play();

    console.log("playing");
}

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

function handleKeyDown(event) {
    if (event.keyCode == 66) { //66 is "b"
        window.isBDown = true;
    }
}

window.addEventListener('keydown', handleKeyDown, false);

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
        if(urls.length > 3) {  // if we only have to play 1 animation, we skip the middle step
            if (mixer.clipAction(clips[fadeCounter]).time > (clips[fadeCounter].duration - 0.1)) {
                console.log("at continuous step", fadeCounter);
                mixer.clipAction(clips[fadeCounter]).paused = true;  // pause current clip
                // set up next clip
                mixer.clipAction(clips[fadeCounter + 1]).setLoop(THREE.LoopOnce);
                mixer.clipAction(clips[fadeCounter + 1]).reset();
                mixer.clipAction(clips[fadeCounter + 1]).play();
                mixer.clipAction(clips[fadeCounter]).crossFadeTo(mixer.clipAction(clips[fadeCounter + 1]), 0.6, false);

                if (fadeCounter == urls.length - 2) {
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
        }
    }
}

function animate() {

    requestAnimationFrame( animate );

    if(window.isBDown){ // for testing, will normally be activated once the animation sequence has been formed
        fadeCounter = 1;
        firstStep = true;
        window.isBDown = false;
    }

    playAnimationSequence();

    if(mixer) {mixer.update(clock.getDelta());
        //console.log(mixer.clipAction(getClip(clips, 'idle')).time);
    }

    camera.lookAt(cameraTarget.position);

    render();

    stats.update();
    //helper.update();

}

function render() {

    renderer.render( scene, camera );

}