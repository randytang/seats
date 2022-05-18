const inputElmt = document.querySelector("#search-box");
const formElmt = document.querySelector(".form-inactive");
inputElmt.addEventListener('focus', activateInput);
inputElmt.addEventListener('focusout', (e) => { 
	formElmt.setAttribute("class", "form-inactive");
});

const printBtn = document.querySelector("#printBtn");
printBtn.addEventListener('click', print_selected_apps);

let loader_container = document.querySelector(".loader-container");
let loader_animation = document.querySelector(".loader-animation");

function activateInput(e) {
	formElmt.setAttribute("class", "form-inactive form-active");
}


function print_selected_apps(e) {
	loader_container.setAttribute("class", "loader-container active");
	loader_animation.setAttribute("class", "loader-animation active");

	const dllink = document.createElement("a");

	const aForm = new FormData(document.querySelector("#selected-apps"));
	fetch("/sef/printapps", {
		method: 'POST',
		body: aForm
	})
	.then(function(response) {
		let content_disp_header = response.headers.get('Content-Disposition');
		let filename = content_disp_header.split('filename=')[1];
		filenameStripped = filename.replace(/"/g, "");
		dllink.setAttribute("download", filenameStripped);
        /*  chrome/chromium will have setting by default to not 
         *  ask where to save downloaded file as opposed to firefox.
         *  so if using in chrome/chromium, file will automatically
         *  be downloaded to default path/directory set/specified in
         *  settings, i.e 'Downloads'.
         *
         */
		return response.blob();
	})
	.then(function(response) {
		let aURLtoPDF = URL.createObjectURL(response);
		dllink.setAttribute("href", aURLtoPDF);
		let body = document.querySelector("body");
		body.appendChild(dllink);
		loader_container.setAttribute("class", "loader-container");
		loader_animation.setAttribute("class", "loader-animation");
		dllink.click();
	});
}



	


	

