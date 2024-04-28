if (document.getElementById('id_is_limited')) {
    let limited_checkbox = document.getElementById('id_is_limited');
    let hidden_elements = document.getElementsByClassName('hidden')
    let hidden_elements_array = Array.from(hidden_elements)
    limited_checkbox.addEventListener('change', function() {
        if (this.checked) {
            hidden_elements_array.forEach(function (element) {
                element.classList.remove('hidden');
            });
s
        }else{
            hidden_elements_array.forEach(function (element) {
                element.classList.add('hidden');
            });
        }
    })
}
if (document.title == 'Edit task'){
    get_bbs()
    console.log(document.title )
    if(document.getElementById('edit_form')) {
        const form = document.getElementById('edit_form')
        let originalValues = []
        let tasksToDelete = [];
        let taskToCreate = {}
        const updates = {};
        let id_ = []
        const csrfToken = document.querySelector('[name="csrfmiddlewaretoken"]').value;
        const headers = {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
            }
        const bbsDetailUrl = "{% url 'taskboard:bbs-detail' 'dummy_id' %}".replace('dummy_id', '');
        form.querySelectorAll('input, textarea, select').forEach(field => {
            originalValues[field.name] = field.value;

        });
        form.addEventListener('submit', function (event) {
            event.preventDefault();
            form.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
                if (checkbox.checked) {
                    tasksToDelete.push({id: checkbox.parentElement.dataset.form_id, action: "DELETE"});
                }
            });

            form.querySelectorAll('input[type="text"],input[type="date"], textarea, select').forEach(field => {
                if (originalValues[field.name] !== field.value) {
                    const formId = field.parentElement.dataset.form_id;
                    if (formId && formId !== "None") {
                        if (!updates[formId]) {
                            updates[formId] = {
                                id: formId,
                                action: "PUT",
                                data: []
                            };
                        }
                        updates[formId].data.push({[field.name]: field.value});
                    } else {
                        taskToCreate[field.name] = field.value;
                    }
                }
            });
            console.log(taskToCreate)
            console.log(updates)
            console.log(updates.length)
            if(Object.keys(updates).length > 0){
                console.log(Object.keys(updates).length)
                Object.keys(updates).forEach(formId => {
                    id_.push(formId)
                    console.log(formId)
                    const elementsWithDataRequestId = document.querySelectorAll('[data-form_id]');
                    elementsWithDataRequestId.forEach(element =>  {
                        if (element.dataset.form_id == formId){
                            let children = element.querySelectorAll('input[type="text"],input[type="date"], textarea, select')
                            children.forEach(ch =>{
                                 let obj = {};
                                 obj[ch.name] = ch.value;
                                 console.log(obj)
                                 updates[formId].data.push(obj)
                                 console.log(updates)
                            })
                        }
                    })
                })
                id_.forEach(id => {
                    let postData = {};
                    updates[id].data.forEach(item =>{
                        console.log(item)
                        for (let key in item) {
                            const newKey = key.replace(/form-\d+-/, '');
                            postData[newKey] = item[key];
                        }
                    })
                    method = 'PUT'
                    let url =  `http://127.0.0.1:8080/api/tasks/${id}/`
                    console.log(url)
                    console.log(headers)
                    console.log(postData)
                    console.log(JSON.stringify(postData))
                    fetch(url, {
                        method: method,
                        headers: headers,
                        body: JSON.stringify(postData),
                        credentials: 'include'
                    })
                    .then(response => {
                        console.log(response)
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                    })
                })
            }

            if (tasksToDelete){
                tasksToDelete.forEach(methodInfo => {
                    console.log(tasksToDelete)
                    method = 'DELETE'
                    const postData = {};
                    let url =  `http://127.0.0.1:8080/api/tasks/${methodInfo.id}/`
                    fetch(url, {
                        method: method,
                        headers: headers,
                        body: undefined,
                        credentials: 'include'
                    })
                    .then(response => {
                        console.log(response)
                        if (!response.ok) {
                            throw new Error(`HTTP error! Status: ${response.status}`);
                        }
                    })
                })
            }

            if (Object.keys(taskToCreate).length > 0){
                const postData = {};
                for (let key in taskToCreate) {
                    const newKey = key.replace(/form-\d+-/, '');
                    postData[newKey] = taskToCreate[key];
                }
                console.log(postData);
                console.log(taskToCreate)
                console.log(headers)
                fetch('http://127.0.0.1:8080/api/tasks/', {
                    method: 'POST',
                    headers: headers,
                    body: JSON.stringify(postData),
                    credentials: 'include'
                })
                .then(response => {
                    console.log(response)
                    if (!response.ok) {
                        throw new Error(`HTTP error! Status: ${response.status}`);
                    }
                })
            }

        })
        get_bbs()
    }
}

function get_bbs(){
    fetch('http://127.0.0.1:8000/api/bbs/')
    .then(response => {
        console.log(response)
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        else {
            const data = response.json()
            console.log(data)
        }
    })
}
