let Username = document.getElementById('Username').value
let Password = document.getElementById('Password').value

let test
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

async function Test() { 
    let obj = {
        userName : Username,
        password : Password
    }

    let Params = {
        method : 'POST',
        body : JSON.stringify(obj),
        headers : {'Content-type':'application/json'},
    }
    let resp = fetch('https://localhost:44399/api/login',Params)
    console.log(await resp)
    let data = await resp.json()
    console.log(data)
    console.log()
}


