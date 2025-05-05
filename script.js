// logica principal
// Variáveis globais
let video, canvas, context;
let registerVideo, registerCanvas, registerContext;

// Quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar câmera na tela de login
    if (document.getElementById('video')) {
        video = document.getElementById('video');
        canvas = document.getElementById('canvas');
        context = canvas.getContext('2d');
        
        // Iniciar a câmera
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(stream) {
                    video.srcObject = stream;
                    video.play();
                });
        }
        
        // Configurar botão de captura
        document.getElementById('captureBtn').addEventListener('click', function() {
            context.drawImage(video, 0, 0, 320, 240);
            // Aqui você adicionaria a lógica de reconhecimento facial
            alert('Rosto capturado! Implemente o reconhecimento facial aqui.');
        });
    }
    
    // Inicializar câmera na tela de cadastro
    if (document.getElementById('registerVideo')) {
        registerVideo = document.getElementById('registerVideo');
        registerCanvas = document.getElementById('registerCanvas');
        registerContext = registerCanvas.getContext('2d');
        
        // Iniciar a câmera
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then(function(stream) {
                    registerVideo.srcObject = stream;
                    registerVideo.play();
                });
        }
        
        // Configurar botão de captura
        document.getElementById('registerCaptureBtn').addEventListener('click', function() {
            registerContext.drawImage(registerVideo, 0, 0, 320, 240);
            alert('Rosto capturado para cadastro!');
        });
    }
    
    // Navegação entre páginas
    if (document.getElementById('loginBtn')) {
        document.getElementById('loginBtn').addEventListener('click', function() {
            // Validação simples de login
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            if (username && password) {
                // Redirecionar para a página de reconhecimento
                window.location.href = 'pages/reconhecimento.html';
            } else {
                alert('Por favor, preencha todos os campos.');
            }
        });
    }
    
    if (document.getElementById('registerBtn')) {
        document.getElementById('registerBtn').addEventListener('click', function() {
            // Validação simples de cadastro
            const fullName = document.getElementById('fullName').value;
            const email = document.getElementById('email').value;
            const newUsername = document.getElementById('newUsername').value;
            const newPassword = document.getElementById('newPassword').value;
            
            if (fullName && email && newUsername && newPassword) {
                alert('Cadastro realizado com sucesso!');
                window.location.href = '../index.html';
            } else {
                alert('Por favor, preencha todos os campos.');
            }
        });
    }
    
    if (document.getElementById('backBtn')) {
        document.getElementById('backBtn').addEventListener('click', function() {
            window.location.href = '../index.html';
        });
    }
});