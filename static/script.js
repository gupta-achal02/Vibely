var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
output.innerHTML = slider.value;

slider.oninput = function() {
output.innerHTML = this.value;
}

function picture(){ 
    document.getElementById('load').style.display='block';
    document.getElementById('load').style.margin='auto';

}