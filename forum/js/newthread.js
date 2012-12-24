$(document).ready(function()
{
	$("#newthreadform").submit(function(event)
	{
		var $form = $(this),
		$inputs = $form.find("input, button,textarea"),
		serializedData = $form.serialize();

		$inputs.attr("disabled", "disabled");

		$.ajax(
		{
			url: "/createnewthread",
			type: "POST",
			data: serializedData,
			contentType: 'application/x-www-form-urlencoded',
			dataType: 'html',
			success: function(data, textStatus)
			{
				$('#serverResponse').html('The new thread was created succesfully. Visit it <a href="/showthread?tid='+data+'">here</a>.');
				$('#serverResponse').attr('class','success');
				$('span#close').attr('class','success');
				$('#serverResponse').fadeIn();
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				$('#serverResponse').html('There was an error while creating the new thread.');
				$('#serverResponse').attr('class','error');
				$('span#close').attr('class','error');
				$('#serverResponse').fadeIn();
			},
			complete: function()
			{
				$inputs.removeAttr("disabled");
			}
		});
		event.preventDefault();
	});

	$(document).delegate('span#close','click',function(){
		$('#serverResponse').fadeOut('slow');
	});
});