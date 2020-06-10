studentCheck = document.querySelector("#toggle-student-check");
checkedNames = document.querySelectorAll(".check_student");

if (studentCheck){
    studentCheck.addEventListener("change", (event)=>{
        checkedNames.forEach(element => {
            element.checked = studentCheck.checked;
        });
    })
}
