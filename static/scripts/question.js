function dropItDown() {

    document.getElementById("dropdown-content").classList.toggle("show");
}

/*
function pagination() {

    var divs = document.getElementsByClassName('question');
    var numTabs = 0;
    for (var i = 0; i < divs.length; i++) {
        if (divs[i].id.indexOf('tab') != -1)
            numTabs++;
    }
    alert(numTabs);
}



window.onload = pagination;
*/

function validateForm() {
    var x = document.forms["myForm"]["fname"].value;
    if (x == "" || x.length() > 45) {
        alert("All questions must be filled out.");
//document.getElementById("error").innerHTML = "Error!";
        return false;
    }
}

