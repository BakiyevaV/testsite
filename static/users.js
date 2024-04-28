const domain = 'http://127.0.0.1:8080/';
let list = document.getElementById('list');
function listLoad() {
    fetch(domain + 'api/users/')
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        let s = '<ul>';
        for (let i = 0; i < data.length; i++) {
            s += `<li>${data[i].id } - ${ data[i].username }</li>`;
        }
        s += '</ul>';
        console.log(s)
        document.getElementById('list').innerHTML = s;
    })
    .catch(error => {
        window.alert(error.message);
    });
}
console.log('Hello')
listLoad();