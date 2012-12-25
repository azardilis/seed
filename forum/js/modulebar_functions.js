$(document).ready(function(){
	$('img.dir').click(function(){
		scroll($(this).attr('dir'));
	});

	var tw = 0 ;
	$('ul#modulebar').children().each(function(){
		tw += $(this).width();
	});
	$('ul#modulebar').css('width',tw + ($('ul#modulebar').children().size()*12));

});

function scroll(dir){
	$('#modulenav').scrollTo(dir+'=150px',200,{queue:true, axis:'x'});
}