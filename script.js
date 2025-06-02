// logica principal
// Variáveis globais
// Login functionality
document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Simulação de login - em um sistema real, isso seria uma chamada AJAX para o servidor
    if(username === 'admin' && password === 'admin123') {
        // Armazenar token de autenticação (simulado)
        localStorage.setItem('authToken', 'simulated-token');
        
        // Redirecionar para o dashboard
        window.location.href = 'dashboard.html';
    } else {
        alert('Usuário ou senha incorretos!');
    }
});

// Verificar autenticação em páginas protegidas
function checkAuth() {
    if(window.location.pathname !== '/index.html' && window.location.pathname !== '/') {
        const token = localStorage.getItem('authToken');
        if(!token) {
            window.location.href = 'index.html';
        }
    }
}

// Chamar a verificação quando a página carregar
window.addEventListener('DOMContentLoaded', checkAuth);

// Logout functionality
function logout() {
    localStorage.removeItem('authToken');
    window.location.href = 'index.html';
}

// Funções para o reconhecimento facial (usando a biblioteca face-api.js)
async function setupFaceRecognition() {
    if(!document.getElementById('video')) return;
    
    try {
        // Carregar modelos
        await faceapi.nets.tinyFaceDetector.loadFromUri('/models');
        await faceapi.nets.faceLandmark68Net.loadFromUri('/models');
        await faceapi.nets.faceRecognitionNet.loadFromUri('/models');
        
        // Acessar a webcam
        const video = document.getElementById('video');
        navigator.mediaDevices.getUserMedia({ video: {} })
            .then(stream => {
                video.srcObject = stream;
            })
            .catch(err => {
                console.error('Erro ao acessar a webcam:', err);
                alert('Não foi possível acessar a webcam. Por favor, verifique as permissões.');
            });
        
        // Detectar rostos
        video.addEventListener('play', () => {
            const canvas = faceapi.createCanvasFromMedia(video);
            document.querySelector('.canvas-container').append(canvas);
            faceapi.matchDimensions(canvas, { width: video.width, height: video.height });
            
            setInterval(async () => {
                const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
                    .withFaceLandmarks()
                    .withFaceDescriptors();
                
                canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
                faceapi.draw.drawDetections(canvas, detections);
                faceapi.draw.drawFaceLandmarks(canvas, detections);
                
                // Aqui você pode adicionar lógica para comparar com rostos conhecidos
            }, 100);
        });
    } catch (error) {
        console.error('Erro ao carregar modelos de reconhecimento facial:', error);
        alert('Erro ao inicializar o reconhecimento facial. Por favor, recarregue a página.');
    }
}

// Inicializar reconhecimento facial quando a página carregar
window.addEventListener('DOMContentLoaded', setupFaceRecognition);

// Funções para o cadastro de alunos
function saveStudent(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const student = Object.fromEntries(formData.entries());
    
    // Simular salvamento (em um sistema real, seria uma chamada AJAX)
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    students.push(student);
    localStorage.setItem('students', JSON.stringify(students));
    
    alert('Aluno cadastrado com sucesso!');
    form.reset();
    
    // Atualizar a tabela se estiver na página de alunos
    if(window.location.pathname.includes('alunos.html')) {
        loadStudentsTable();
    }
}

function loadStudentsTable() {
    const tableBody = document.querySelector('#studentsTable tbody');
    if(!tableBody) return;
    
    const students = JSON.parse(localStorage.getItem('students') || '[]');
    
    tableBody.innerHTML = '';
    students.forEach((student, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${student.name}</td>
            <td>${student.registration}</td>
            <td>${student.class}</td>
            <td>
                <button class="btn btn-secondary" onclick="editStudent(${index})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-primary" onclick="deleteStudent(${index})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

function editStudent(index) {
    const students = JSON.parse(localStorage.getItem('students') || '[]');
    const student = students[index];
    
    // Preencher formulário de edição (você precisará criar este formulário)
    document.getElementById('editName').value = student.name;
    document.getElementById('editRegistration').value = student.registration;
    document.getElementById('editClass').value = student.class;
    document.getElementById('editIndex').value = index;
    
    // Mostrar modal de edição (você precisará criar este modal)
    $('#editStudentModal').modal('show');
}

function updateStudent(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const index = formData.get('editIndex');
    const updatedStudent = Object.fromEntries(formData.entries());
    delete updatedStudent.editIndex;
    
    let students = JSON.parse(localStorage.getItem('students') || '[]');
    students[index] = updatedStudent;
    localStorage.setItem('students', JSON.stringify(students));
    
    alert('Aluno atualizado com sucesso!');
    loadStudentsTable();
    $('#editStudentModal').modal('hide');
}

function deleteStudent(index) {
    if(confirm('Tem certeza que deseja excluir este aluno?')) {
        let students = JSON.parse(localStorage.getItem('students') || '[]');
        students.splice(index, 1);
        localStorage.setItem('students', JSON.stringify(students));
        loadStudentsTable();
        alert('Aluno excluído com sucesso!');
    }
}

// Carregar tabela de alunos quando a página carregar
window.addEventListener('DOMContentLoaded', loadStudentsTable);

// Funções para o histórico de acessos
function loadAccessHistory() {
    const tableBody = document.querySelector('#accessHistoryTable tbody');
    if(!tableBody) return;
    
    // Simular dados (em um sistema real, seria uma chamada AJAX)
    const accessHistory = JSON.parse(localStorage.getItem('accessHistory') || '[]');
    
    tableBody.innerHTML = '';
    accessHistory.forEach((access, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(access.timestamp).toLocaleString()}</td>
            <td>${access.studentName}</td>
            <td>${access.studentRegistration}</td>
            <td>${access.accessType}</td>
            <td>${access.method}</td>
        `;
        tableBody.appendChild(row);
    });
}

// Carregar histórico quando a página carregar
window.addEventListener('DOMContentLoaded', loadAccessHistory);

// Simular registro de acesso (para demonstração)
function simulateAccess() {
    const students = JSON.parse(localStorage.getItem('students') || '[]');
    if(students.length === 0) {
        alert('Nenhum aluno cadastrado para simular acesso.');
        return;
    }
    
    const randomStudent = students[Math.floor(Math.random() * students.length)];
    const accessTypes = ['Entrada', 'Saída'];
    const methods = ['Reconhecimento Facial', 'Cartão RFID', 'Manual'];
    
    const access = {
        timestamp: new Date().toISOString(),
        studentName: randomStudent.name,
        studentRegistration: randomStudent.registration,
        accessType: accessTypes[Math.floor(Math.random() * accessTypes.length)],
        method: methods[Math.floor(Math.random() * methods.length)]
    };
    
    let accessHistory = JSON.parse(localStorage.getItem('accessHistory') || '[]');
    accessHistory.unshift(access);
    localStorage.setItem('accessHistory', JSON.stringify(accessHistory));
    
    alert(`Acesso registrado para ${randomStudent.name} (${access.accessType} via ${access.method})`);
    loadAccessHistory();
}
//script do cadasto..
  document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Adiciona classe de animação
    this.classList.add('form-submitted');
    
    // Simula envio (substitua pelo seu código real)
    setTimeout(() => {
      // Remove a classe após a animação
      this.classList.remove('form-submitted');
      
      // Aqui você pode adicionar o redirecionamento ou feedback
      alert('Cadastro realizado com sucesso!');
      this.reset();
    }, 1500);
  });

  // Efeito de máquina de escrever no título
  const title = document.querySelector('.card-header h2');
  if (title) {
    const text = title.innerText;
    title.innerText = '';
    
    let i = 0;
    const typingEffect = setInterval(() => {
      if (i < text.length) {
        title.innerText += text.charAt(i);
        i++;
      } else {
        clearInterval(typingEffect);
      }
    }, 100);
  }


