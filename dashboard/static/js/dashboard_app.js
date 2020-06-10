loading = document.getElementById("loading");
const menubar = document.querySelector(".menu-bar");
const menu = document.querySelector(".menu");

menubar.addEventListener("click", ()=>{
    menu.classList.toggle("toggle-menu");
})


// TOGGLING RIGHT PANEL
const rightPanel = document.querySelector(".right-panel");
const rightPanelIcon = document.querySelector(".right-panel .icon");
if (rightPanel && rightPanelIcon){
    rightPanelIcon.addEventListener("click", ()=>{
        rightPanel.classList.toggle("hide-right-panel");
    })
}

// RIGHT PANEL TABS
tabHeader = document.querySelectorAll(".r-header-item")
if (tabHeader.length){
    tabHeader.forEach(header =>{
        header.addEventListener("click", ()=>{
            bodyId = header.dataset.toggle
            body = document.getElementById(bodyId)
            bodies = document.querySelectorAll(".r-tab-body")
            bodies.forEach(el=>{el.style.display="none"});

            body.style.display = "block";
        })
    })
}

// Tabs
tabs = document.querySelectorAll(".tabs .tab");
if (tabs.length){
    document.querySelector(".default-tab").classList.add("show-tab-body");
    tabs.forEach(element => {
        const body = document.querySelector(`.${element.dataset.toggle}`);       
        element.addEventListener("click", (event)=>{
            const bodies = document.querySelectorAll(".tab-body .body");
            
            bodies.forEach(e => {
                e.classList.remove("show-tab-body");
            })

            tabs.forEach(t=>{
                t.classList.remove("active-tab");
            })

            body.classList.add("show-tab-body");
            element.classList.add("active-tab");
        })
    })
}

tabs2 = document.querySelectorAll(".toggle-user-request button");
if (tabs2.length){
    document.querySelector("#teacher").classList.add("show-tab-body");

    tabs2.forEach(element =>{
        const body = document.querySelector(`#${element.dataset.user_type}`);
        element.addEventListener("click", (event)=>{
            const bodies = document.querySelectorAll(".tab2-body");
            
            bodies.forEach(e => {
                e.classList.remove("show-tab-body");
            })

            tabs2.forEach(t=>{
                t.classList.remove("active-tab");
            })

            body.classList.add("show-tab-body");
            element.classList.add("active-tab");
        })
    })
}

const reportForm = document.querySelector(".report-detail-form");

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

const reportFormClass = document.querySelector(".report-detail-form-class");
if (reportFormClass){
    reportFormClass.addEventListener("submit", (event)=>{
        event.preventDefault();
        var semester = document.querySelector(".report-detail-form-class #semester").value;
        var academic_year = document.querySelector(".report-detail-form-class #academic_year").value;
        var student = document.querySelector(".report-detail-form-class #student").value;
        
        academic_year = academic_year.replace("/", "-");
        student = student.split("/").join("-");
        semester = semester.replace(" ", "-");
        const student_class_id = document.querySelector(".report-detail-form-class #student_class_id").value

        if (student != "all"){
            window.location = `/results/${academic_year}/${semester}/${student}`;
        } else{
            window.location = `/results/students/${student_class_id}/${academic_year}/${semester}`;
        }
    })
}

// Request for report preview
function previewReport(){
    const semester = document.getElementById("semester").value
    const academic_year = document.getElementById("academic_year").value
    const student = document.getElementById("student").value
    const student_class_id = document.getElementById("student_class_id").value
    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value

    if (semester != "" && academic_year != "" && student != "" && student_class_id != ""){
        if (student != "all"){
            event.preventDefault()
            const reportDiv = document.getElementById("student-report")
            const url = `/student/one_report_preview`;

            $.post( url, 
                    {
                        semester, 
                        academic_year,
                        student,
                        student_class_id,
                        csrfmiddlewaretoken
                    }, 
                function(data){
                    reportDiv.innerHTML =  data;
            });
        } 
        else{
            alert("Can't preview the report of all students");
        }
    } else{
        alert("All fields are required, please.");
    }
}

// CHECK BLANCE
function checkBalance(element){
    loading.classList.add("show-loading");
    balance = document.querySelector("#balance")
    const url = `/sms/check-balance`;
    $.get( url, 
        function(data){
            loading.classList.remove("show-loading");
            balance.innerHTML =  data;
    });
}

function toggleGroupedCheckbox(element, calzz){
    boxes = document.querySelectorAll(calzz);
    boxes.forEach(box =>{
        box.checked = element.checked;
    })
}

// DELETION GRADING SYSTEM
function deleteGradingSystem(event){
    response = confirm("Confirm deletion of grading system!");
    if (!response){
        event.preventDefault();
    }
}

// FORM SUBMISSION
function submitForm(form_id){
    document.getElementById(form_id).submit();
}


// RIGHT PANEL USER SEARCH
const searchInput = document.getElementById("user-query")
const usersDiv = document.getElementById("users")

function fetch_users(){
    const query = searchInput.value
    if (query){
        const url = `/accounts/fetch_users/`
        const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value

        $.post( url, 
            {
                query, 
                csrfmiddlewaretoken
            }, 
        function(data){
            usersDiv.innerHTML =  data;
            console.log(data)
        });
    }
}