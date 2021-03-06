/**
 * Created by Nicola on 13/07/16.
 */

function Button(name){
    this.name = name;
}
Button.prototype = {
    constructor: Button,

    enable: function(){
        document.getElementById(this.name).disable = false;
    },
    disable: function(){
        document.getElementById(this.name).disable = true;
    }
};

function SwitchButton(name,icon1, icon2){
    this.play_icon = icon1;
    this.pause_icon = icon2;
    this.name = name;
    this.play_on = false;
}

SwitchButton.prototype = new Button();
SwitchButton.prototype.constructor= SwitchButton;

SwitchButton.prototype.play = function() {
    // set the icon for the button
    document.getElementById(this.name).className = "glyphicon glyphicon-" + this.play_icon;
    this.play_on = true;
};
SwitchButton.prototype.pause = function() {
    // set the icon for the button
    document.getElementById(this.name).className = "glyphicon glyphicon-" + this.pause_icon;
    this.play_on = false;
};

SwitchButton.prototype.switch = function() {
    if (this.play_on) {
        this.pause();
    }
    else {
        this.play();
    }
};

// used for the loading of translations/animations, modifies css
function INTERFACE() {
    this.play_pause_button = new SwitchButton('switcher','play', 'pause');
    
    this.current_text = '';
    this.gloss_length = 0;      // will hold the number of signs to be played (for gloss highlighting)
    this.available_signs_show = false;
    this.show_non_manual = false;       // will display the non-manual features happening at that time
    
    this.gloss_counter_diff = 0;        // if we have compounds the counters won't match, so we make the difference
    this.gcd_has_changed = false;
    this.gloss_index = 0;
    
    // for checking the correct spelling of input
    this.typingTimer = 0;
    this.doneTypingInterval = 1000;
    this.$input = $('#english');
    this.can_begin_translate = false;
}

INTERFACE.prototype = {

    constructor: INTERFACE,

    enableSpinner: function(div) {
        document.getElementById(div).style.visibility = 'visible';
    },
    disableSpinner: function(div){
        document.getElementById(div).style.visibility = 'hidden';
    },
    setGloss: function(div, text) {
        document.getElementById(div).innerHTML = text;
        this.current_gloss = text;
    },
    highlightGloss: function(id, exists, compound){
        if(id >= 0 && id < this.gloss_length) {
            if (compound && exists){
                document.getElementById(id).style.color = '#33cc33';
                document.getElementById(id).style.textShadow = "#33cc33 0 0 5px";
            }
            else if (exists) {   // if the sign for gloss is found
                document.getElementById(id).style.color = '#3366ff';
                document.getElementById(id).style.textShadow = "#3366ff 0 0 5px";
            }
            else{   // if unknown color red
                document.getElementById(id).style.color = 'red';
                document.getElementById(id).style.textShadow = 'red 0 0 5px';
            }
        }
    },
    resetGloss: function(id) {
        if(id >= 0 && id < this.gloss_length) {
            document.getElementById(id).style.color = document.getElementById('bsl').style.color;   // reset to container color
            document.getElementById(id).style.textShadow = document.getElementById('bsl').style.textShadow;   // reset to container color
        }
    },
    resetAllGloss: function(){
        $("span").css( 'color', document.getElementById('bsl').style.color)
            .css( 'text-shadow', document.getElementById('bsl').style.textShadow);
    },
    resetGcd: function(){
        this.gloss_counter_diff = 0;
        this.gcd_has_changed = false;
        this.gloss_index = 0;
    },
    showNonManual: function(tags, speed, override_show){
        if(this.show_non_manual || override_show) {
            $('#non-manual-text').html(tags.join(', '));
            $('.helper').fadeIn(200).delay(speed).fadeOut(200);
        }
    }
};

function URLS(){
    this.model = '../static/res/model/model2.js'; // where the model is located (for local testing)
    this.base = [{name:'blinking', path:'init', index:-1}, {name:'idle', path:'init', index:-1}];       // these are loaded along with the model at the beginning

    this.manual = [];
    this.non_manual = [];   // manual_clips for the non_manual features
    this.non_manual_names = [];     // used to load the animations first

    this.modifiers = [];
}

URLS.prototype = {
    constructor: URLS,
    reset: function(){
        this.manual = [];
        this.non_manual = [];
        this.modifiers = [];
    }
};