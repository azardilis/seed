function appendPost(strngurl){
	var sE = document.createElement('article');
	sE.setAttribute('class','post');

	//process the stringurl here to add attributes/remove attributes - in particular, we want the post ID, so that we can retrieve at a later time
	var txt = document.createTextNode(strngurl);
	sE.appendChild(txt);
	var rSection = document.getElementById('responses');
	//add node to the beginning of the posts
	rSection.insertBefore(sE,rSection.childNodes[0]);
}

$(document).ready(function(){
		$("#replyform").submit(function(event)
		{
			var $form = $(this),
			$inputs = $form.find("input, button,textarea"),
			serializedData = $form.serialize();
			alert('called2');
			$inputs.attr("disabled", "disabled");

			$.ajax(
			{
				url: "/replythread",
				type: "POST",
				data: serializedData,
				contentType: 'application/x-www-form-urlencoded',
				dataType: 'html',
				success: function(data, textStatus)
				{
					appendPost(serializedData);
				},
				error: function(xmlhttp, textStatus, errorThrown)
				{
					alert('There was an error while replying to thread.');
				},
				complete: function()
				{
					$inputs.removeAttr("disabled");
				}
			});
			event.preventDefault();
		});
});