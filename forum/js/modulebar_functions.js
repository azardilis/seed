$(document).ready(function(){
	$('img.dir').click(function(){
		scroll($(this).attr('dir'));
	});

	var tw = 0 ;
	$('ul#modulebar').children().each(function(){
		tw += $(this).width();
	});
	$('ul#modulebar').css('width',tw + ($('ul#modulebar').children().size()*12));
	curr = 0 ; /*counter that will hold the current position, initialized here*/
	total = $('ul#modulebar').children().size(); /*total modules subscribed to*/

});

function scroll(dir){
	curr = (curr + parseInt(dir))%total ;
	$('#modulenav').scrollTo('li:eq('+curr+')',200,{queue:true, axis:'x'});
}