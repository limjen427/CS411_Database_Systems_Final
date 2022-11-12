var wineholder = {};

async function LoadWineList() {
    return WineList('http://127.0.0.1:5000/wine/all');
}

async function RegisterNewReview(){
    return ReviewMaker('http://127.0.0.1:5000/review/create%27');
}


async function WineList(url = '') {
    const urlString = url;
    fetch(urlString, {
        method: "GET",
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers':  "Content-Type",
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, DELETE, PUT',
            'Authorization': 'Bearer key'
        }
    })
    .then(objData => objData.text())
    .then(json => {
        wineAll = document.getElementById("wineAll");

        array = [];
        c = 0;
        json.split(/([()])/).filter(Boolean).forEach(e =>
            // Increase / decrease counter and push desired values to an array
            e == '(' ? c++ : e == ')' ? c-- : c > 0 ? array.push(e) : {}
        );

        for (const tuple of array) {
            split = tuple.split(',');
            if (split.length == 2) {
                var [wineID, name] = split
                if (!(wineID in wineholder)) {
                    name = name.slice(2, -1)

                    wineAll.options[wineAll.options.length] = new Option(name, wineID);

                    wineholder[wineID] = name;
                }
            }
        }

        return json;
    })
}
async function ReviewMaker(url = '') {

    var wineID = document.getElementById("wineAll").value 
    var score = document.getElementById("rating").value 
    var review = document.getElementById("review_box").value 
    var userID = 1676

    const urlString = url + "?" + "wineID=" + wineID + "&score=" + score + "&review=" + review + "&userID=" + userID;
    fetch(urlString, {
        method: "POST",
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
        return json;
    })
}