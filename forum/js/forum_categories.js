/*custom acordion :D*/
$(document).ready(function(){
	$('p.handler').click(function(){
		var e = $(this);
		var ch = e.attr('id');					
		$('section.handlercontent').each(function(){
			if ($(this).attr('id') !== ('cont'+ch)){
				$(this).slideUp();
			}else{
				$(this).slideToggle();
			}
		}); 	
	});
});