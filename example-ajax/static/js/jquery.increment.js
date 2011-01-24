 /*
 *
 * Increment - a jQuery Plugin
 * Copyright 2010 Sean O
 * http://sean-o.com
 * http://twitter.com/seanodotcom 
 *  
 * Version 0.6 - April, 2010
 *      Added support for mousewheel plugin, small Closure Compiler bugfix
 * Version 0.5 - March, 2010
 *      Initial Release  
 *
 * Increment/Decrement numeric inputs by using up/down arrow keys or mousewheel.
 * Use Shift & Ctrl/Cmd keys to modify increment.
 * 
 * Known Issues (v0.6):
 * Google Chrome overrides the ctrl+scroll event for browser resizing, with no known workaround       
 * 
 * The Increment jQuery plugin is provided "AS IS", with no warranties express or implied,
 * and is dual licensed under the MIT & GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 * Enjoy!  --SEAN O (@seanodotcom)
 *    
 */

(function($){

	$.fn.increment = function(options) {
	  // options
		var defaults = { 
			increment:          1,       // amount to increment/decrement
			minVal:             0,       // minimum value of input
			maxVal:             100,     // maximum value of input
			minIncrement:       0.5,     // minimum increment (Ctrl/Cmd Key modifier)
			maxIncrement:       5,       // maximum increment (Shift Key modifier)
      showArrows:         true     // show up/down arrows as UI input hint? (use UTF-8 character set & be mindful of CSS)
      /* TODO: future use
      negativeValues:     false,
			startVal:           0,
			validateInput:      false,
      delay:              0       
      */
	  };
	 	var hint = "<span style='display:inline' class='arrowshint'>&nbsp;&uarr;&darr;</span>";
	 	var valToIncrement = 0;	 	

	 	var opts = $.extend(defaults, options);

		// each function
		return this.each(function(){
	 		this.timeout = null;
	 		// display up/down arrows hint after input if option set
	 		if (opts.showArrows)
	 		{
  	 		$(this)
  	 		 .attr('autocomplete','off')    // turn off autocomplete
         .focus(function(){
            $('.arrowshint').remove();  // .remove() on focus needed for IE (?)
            $(this).after(hint);
            $('.arrowshint').css('opacity', 0.3);
         })
         .blur(function(){ $('.arrowshint').remove(); });
      }
      if ( $(this).attr('title') == '' ) $(this).attr('title','Use up/down arrows to increment/decrement value');
      /* future use
      if (opts.validateInput)
      {
      }
      */

      // keydown or mousewheel event
			//$(this).keydown(function(event){
			$(this).bind("mousewheel keydown", function(e, delta){
			  // prevent browser content resizing on ctrl-mousewheel events (doesn't stop Chrome)
			  e.preventDefault();
			 //console.log( delta );
  	    $tgt = $(e.target);
  	    $id = $tgt.attr('id');
  	    var key = ( e.keyCode || e.charCode || e.which );
  	    clearTimeout(this.timeout);
  	    this.timeout = setTimeout(function () {
  	      /* Mousewheel & keydown detection */
  	      // determine value to increment based on Ctrl(Cmd) / Shift key modifiers
  	      valToIncrement = (e.shiftKey ? opts.maxIncrement : (e.ctrlKey || e.metaKey) ? opts.minIncrement : opts.increment);
  	      // TODO: just tack on negative for down arrow
          if (delta > 0 || e.which == 38) {
            changeTime($id, 'add');
              // newval = parseFloat(num) + 1 * (e.shiftKey ? .1 : 1);
          } else if ( delta < 0 || e.which == 40 ) {
            changeTime($id, 'sub');
              //newval = parseFloat(num) - 1 * (e.shiftKey ? .1 : 1);
          }
  	    }, opts.delay);
	    });
		});  // end each
		
		// helper function
  	function changeTime(id, sign)
  	{
  	    var v = $('#'+id).val()-0;  // get current input value
  	    if (sign == 'add')
  	    {
  	        // don't allow incrementing over maximum
  	        if ( v + valToIncrement > opts.maxVal )
            {
              // alert user has reached maximum value?
              return false;
            }
  	        v += valToIncrement;
  	    } else if (sign == 'sub') {
  	        // don't allow decrementing below minimum
  	        if ( v - valToIncrement < opts.minVal )
            {
              // alert user has reached minimum value?
              return false;
            }
            v -= valToIncrement;
  	    } else {
  	      return false;  // only 'add' or 'sub' allowed
  	    }
  	    $('#'+id).val(v);  // set new value
  	}  // end each fn
  	
	};  // end main fn
	
})(jQuery);  // return jQuery object