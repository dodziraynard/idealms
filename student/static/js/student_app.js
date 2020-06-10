const reportForm = document.querySelector(".report-detail-form");
console.log(reportForm)

if (reportForm){
    reportForm.addEventListener("submit", (event)=>{
        event.preventDefault();
        var semester = document.getElementById("semester").value;
        var academic_year = document.getElementById("academic_year").value;
        var student = document.getElementById("student").value;
        
        academic_year = academic_year.replace("/", "-");
        student = student.split("/").join("-");
        semester = semester.replace(" ", "-");
        const student_class_id = document.getElementById("student_class_id").value

        if (student != "all"){
            window.location = `/results/${academic_year}/${semester}/${student}`;
        } else{
            window.location = `/results/students/${student_class_id}/${academic_year}/${semester}`;
        }
        
    })
}