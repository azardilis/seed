$(document).ready(function() {
		$(document).delegate('h3.trigger a','click',function(){
			$('div.year').slideUp();

			var e = $(this); /*get the a element that triggered the click event*/

			$('div#year'+e.attr('year')).slideDown();
		});
	});