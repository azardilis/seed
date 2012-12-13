
/*append a post to the body of the thread (at level 1)*/
function appendPost(arr){
	var bd = '' ;
	for (i in arr){
		if (arr[i][0] === 'bd'){
			bd = arr[i][1];
		}
	}
	
	
	var sE = document.createElement('section');
	sE.setAttribute('class','post');

	var art = document.createElement('article');
	
	var txt = document.createTextNode('You replied : '+bd+' (refresh page for actions).');
	art.appendChild(txt);
	sE.appendChild(art);
	
	var rSection = document.getElementById('responses');
	//add node to the beginning of the posts
	rSection.insertBefore(sE,rSection.childNodes[0]);
}

/*appends to post*/
function appendToPost(arr){

	var bd = '' ;
	var parent  = 0 ;
	for (i in arr){
		if (arr[i][0] === 'bd'){
			bd = arr[i][1];
		}else if(arr[i][0] === 'r2pid'){
			parent = arr[i][1] ;
		}
	}
	
	var psts = document.createElement('section');
	psts.setAttribute('class','posts');
	
	var sE = document.createElement('section');
	sE.setAttribute('class','post');

	var art = document.createElement('article');
	art.setAttribute('class','art');
	
	var txt = document.createTextNode('You replied : '+bd+' (refresh page for actions).');
	art.appendChild(txt);
	
	
	sE.appendChild(art);
	psts.appendChild(sE);
	
	var appHere = $('article.art#'+parent).parent();
	appHere.append(psts);
}

$(document).ready(function(){
	
		/*This is AJAX for replying to a THREAD*/
		$("#replyform").submit(function(event)
		{
			var $form = $(this);
			var $inputs = $form.find("input, button,textarea") ;
			serializedData = $form.serialize();
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
					appendPost(returnArray(serializedData));
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
		
		/*This toggles the reply box on for replying to a POST*/
		$('p.reply').click(function(){
			var e = $(this);
			var pid = e.attr('pid');
			$('#rf'+pid).slideDown();
		});
		
		/*This toggles the reply box on for replying to a POST and inputs the quote*/		
		$('p.quote').click(function(){
			var e = $(this);
			var pid = e.attr('pid');
			var poster = $('article.art#'+pid).attr('poster');
			var qs = "[quote="+poster+"]"+$('article.art#'+pid).html()+"[/quote]";
			$('#rf'+pid+' textarea').html(qs);
			$('#rf'+pid).slideDown();
		});
		
		/*This is AJAX for replying to a POST*/
		$('form.psreplyform').submit(function(event)
		{
			var $form = $(this);
			var $inputs = $form.find("input, button,textarea") ;
			var serializedData = $form.serialize();			
			$inputs.attr("disabled", "disabled");
			$.ajax(
			{
				url: "/replypost",
				type: "POST",
				data: serializedData,
				contentType: 'application/x-www-form-urlencoded',
				dataType: 'html',
				success: function(data, textStatus)
				{
					appendToPost(returnArray(serializedData));
				},
				error: function(xmlhttp, textStatus, errorThrown)
				{
					alert('There was an error while replying to post.');
				},
				complete: function()
				{
					$inputs.removeAttr("disabled");
					$inputs.html('');
				}
			});
			event.preventDefault();
		});
});

function returnArray(str){
	var arr = str.split("&");
	for (i in arr){
		arr[i] = arr[i].split("=");
	}
	
	return arr;
}