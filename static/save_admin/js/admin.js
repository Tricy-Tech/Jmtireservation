function showPopUp() {
    console.log("showing pop-up message");
    var popUp = document.getElementById("pop-up");
    popUp.style.display = "block";
}

$('input[name="_save"]').click(function() {
    alert("Your changes have been saved.");
});