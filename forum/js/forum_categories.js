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

	$(document).delegate('span.btn-toggle-subs','click',function(){
			var e = $(this);
			serializedData = 'mcode='+e.attr('mid');
			$.ajax(
			{
				url: "/subscriptions",
				type: "POST",
				data: serializedData,
				contentType: 'application/x-www-form-urlencoded',
				dataType: 'html',
				success: function(data)
				{
					e.html(data);
				},
				error: function(xmlhttp, textStatus, errorThrown)
				{
					console.log('There was an error while toggling subscriptions.');
				},
				complete: function()
				{
					console.log('Toggling subscription completed');
				}
			});
	});
});