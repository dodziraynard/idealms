const tabs = document.querySelectorAll(".user-tabs .tab");
const form_body = document.querySelector(".form-body");
const user_type = document.querySelector("#user_type")

form_body.addEventListener("transitionend", ()=>{
    // form_body.style.opacity = 1;
    // form_body.style.transform = 'rotateY(180deg)';
    // form_body.style.transition = "0.5s all ease";
    // form_body.classList.remove("toggle-form-body");
    // console.log(form_body.style)
})

if (tabs){
    tabs.forEach(tab =>{
        tab.addEventListener("click",() =>{
            const tabs = document.querySelectorAll(".user-tabs .tab")
            tabs.forEach(t =>{
                t.classList.remove("active-tab");
            })

            form_body.classList.toggle("toggle-form-body");
            tab.classList.add("active-tab");
            user_type.value = tab.dataset.user;
            document.querySelector(".form-body .selected-user").innerText = tab.dataset.user;
        })
    })
}

window.addEventListener("load", ()=>{
    const text = document.querySelector(".intro-text")
    const form = document.querySelector("form");

    text.classList.add("undo-transform")
    form.classList.add("undo-transform")
})