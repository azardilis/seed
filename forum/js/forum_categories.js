/*custom acordion :D*/
$(document).ready(function(){
	$('p.handler').click(function(){
		var e = $(this);
		var ch = e.attr('id');					
		$('section.handlercontent').slideUp(); /*slide all contents up*/

		/*remove box shadows from all handlers*/
		$('section.container').css({'-moz-box-shadow':'',
			'-webkit-box-shadow':'',
			'box-shadow':''});

		e.parent().css({'-moz-box-shadow':'inset 0px 0px 1px 1px #88ccff',
			'-webkit-box-shadow':'inset 0px 0px 1px 1px #88ccff',
			'box-shadow':'inset 0px 0px 1px 1px #88ccff'
		});

		/*add to current handler*/
		$('#cont'+ch).slideToggle(); /*slide the content of this one down*/
	});
});