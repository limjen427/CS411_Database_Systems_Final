async function onClickSearch(){
    return findWine('[http://127.0.0.1:5000/wine/all](http://127.0.0.1:5000/wine/all)');
}
    
    async function findWine(url = '', params = {}, bodyObj = {}) {
    var name = document.getElementById("Wine").value;
    const urlString = url + "?" + "name=" + name;
    fetch(urlString, {
    method: "GET",
    headers: {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS,DELETE,PUT',
    'Authorization': 'Bearer key'
    }
    })
    .then(objData => objData.text())
    .then(json => {
        document.getElementById("output").innerHTML = "";
    
        let table = document.createElement('table');
        let thead = document.createElement('thead');
        let tbody = document.createElement('tbody');
    
        table.appendChild(thead);
        table.appendChild(tbody);
    
        document.getElementById('output').appendChild(table);
    
        let row_1 = document.createElement('tr');
        let heading_1 = document.createElement('th');
        heading_1.innerHTML = "Wine Name";
    
        row_1.appendChild(heading_1);
    
        thead.appendChild(row_1);
    
        array = [];
        c = 0;
        json.split(/([()])/).filter(Boolean).forEach(e =>
            e == '(' ? c++ : e == ')' ? c-- : c > 0 ? array.push(e) : {}
        );
    
        for (const tuple of array) {
            split = tuple.split(',');
            if (split.length == 2) {
                var [name] = split
    
                let trow = document.createElement('tr');

                let tcol1 = document.createElement('td'); //col 1
                tcol1.innerHTML = name.replace("'", "").replace("'", "")
    
                trow.appendChild(tcol1); //append col1
    
                tbody.appendChild(trow); //append whole row
    
            }
        }
    
    })
}