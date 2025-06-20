document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // evita o envio normal do formulário

    const form = event.target;
    const formData = new FormData(form);

    try {
        const response = await fetch(form.action, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            mostrarErro(errorText);
        } else {
            // Redireciona em caso de sucesso
            window.location.href = response.url;
        }

    } catch (error) {
        mostrarErro("Erro inesperado. Tente novamente.");
    }
});

function mostrarErro(msg) {
    const box = document.getElementById("login-error-message");
    box.textContent = msg;
    box.style.display = "block";
}