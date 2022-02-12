
async function login() { 
    let Username = document.getElementById('Username')
    let Password = document.getElementById('Password')

    let obj = {
        username : Username.value,
        password : Password.value
    }
    let Params = {
        method : 'POST',
        body : JSON.stringify(obj),
        headers : {'Content-type':'application/json'},
    }
    let resp = await fetch('https://localhost:44375/api/login',Params)

    let data = await resp.json()
    if (data.Auth) {

        localStorage.setItem('ID',data.ID) 
        localStorage.setItem('fullName',data.fullName) 
        localStorage.setItem('numOfActions',parseInt(data.numOfActions)) 

        // let UserID =  "UserID="+data.ID
        // let fullName = "fullName="+data.fullName
        // let numOfActions =  "numOfActions="+data.numOfActions
        // let usp= "?&" +UserID +"&" +fullName+"&"+numOfActions
        document.location.href ='./homePage.html'
    }else{
        alert(data.userName)
    }
}

async function checkDate() {
    let resp = await fetch("https://localhost:44375/api/Values/1") 
}

//#region base functions - exist in every page

function logOut(){
    if(confirm('you are about to log-out of system \nare you sure?')){
        document.location.href = "C:/Users/user/coding/Technion/Projects/Factory_managment/html/Login.html"
    }
}

function greet() {
    let data = localStorage

    let ID = data.getItem('ID')
    let fullName = data.getItem('fullName')
    let numOfActions = data.getItem('numOfActions')

    let UserFullName = document.getElementById('fullName')
    UserFullName.innerText = "Hello there, \n"+ fullName+'!\n you have ' + numOfActions+" actions left today..."
}

function getInfo(status) {
    let ID = localStorage.getItem('ID')
    let fullName = localStorage.getItem('fullName')
    let numOfActions = localStorage.getItem('numOfActions')

    if (status) {
        console.log(ID)
        console.log(numOfActions)
        console.log(fullName)
    }
}

async function reduceActions() {
    let ID = localStorage.getItem('ID')
    let numOfActions = localStorage.getItem('numOfActions')
    let fullName = localStorage.getItem('fullName')

    let ActionParams = {
        method : "PUT",
        headers : {'Content-type':'application/json'},
    }

    let Action = await fetch('https://localhost:44375/api/Values/'+ID,ActionParams)
    let ActionResp = await Action.json()

    numOfActions--
    localStorage.setItem('numOfActions',numOfActions)
    window.location.reload()
}

//#endregion


//#region department related functions...

async function getDeps() {
    //#region http request - gettting Departments
    let aresp = await fetch('https://localhost:44375/api/Departments')
    let Departments =await aresp.json()
    console.log(Departments)
    //#endregion

    let depTable = document.getElementById('depTable')

    Departments.forEach(department => {
        let ID = localStorage.getItem("ID")
        let numOfActions = localStorage.getItem("numOfActions")
        let fullName = localStorage.getItem("fullName")

        let currTr = document.createElement('tr')

        //#region raw data - Manager and Name 
        let DataTd = document.createElement('td')
        currTr.appendChild(DataTd)
        
        let name = document.createElement('a')
        DataTd.appendChild(name)
        name.innerText = department.Name
        name.href = './Departments_detailed.html' + "?&depID="+department.ID+"&Name="+department.Name

        let Manager = document.createElement('td')
        DataTd.appendChild(Manager)
        let depManager = department.managerFull 
        depManager_FullName = depManager.firstName +" "+depManager.lastName
        Manager.innerText = depManager_FullName
        //#endregion

        //#region modification - edit and delete
        let modTd = document.createElement('td')
        currTr.appendChild(modTd)
        
        //edit link - adding matching url params
        let edit = document.createElement('a')
        modTd.appendChild(edit)
        edit.innerText = "edit"
        edit.href = './Departments_edit.html' + "?&depID="+department.ID+"&Name="+department.Name+"&Manager="+ depManager.ID
        
        let Break = document.createElement('br')
        modTd.appendChild(Break)
        
        //delete link
        if (department.empList.length==0) {
            let Delete = document.createElement('button')
            let Value = department.ID
            Delete.value = department.ID
            Delete.innerText = 'Delete'

            Delete.onclick = async function () 
            {
                if (confirm('you are about to delete this department! \nare you sure you want to do that?')) 
                {
                    if(numOfActions>0)
                    {
                        let delParams = {
                            method : "DELETE",
                            headers : {'Content-type':'application/json'},
                        }
                        let uptResp = await fetch('https://localhost:44375/api/Departments/'+Value,delParams)
                        let data =await uptResp.json()
                        alert(data)
                            
                        let ActionParams = {
                            method : "PUT",
                            headers : {'Content-type':'application/json'},
                        }
                        let Action = await fetch('https://localhost:44375/api/Values/'+ID,ActionParams)
                        let ActionResp = await Action.json()
                        console.log(ActionResp)
                        localStorage.setItem('numOfActions',ActionResp)

                        await reduceActions()
                    }
                    else
                    {
                        alert('you dont have any more actions left today...\n try again tommorow')
                        window.location.href = './html/Login.html'

                    }
                }
                window.location.reload()
            }
            modTd.appendChild(Delete)
        }
        //#endregion

        depTable.appendChild(currTr)
    })
}

async function getDep(){
    let usp = new URLSearchParams(window.location.href)
    let depID = usp.get("depID")
    
    let resp = await fetch('https://localhost:44375/api/Departments/'+depID)
    let data =await resp.json()

    let empTable = document.getElementById('empTable')
    empTable.border = 1
    empTable.style.margin = "auto"

    //#region adding manager data
    let Manager_tr = document.createElement('tr')

    let Manager_fname_td = document.createElement('td')
    Manager_fname_td.innerText = data.managerFull.firstName
    Manager_fname_td.href = '../Employees/Employees_detailed.html?'
    +'&ID='+data.managerFull.ID
    +'&firstName='+data.managerFull.firstName
    +'&lastName='+data.managerFull.lastName
    +'&startWorkYear='+data.managerFull.startWorkYear


    Manager_tr.appendChild(Manager_fname_td)

    let Manager_lname_td = document.createElement('th')
    Manager_lname_td.innerText = data.managerFull.lastName
    Manager_tr.appendChild(Manager_lname_td)
    
    let Manager_recruit_td = document.createElement('th')
    Manager_recruit_td.innerText = data.managerFull.startWorkYear
    Manager_tr.appendChild(Manager_recruit_td)

    empTable.appendChild(Manager_tr)
    //#endregion

    data.empList.forEach(emp => {//adding all Employees
        let newTr = document.createElement('tr')

        let fname = document.createElement('td')
        newTr.appendChild(fname)
        fname.innerText = emp.firstName+" "+emp.lastName

        //#region employee url params
        let IDParam = "&ID="+emp.ID
        let fnameParam = "&firstName="+emp.firstName
        let lnameParam = "&lastName="+emp.lastName
        let recruitParam = "&startWorkYear="+emp.startWorkYear
        //#endregion

        fname.href = '../Employees/Employees_detailed.html?'+IDParam+fnameParam+lnameParam+recruitParam

        let lname = document.createElement('td')//lastName
        newTr.appendChild(lname)
        lname.innerText = emp.lastName
        
        let SWY = document.createElement('td')//start work year
        newTr.appendChild(SWY)
        SWY.innerText = emp.startWorkYear

        empTable.appendChild(newTr)
    });
    getInfo()
}

async function findDep(){

    let depName = document.getElementById('NameInp')
    let depManager = document.getElementById('Employees')

    let resp = await fetch('https://localhost:44375/api/Employees/')
    let Emps =await resp.json()
    Emps.forEach(emp => {
        let newOption = document.createElement('option')
        newOption.value = emp.ID
        
        newOption.innerText = emp.firstName+' '+emp.lastName
        depManager.appendChild(newOption)
    });

    let usp = new URLSearchParams(window.location.href)
    let Name = usp.get('Name')
    let Manager = usp.get('Manager')

    depName.value = Name
    depManager.value = Manager
}

async function AddDep(){
    let ID = localStorage.getItem("ID")
    let numOfActions = localStorage.getItem("numOfActions")
    let fullName = localStorage.getItem("fullName")

    let depName = document.getElementById('NameInp').value
    let depManager = document.getElementById('Employees').value
    let depID = new URLSearchParams(window.location.href).get('depID')
    let usp = new URLSearchParams(window.location.href)
    console.log(depID)

    if (parseInt(numOfActions)>0)
    {
        //#region http params
        let upt = {
            ID: depID,
            Name : depName,
            Manager : depManager
        }
        let params = {
            method : "POST",
            body : JSON.stringify(upt),
            headers : {'Content-type':'application/json'},
        }
        //#endregion

        let addResp = await fetch('https://localhost:44375/api/Departments/'+depID,params)
        let data =await addResp.json()
        alert(data)
        await reduceActions()
        window.location.reload()
        
    } 
    else if(!parseInt(usp.get('numOfActions'))>0) 
    {
        alert('you dont have any more actions left today...\n try again tommorow')
        window.location.href = './html/Login.html'
    }
    else
    {
        alert('invalid update input! \nmake sure all required fields are filled...')
    }
}

async function EditDep(){

    let depName = document.getElementById('NameInp').value
    let depManager = document.getElementById('Employees').value
    
    let depID = new URLSearchParams(window.location.href).get('depID')
    console.log(depID)

    let upt = {
        ID: depID,
        Name : depName,
        Manager : depManager
    }
    let params = {
        method : "PUT",
        body : JSON.stringify(upt),
        headers : {'Content-type':'application/json'},
    }
    
    if (!depName==' '&&localStorage.getItem('numOfActions')>0) {
        let uptResp = await fetch('https://localhost:44375/api/Departments/'+depID,params)
        let data =await uptResp.json()
        alert(data)
        await reduceActions()
        window.location.reload()
    }
    else if(localStorage.getItem('numOfActions')<=0) 
    {
        alert('you dont have any more actions left today...\n try again tommorow')
        window.location.href = './html/Login.html'
    }
    else
    {
        alert('invalid update input! \nmake sure all required fields are filled...')
    }
}

function showAdd() {
    let checked = document.getElementById('addNew').checked
    let saveDep = document.getElementById('saveDep')
    let addDep = document.getElementById('addDep')

    if (checked) 
    {
        addDep.style.display = 'block'
        saveDep.style.display = 'none'
    }
    else if(!checked)
    {
        addDep.style.display = 'none'
        saveDep.style.display = 'block'
    }
}

//#endregion


//#region Employees related functions...

async function getEmp(value){

    let table = document.getElementById('empData')
    table.innerHTML = null
    
    let usp = new URLSearchParams(window.location.href)
    
    let ID = localStorage.getItem('ID')

    let numOfActions = localStorage.getItem('numOfActions')

    let evaluate = async (value)=>{
        let depresp = await fetch('https://localhost:44375/api/Departments/')
        let Departments = await depresp.json()
        let DepsNames = Departments.map(dep=>dep.Name)

        let resp = await fetch('https://localhost:44375/api/Employee_Shift')
        let emps = await resp.json()

        if (DepsNames.includes(value)) {
            return emps.filter(x=>x.departmentID == Departments.find(x=>x.Name == value).ID)
        }
        else if (emps.map(x=>x.firstName).includes(value)||emps.map(x=>x.lastName).includes(value))
        {
            return emps.filter(emp=>emp.firstName == value || emp.lastName == value)
        }
        else
        {
            return emps //[emps,Departments]
        }
    }
    
    let empsSetup =async (emps)=>{
        emps = await evaluate(emps)//[0]
        emps.forEach(emp => {
        
            //#region create employee table
            let table = document.getElementById('empData')
            
            let newTr = document.createElement('tr')
            
            let fname = document.createElement('td')//first name
            fname.innerText = emp.firstName
            newTr.appendChild(fname)
        
            let lname = document.createElement('td')//last name
            lname.innerText = emp.lastName
            newTr.appendChild(lname)
        
            let depName = document.createElement('div')
            depName.className = 'depDiv'
            
            depName.innerText =emp.departmentID
            
            newTr.appendChild(depName)
        
            let recruit = document.createElement('td')//start work year
            recruit.innerText = emp.startWorkYear
            newTr.appendChild(recruit)
            //#endregion
        
            //#region create shifts data
            let shiftsTd = document.createElement('td')//td for shifts 
            newTr.appendChild(shiftsTd)
        
            let shifts = document.createElement('ul')//shift list in td...
            shifts.style.background = 'white'    
            shiftsTd.appendChild(shifts)
        
            emp.Shifts.forEach(shift => {// creating all shift list items...
                let deleteShiftButton = document.createElement('button')
        
                //?optional
                // deleteShiftButton.onclick = function () {
                //     let DeletedShift = {
                //         ID: 0,
                //         EmployeeID: empID,
                //         ShiftID: PickedShift
                //     }
        
                //     let params = {
                //         method:"DELETE",
                //         body: JSON.stringify(AddedShift),
                //         headers: {'Content-type':'application/json'}
                //     }
                //     console.log(AddedShift)
                //     let resp = await fetch('https://localhost:44375/api/Employee_Shift/'+shift.ID,params)
                //     let status = await resp.json()
                //     alert(status)
                // }
        
                let date =document.createElement("li") 
                date.innerText = "date : "+ shift.Date
        
                shifts.appendChild(date)
        
                let startTime =document.createElement("li") 
                startTime.innerText = "startTime : "+ shift.startTime
                shifts.appendChild(startTime)
        
                let endTime =document.createElement("li") 
                endTime.innerText = "endTime : "+ shift.endTime
                shifts.appendChild(endTime)
        
                let br =document.createElement("br") 
                shifts.appendChild(br)
            });
            //#endregion
            
            //#region create modification buttons
            recruit.innerText = emp.startWorkYear
            newTr.appendChild(recruit)
            
            let modTd = document.createElement('td')
            let DeleteButton = document.createElement('button')
            DeleteButton.innerText = 'Delete'
            DeleteButton.onclick =async function () {
                if ((numOfActions)>0) {
                    deleteEmployee(emp.ID)
                }
                else
                {
                    alert('you dont have any more actions left today...\n try again tommorow')
                    window.location.href = '../Login.html'
                }
            }
        
            let AddShift = document.createElement('button')
            AddShift.innerText = 'Add a shift'
            AddShift.onclick = async function () {
                window.location.href ='./Employees_addShift.html?&'+`empID=${emp.ID}&empName=${emp.firstName} ${emp.lastName}&departmentID=${currdep}`
            }
        
            let EditEmployee = document.createElement('button')
            EditEmployee.innerText = 'edit Employee'
            EditEmployee.onclick = async function () {
                window.location.href ='./Employees_edit.html'+'?&'+
                `empID=${emp.ID}&firstName=${emp.firstName}&lastName=${emp.lastName}&startWorkYear=${emp.startWorkYear}&departmentID=${emp.departmentID}`
            }
            //#endregion
        
            //#region modification TD arrangement
            modTd.appendChild(DeleteButton)
        
            modTd.appendChild(document.createElement('br'))
            modTd.appendChild(document.createElement('br'))
        
            modTd.appendChild(AddShift)
        
            modTd.appendChild(document.createElement('br'))
            modTd.appendChild(document.createElement('br'))
        
            modTd.appendChild(EditEmployee)
            newTr.appendChild(modTd)
            //#endregion
        
            table.appendChild(newTr)
        })
    }
    await empsSetup(value)
}

async function createEmployee() {
    let fname = document.getElementById('fname').value
    let lname = document.getElementById('lname').value
    let recruitDate = document.getElementById('Date').value
    let depID = document.getElementById('Departments').value

    let condition = fname!=null&&lname!=null&&recruitDate!=null&&depID!=null
    if (condition) {
        let newEmp = {
            firstName : fname,
            lastName : lname,
            startWorkYear : recruitDate,
            departmentID : depID
        }
        let params = {
            method: "POST",
            body : JSON.stringify(newEmp),
            headers : {'Content-type':'application/json'},
        }
        let resp = await fetch('https://localhost:44375/api/Employees',params)
        let status = await resp.json()
        await reduceActions()
        alert(status)
    }
    else
    {
        alert('invalid input!\nmake sure all required fields are filled...')
    }
}

async function deleteEmployee(id){
    let params = {
        method: "DELETE",
        headers : {'Content-type':'application/json'},
    }
    if (parseInt(localStorage.getItem('numOfActions'))>0) 
    {
        let resp = await fetch('https://localhost:44375/api/Employees/'+id,params)
        let status = await resp.json()
        await reduceActions()
        alert(status)
    }
    else
    {
        alert('you dont have any more actions left today...\n try again tommorow')
        window.location.href = './html/Login.html'
    }
}

// !


async function addShiftToEmployee(empID,shftID) {
    let emp_shift = {
        ID : 0,
        EmployeeID : empID,
        ShiftID : shftID
    }
    let params = {
        method: "POST",
        body: JSON.stringify(emp_shift),
        headers : {'Content-type':'application/json'},
    }
    if (parseInt(localStorage.getItem('numOfActions'))>0) {
        let resp = await fetch('https://localhost:44375/api/Employee_Shift/'+id,params)
        let status = await resp.json()
        await reduceActions()
        alert(status)
    }
    else
    {
        alert('you dont have any more actions left today...\n try again tommorow')
        window.location.href = './html/Login.html'
    }

}
//#endregion
