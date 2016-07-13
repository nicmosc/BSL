/**
 * Created by Nicola on 13/07/16.
 */

// will hold all the variables related to the model
function Model(){
    var skinnedMesh;
    var modelUrl = '../static/res/model/model2.js'; // where the model is located
    var baseUrls = [{name:'blinking', path:'init'}, {name:'idle', path:'init'}];       // these are loaded along with the model at the beginning
    var urls;  // here will go all clips for the translation
}

Model.prototype = {
    
};

// will handle all the animation stuff as well as the sub methods for rendering
function Engine(){
    
}