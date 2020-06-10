loading = document.getElementById("loading");

function loadFormMasterRemarksTemplate(){
    loading.classList.add("show-loading");
    const url = `/staff/get_form_teacher_remark_input_template`;
    
    academic_year = document.querySelector("#academic_year").value
    semester      = document.querySelector("#semester").value
    class_name    = document.querySelector("#class_name").value
    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value

    resultDiv     = document.querySelector(".remark-template-div")
    $.post( url, 
        {
            semester, 
            academic_year,
            class_name,
            csrfmiddlewaretoken
        }, 
    function(data){
        loading.classList.remove("show-loading");
        resultDiv.innerHTML =  data;
    });
}

// GET PREVIOUS CLASS TEACHER REMARK
function loadFormMasterPreviousRemarks(event, student_id, option){
    loading.classList.toggle("show-loading");
    field = document.getElementById(event.target.dataset.field_id)
    try {
        const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value
        const url = `/staff/get_previous_remark`;
        $.post( url, 
                {
                    student_id, 
                    option,
                    csrfmiddlewaretoken,
                }, 
            function(data){
                loading.classList.toggle("show-loading");
                field.value =  data;
    });
    } catch (error) {
        loading.classList.toggle("show-loading");
    }
}

// SAVING THE REMARK
function saveRemark(event){
    const total_attendance = document.getElementById("total_attendance").value
    const student_id = event.target.dataset.student_id;

    if(! total_attendance ){
        alert("Please input the total attendance");
        return
    }
    

    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value
    semester    = document.getElementById("selected_semester").value
    class_name    = document.getElementById("selected_class_name").value
    academic_year    = document.getElementById("selected_academic_year").value

    attendance = document.getElementById(student_id+"attendance").value
    attitude = document.getElementById(student_id+"attitude").value
    conduct = document.getElementById(student_id+"conduct").value
    interest = document.getElementById(student_id+"interest").value
    remark = document.getElementById(student_id+"remark").value

    if (total_attendance < attendance){
        alert("Student's attendance cannot be greater than total attendance");
    }

    if(total_attendance 
        && attendance && attitude 
        && conduct && interest 
        && remark && student_id 
        && semester && academic_year
        && academic_year && class_name){

        form_teacher_remark =   {total_attendance, 
                                attendance, 
                                attitude,
                                conduct,
                                interest,
                                remark,
                                student_id,
                                semester,
                                academic_year,
                                class_name,
                                csrfmiddlewaretoken}
            
            loading.classList.add("show-loading");
            const url = `/staff/save_form_teacher_remark`;
            $.post( url, 
                form_teacher_remark, 
            function(data){
                loading.classList.remove("show-loading");
        });
    } else {
        alert("All fields are required!");
        loading.classList.remove("show-loading");
    }
}

function getRecords(student_id){
    let shown = document.getElementById("display_student_id")
    if (shown){shown = shown.value}

    if (shown != student_id){
        loading.classList.add("show-loading");
        const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value

        semester        = document.getElementById("selected_semester").value
        class_name      = document.getElementById("selected_class_name").value
        academic_year   = document.getElementById("selected_academic_year").value

        display = document.querySelector(".record-display")
       
        
        const url = `/staff/get_academic_record`;
        $.post( url, 
            {   student_id,
                semester,
                class_name,
                academic_year,
                csrfmiddlewaretoken},
        function(data){
            display.innerHTML = data;
            loading.classList.remove("show-loading");
    });
    }
}

function saveAllFormMasterRemarks(){
    saveBtns = document.querySelectorAll(".save-record")
    saveBtns.forEach(btn=>{
        btn.click();
    })
}

// SUBJECT RECORDS
function loadSubjectRecordTemplate(){
    academic_year = document.querySelector("#academic_year").value;
    semester      = document.querySelector("#semester").value;
    form    = document.querySelector("#form").value;
    subject_name    = document.querySelector("#subject_name").value;
    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value;

    if (! academic_year || !semester || !form || !subject_name){
        alert("Please check your selections.")
        return
    }
    resultDiv     = document.querySelector(".subject_record_template_div")
    
    loading.classList.add("show-loading");
    const url = `/staff/get_subject_score_input_template`
    $.post( url, 
        {
            semester, 
            academic_year,
            form,
            subject_name,
            csrfmiddlewaretoken
        }, 
    function(data){
        loading.classList.remove("show-loading");
        resultDiv.innerHTML =  data;
    });
}

// Generate sheet
function generateRecordSheet(){
    academic_year = document.querySelector("#academic_year").value;
    semester      = document.querySelector("#semester").value;
    form    = document.querySelector("#form").value;
    subject_name    = document.querySelector("#subject_name").value;
    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value;

    if (! academic_year || !semester || !form || !subject_name){
        alert("Please check your selections.")
        return
    }
    resultDiv     = document.querySelector(".subject_record_template_div")
    
    loading.classList.add("show-loading");
    const url = `/staff/generate_record_sheet`
    $.post( url, 
        {
            semester, 
            academic_year,
            form,
            subject_name,
            csrfmiddlewaretoken
        }, 
    function(data){
        loading.classList.remove("show-loading");
        resultDiv.innerHTML =  data;
    });
}

function loadGradingSystem(){
    const url = `/api/grading-system`
    $.get( url,    
    function(data){
        if (data.grading){
            localStorage.setItem("grading", JSON.stringify(data.grading))
        }
        else{
            alert("An error occurred, please refresh the page.")
        }

    });
}

// Generate house master remark sheet
function generateHouseMasterRemarkSheet(){
    academic_year = document.querySelector("#academic_year").value
    semester      = document.querySelector("#semester").value
    form          = document.querySelector("#form").value
    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value

    if (! academic_year || !semester || !form ){
        alert("Please check your selections.")
        return
    }
    resultDiv     = document.querySelector(".house_master_remark_template_div")
    
    loading.classList.add("show-loading");
    const url = `/staff/generate_house_master_remark_sheet`
    $.post( url, 
        {
            semester, 
            academic_year,
            form,
            csrfmiddlewaretoken
        }, 
    function(data){
        loading.classList.remove("show-loading");
        resultDiv.innerHTML =  data;
    });
}

// Generate form master remark sheet
function generateFormTeacherRemarkSheet(){
    loading.classList.add("show-loading");
    const url = `/staff/generate_form_master_remark_sheet`;
    
    academic_year = document.querySelector("#academic_year").value
    semester      = document.querySelector("#semester").value
    class_name    = document.querySelector("#class_name").value
    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value

    resultDiv     = document.querySelector(".remark-template-div")
    $.post( url, 
        {
            semester, 
            academic_year,
            class_name,
            csrfmiddlewaretoken
        }, 
    function(data){
        loading.classList.remove("show-loading");
        resultDiv.innerHTML =  data;
    });
}

function completeRecord(student_id){
    class_score = document.getElementById(student_id+"class_score").value
    exam_score = document.getElementById(student_id+"exam_score").value
    
    total   = parseFloat(class_score) * 0.3 + parseFloat(exam_score) * 0.7
    document.getElementById(student_id+"total").value = total.toFixed()

    grade   = document.getElementById(student_id+"grade")
    remark  = document.getElementById(student_id+"remark")
    position = document.getElementById(student_id+"position")

    gradingSystem = JSON.parse(localStorage.getItem("grading"));
    
    // GRADE AND REMARK
    for (let i = 0; i < gradingSystem.length; i++) {
        const item = gradingSystem[i];
        if( total >= item.min_score) {
            grade.value = item.grade
            remark.value = item.remark
            break;
        } else{
            grade.value = "F"
            remark.value = "Fail"
        }
    }

    // POSITION
    total_inputs = document.querySelectorAll("input[name=total]")
    position_inputs = document.querySelectorAll("input[name=position]")
    total_marks = []

    total_inputs.forEach(item=>{
        total_marks.push(parseInt(item.value))
    })
    
    total_marks.sort(function( a , b ){
        return a > b ? -1 : 1;
    });;

    total_inputs.forEach(item=>{
        total = parseInt(item.value);
        position = total_marks.indexOf(total) + 1;
        id = item.dataset.student_id
        document.getElementById(id+"position").value = position;
    })
}

function saveRecord(student_id){
    const csrfmiddlewaretoken   = document.querySelector("input[name='csrfmiddlewaretoken']").value
    semester                    = document.getElementById("selected_semester").value
    subject_name                = document.getElementById("selected_subject_name").value
    academic_year               = document.getElementById("selected_academic_year").value
    class_score     = document.getElementById(student_id+"class_score").value
    exam_score      = document.getElementById(student_id+"exam_score").value
    total           = document.getElementById(student_id+"total").value
    grade           = document.getElementById(student_id+"grade").value
    remark          = document.getElementById(student_id+"remark").value
    position        = document.getElementById(student_id+"position").value
    roll_no         = document.getElementById("roll_no").value

    record = {
        semester,
        subject_name,
        academic_year,
        class_score,
        exam_score,
        total,
        grade,
        remark,
        position,
        roll_no,
        student_id,
        csrfmiddlewaretoken,
    }

    loading.classList.add("show-loading");
    url = "/staff/save_subject_record"
    $.post( url,   
    record, 
    function(data){
        loading.classList.remove("show-loading");
       console.log(data);
    });
}

function saveAllSubjectRecords(){
    saveBtns = document.querySelectorAll(".save-record")
    saveBtns.forEach(btn=>{
        btn.click();
    })
}


// HOUSE MASTER
function loadHouseMasterRemarkTemplate(){
    academic_year = document.querySelector("#academic_year").value
    semester      = document.querySelector("#semester").value
    form          = document.querySelector("#form").value
    const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value

    if (! academic_year || !semester || !form ){
        alert("Please check your selections.")
        return
    }
    resultDiv     = document.querySelector(".house_master_remark_template_div")
    
    loading.classList.add("show-loading");
    const url = `/staff/house_master_remark_template`
    $.post( url, 
        {
            semester, 
            academic_year,
            form,
            csrfmiddlewaretoken
        }, 
    function(data){
        loading.classList.remove("show-loading");
        resultDiv.innerHTML =  data;
    });
}

function saveHouseMasterRemark(student_id){
    const csrfmiddlewaretoken   = document.querySelector("input[name='csrfmiddlewaretoken']").value
    semester                    = document.getElementById("selected_semester").value
    academic_year               = document.getElementById("selected_academic_year").value
    remark                      = document.getElementById(student_id+"remark").value
    
    record = {
        semester,
        academic_year,
        remark,
        student_id,
        csrfmiddlewaretoken,
    }

    loading.classList.add("show-loading");
    url = "/staff/save_house_master_remark"
    $.post( url,   
    record, 
    function(data){
        loading.classList.remove("show-loading");
       console.log(data);
    });
}

function saveAllHouseMasterRemarks(){
    saveBtns = document.querySelectorAll(".save-record")
    saveBtns.forEach(btn=>{
        btn.click();
    })
}

// GET PREVIOUS CLASS TEACHER REMARK
function loadHouseMasterPreviousRemarks(event, student_id){
    loading.classList.toggle("show-loading");
    field = document.getElementById(event.target.dataset.field_id)
    try {
        const csrfmiddlewaretoken    = document.querySelector("input[name='csrfmiddlewaretoken']").value
        const url = `/staff/get_previous_house_master_remark`;
        $.post( url, 
                {
                    student_id,                     
                    csrfmiddlewaretoken,
                }, 
            function(data){
                loading.classList.toggle("show-loading");
                field.value =  data;
    });
    } catch (error) {
        loading.classList.toggle("show-loading");
    }
}