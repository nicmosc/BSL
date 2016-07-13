/**
 * Created by Nicola on 13/07/16.
 */

// will hold all the variables related to the model
function MODEL() {
    var skinnedMesh;
    var modelUrl = '../static/res/model/model2.js'; // where the model is located
    var baseUrls = [{name: 'blinking', path: 'init'}, {name: 'idle', path: 'init'}];       // these are loaded along with the model at the beginning
    var urls;  // here will go all clips for the translation
}

Model.prototype = {};

// will handle all the animation stuff as well as the sub methods for rendering
function ENGINE() {
    this.scene = new THREE.Scene();
    this.renderer = new THREE.WebGLRenderer({antialias: true});
}

ENGINE.prototype = {
    initialise: function () {
        container = document.createElement('div');
        document.body.appendChild(container);

        // SCENE
        this.scene = new THREE.Scene();

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
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(SCREEN_WIDTH, SCREEN_HEIGHT);
        container.appendChild(renderer.domElement);

        renderer.gammaInput = true;
        renderer.gammaOutput = true;

        // MODEL
        $.getJSON(modelUrl, function (json) {

            var matLoader = new THREE.ObjectLoader(); // this loader will be used to parse JSON textures into THREE textures

            // the following sequence is analogous to the source code
            matLoader.texturePath = modelUrl.substring(0, modelUrl.lastIndexOf('/') + 1);
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
    }
};