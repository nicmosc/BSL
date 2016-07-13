/**
 * Created by Nicola on 13/07/16.
 */

// object to set the front end stuff
function Button(name,icon1, icon2){
    this.play_icon = icon1;
    this.pause_icon = icon2;
    this.name = name;
    this.play_on = true;
}

Button.prototype = {
    constructor: Button,
    
    play: function(){
        // set the icon for the button
        document.getElementById(this.name).className = "glyphicon glyphicon-"+this.play_icon;
        this.play_on = true;
    },
    pause: function(){
        // set the icon for the button
        document.getElementById(this.name).className = "glyphicon glyphicon-"+this.pause_icon;
        this.play_on = false;
    },
    switch: function(){
        if (this.play_on){
            this.pause();
        }
        else{
            this.play();
        }
    }
};

// used for the loading of tranlations/animations, modifies css
function INTERFACE() {
    this.play_pause_button = new Button('switcher','play', 'pause');
}

INTERFACE.prototype = {

    constructor: INTERFACE,

    enableSpinner: function(div) {
        console.log('enabling');
        document.getElementById(div).style.visibility = 'visible';
    },
    disableSpinner: function(div){
        console.log('disabling');
        document.getElementById(div).style.visibility = 'hidden';
    },
    setGloss: function(div, text) {
        document.getElementById(div).innerHTML = text;
    }
};