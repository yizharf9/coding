let Username = document.getElementById('Username')
let Password = document.getElementById('Password')

function test(){
    console.log(Username.value)
    console.log(Password.value)

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
        }
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
    if (data) {
        window.open('./FactoryManagment_home_page.html', '_blank',)
    }else{
        alert('invalid password or username!')
    }
    return await data
}

