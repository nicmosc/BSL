/**
 * Created by Nicola on 13/07/16.
 */

// used for the loading of tranlations/animations, modifies css
    
var Spinner = (function (div_id) {
    this.div_id = div_id;

    this.enable = function(){
        document.getElementById(this.div_id).style.visibility = 'visible';
    };
    this.disable = function(){
        document.getElementById(this.div_id).style.visibility = 'hidden';
    };
});

