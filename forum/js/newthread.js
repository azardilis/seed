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
				alert('Thread created!');
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				alert('There was an error while creating a new thread.');
			},
			complete: function()
			{
				$inputs.removeAttr("disabled");
			}
		});
		event.preventDefault();
	});
});