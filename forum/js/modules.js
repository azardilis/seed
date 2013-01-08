$(document).ready(function() {
		$(document).delegate('h3.trigger','click',function(){
			var e = $(this);
			$('h3.trigger').each(function(){
				if (e.attr('year') !== $(this).attr('year')){
					$('div#year'+$(this).attr('year')).slideUp();
				}else{
					$('div#year'+e.attr('year')).slideToggle();
				}
			});
		});
	});