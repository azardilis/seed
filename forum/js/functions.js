function appendPost(strngurl){
	var sE = document.createElement('article');
	sE.setAttribute('class','post');

	//process the stringurl here to add attributes/remove attributes - in particular, we want the post ID, so that we can retrieve at a later time
	var txt = document.createTextNode(strngurl);
	sE.appendChild(txt);

	//this appends to the document
	var rSection = document.getElementById('responses');
	rSection.appendChild(sE);
}
