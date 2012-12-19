/*custom acordion :D*/
$(document).ready(function(){
	$('p.admin-handler').click(function(){
		var e = $(this);
		var ch = e.attr('id');					
		$('section.admin-handlercontent').slideUp(); /*slide all contents up*/

		

		/*add to current handler*/
		$('#cont'+ch).slideToggle(); /*slide the content of this one down*/
	});
});