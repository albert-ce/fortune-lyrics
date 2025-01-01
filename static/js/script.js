async function connect_spotify() {
    window.location.href = "/auth/login";
}

async function logout() {
    window.location.href = "/auth/logout";
}

async function first_fortune(){
    document.getElementById('loading').innerHTML = "Loading...";
    await fetch('/fortune/generate_new');
    var response = await fetch('/fortune/get_fortune');
    var responseTxt = await response.text()
    document.getElementById('content').innerHTML = responseTxt;
}

async function click_cookie() {
    fetch('/fortune/generate_new');
    document.getElementById('cookie').style.animation = "none";
    document.getElementById('tap').style.display = 'none';
    document.getElementById('right').style.animation = "breakRight 0.01s 0.01s linear forwards";
    document.getElementById('left').style.animation = "breakLeft 0.01s 0.01s linear forwards";
    await new Promise(resolve => setTimeout(resolve, 1000));
    document.getElementById('right').style.animation = "disappearRight 1s linear forwards";
    document.getElementById('left').style.animation = "disappearLeft 1s linear forwards";
    document.getElementById('fortune-message').style.animation = "appearMessage 1s linear forwards";
    document.getElementById('fortune-message').style.display = 'block';
    await new Promise(resolve => setTimeout(resolve, 1100));
    document.getElementById('cookie').style.display = 'none';
    await new Promise(resolve => setTimeout(resolve, 2000));
    document.getElementById('new').style.animation = "appearRefresh 0.2s linear forwards";
    document.getElementById('new').style.display = 'block';
}

async function new_fortune(){
    var response = await fetch('/fortune/get_fortune');
    var responseTxt = await response.text()
    document.getElementById('content').innerHTML = responseTxt;
}