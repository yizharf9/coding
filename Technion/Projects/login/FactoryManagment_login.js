let Username = document.getElementById('Username')
let Password = document.getElementById('Password')

function test(){
    let 
}

async function getData() {
    let resp =await fetch('https://localhost:44399/api/Users')
    let data = await resp.json()
    console.table(data)

    let auth = false
    data.forEach(user => {
        if (user.userName == Username |user.password == Password) {
            auth = true
            console.log(user)
        }else{alert()}
    })
}


async function login() { 
    let obj = {
        username : Username.value,
        password : Password.value
    }

    let Params = {
        method : 'POST',
        body : JSON.stringify(obj),
        headers : {'Content-type':'application/json'},
    }
    let resp = await fetch('https://localhost:44399/api/login',Params)

    let data = await resp.json()
    console.log(data.auth)
    if (data.auth) {
        //window.open('./FactoryManagment_home_page.html', '_blank',)
        let temp = document.getElementById('loginInp')
        temp.innerHTML = ""
        let authBox = document.createElement('a')
        authBox.href = "./FactoryManagment_home_page.html?username="
        authBox.innerText = "You are being redirected to your'e home page"
        
        let br = document.createElement('br')
        temp.appendChild(br)
        temp.appendChild(br)
        temp.appendChild(br)

        temp.appendChild(authBox)
    }else{
        alert(data.username)
    }
    return await data
}
console.log('hello world')