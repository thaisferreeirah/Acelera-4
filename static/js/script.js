fetch('/static/components/menu.html') // ajuste o caminho se estiver em outra pasta
    .then(response => response.text())
    .then(html => {
        document.getElementById('menu-container').innerHTML = html;
    });