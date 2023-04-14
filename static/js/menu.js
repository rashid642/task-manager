document.getElementById("ham").addEventListener("click",drop)

function drop()
{
    let x = document.getElementsByClassName("navListMobile")[0]
    if (x.style.display == 'flex'){
        x.style.display = 'none'
    }
    else{
        x.style.display = 'flex'
    }
}