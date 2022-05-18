var canvas = document.querySelector("canvas");
var signaturePad = new SignaturePad(canvas);
var clearBtn = document.querySelector("#clear");
var signatureInputElmt = document.querySelector("#sign_input");
var hiddenElmt = document.querySelector("input[type='hidden']");
const saveBtn = document.querySelector("#save");
var bodyElmt = document.querySelector("body");
const signcontainer = document.querySelector("#signature-container");

function renderSign(e) {
	if (signaturePad.isEmpty()) {
		alert('You have to sign above the signature line first before clicking the sign button!');
	} else {
		if (signcontainer.hasChildNodes()) {
			while (signcontainer.hasChildNodes()) {
				signcontainer.removeChild(signcontainer.lastChild);
			}
		} 
		var signLabel = document.createElement("label");
		signLabel.setAttribute("for", "student_sign");
		var signText = document.createTextNode("Signature: ");
		signLabel.appendChild(signText);
		signcontainer.append(signLabel);
		signURL = canvas.toDataURL();
		hiddenElmt.setAttribute("value", signURL);
		var imgElmt = document.createElement('img');
		imgElmt.setAttribute('src', signURL);
		imgElmt.setAttribute('id', "signImg");
		signcontainer.append(imgElmt);
		signaturePad.clear();
	}
}


function clearPad(e) {
	signaturePad.clear();
}

saveBtn.addEventListener('click', renderSign);
clearBtn.addEventListener('click', clearPad);

