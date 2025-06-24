fetch('/static/components/menu.html')
    .then(response => response.text())
    .then(html => {
        document.getElementById('menu-container').innerHTML = html;

        atualizarStatusMenu();
    });

let reconhecimentoAtivo = JSON.parse(localStorage.getItem("reconhecimentoAtivo")) || false;

// Alternar estado
function toggleReconhecimento() {
    reconhecimentoAtivo = !reconhecimentoAtivo;
    localStorage.setItem("reconhecimentoAtivo", JSON.stringify(reconhecimentoAtivo));

    if (reconhecimentoAtivo) {
        socket.emit('enable_recognition');
    } else {
        socket.emit('disable_recognition');
    }

    atualizarBotao();
    atualizarStatusMenu();
}

// Atualiza visual do botão
function atualizarBotao() {
    const botao = document.getElementById('reconhecimentoBtn');
    botao.classList.toggle('ativado', reconhecimentoAtivo);
    botao.classList.toggle('desativado', !reconhecimentoAtivo);
    botao.innerHTML = `<i class="fas ${reconhecimentoAtivo ? 'fa-toggle-on' : 'fa-toggle-off'}"></i> Reconhecimento facial: ${reconhecimentoAtivo ? 'Ativado' : 'Desativado'}`;
}

function atualizarStatusMenu() {
    const statusLi = document.getElementById("status-reconhecimento");
    if (statusLi) {
        console.log("Atualizando status do menu:", reconhecimentoAtivo);
        statusLi.innerHTML = `<i class="fas fa-camera"'}"></i> ${reconhecimentoAtivo ? 'Ativado' : 'Desativado'}`;
        statusLi.style.color = reconhecimentoAtivo ? "#28a745" : "#dc3545";
    }
}

function toggleMenu() {
    const menu = document.getElementById('menu-superior');
    menu.classList.toggle('active');
}

document.addEventListener("DOMContentLoaded", () => {
    atualizarBotao();
});