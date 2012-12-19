$(document).ready(function(){
	$('img.dir').click(function(){
		scroll($(this).attr('dir'));
	});

	$('ul#modulebar').css('width',$('ul#modulebar').children().length * 404);

});

function scroll(dir){
	$('#modulenav').scrollTo(dir+'=150px',200,{queue:true, axis:'x'});
}