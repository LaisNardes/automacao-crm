let itensSemOem = [];
let itensComOem = [];
let itensProcessados = [];
let statusInterval = null;

function carregarItens() {
    const codigo = document.getElementById("codigo").value.trim();
    if (!codigo) {
        alert("Por favor, introduce un código de vehículo");
        return;
    }

    const resultado = document.getElementById("resultado");
    const btnCarregar = document.getElementById("btnCarregar");
    const itensSemOemContainer = document.getElementById("itens-sem-oem-container");
    const itensSemOemList = document.getElementById("itens-sem-oem-list");
    const sucessoDiv = document.getElementById("sucesso");
    const erroDiv = document.getElementById("erro");
    const automacaoContainer = document.getElementById("automacao-container");
    const logContainer = document.getElementById("log-container");

    btnCarregar.disabled = true;
    resultado.innerHTML = '<div class="processing"><span class="loading-spinner"></span> Cargando artículos...</div>';
    sucessoDiv.innerHTML = "<h3>Productos procesados correctamente</h3><p>Aún no se ha realizado ningún procesamiento.</p>";
    erroDiv.innerHTML = "<h3>Productos con error en el procesamiento</h3><p>Aún no se ha realizado ningún procesamiento.</p>";
    automacaoContainer.style.display = "none";
    logContainer.style.display = "none";
    itensSemOemContainer.style.display = "none";

    fetch("/processar", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `codigo=${encodeURIComponent(codigo)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultado.innerHTML = `<div class="error">${data.error}</div>`;
            itensSemOemContainer.style.display = "none";
        } else {
            resultado.innerHTML = `<div class="success">${data.message}</div>`;

            itensSemOem = data.itens_sem_oem || [];
            itensComOem = data.itens_com_oem || [];

            if (itensSemOem.length > 0) {
                let html = "";
                itensSemOem.forEach((item, index) => {
                    html += `<li class="item-sem-oem">
                        <strong>${item.Código}</strong>
                        <input type="text" id="descricao-${index}" value="${item.Descripción}" />
                    </li>`;
                });
                itensSemOemList.innerHTML = html;
                itensSemOemContainer.style.display = "block";
            } else {
                itensSemOemContainer.style.display = "none";
            }

            if (itensComOem.length > 0) {
                let html = `<h3>Artículos con OEM (${itensComOem.length})</h3><ul>`;
                itensComOem.forEach(item => {
                    html += `<li><strong>${item.Código} - ${item.Descripción}</strong><div class="item-details">OEM: ${item.OEM}</div></li>`;
                });
                html += "</ul>";
                sucessoDiv.innerHTML = html;
            } else {
                sucessoDiv.innerHTML = "<h3>Artículos con OEM</h3><p>No se encontraron artículos con OEM.</p>";
            }

            erroDiv.innerHTML = "<h3>Productos con error en el procesamiento</h3><p>Aún no se ha realizado ningún procesamiento.</p>";
        }
    })
    .catch(error => {
        resultado.innerHTML = `<div class="error">Error al cargar artículos: ${error}</div>`;
        itensSemOemContainer.style.display = "none";
    })
    .finally(() => {
        btnCarregar.disabled = false;
    });
}

function processarItensEditados() {
    if (itensSemOem.length === 0 && itensComOem.length === 0) {
        alert("No hay artículos para procesar.");
        return;
    }

    const itensEditados = itensSemOem.map((item, index) => {
        const descricaoEditada = document.getElementById(`descricao-${index}`).value.trim();
        return {...item, Descripción: descricaoEditada};
    });

    const data = {
        itens_editados: itensEditados,
        itens_com_oem: itensComOem
    };

    const resultado = document.getElementById("resultado");
    const btnSalvarProcessar = document.querySelector(".btn-salvar-processar");
    const sucessoDiv = document.getElementById("sucesso");
    const erroDiv = document.getElementById("erro");
    const automacaoContainer = document.getElementById("automacao-container");
    const itensSemOemContainer = document.getElementById("itens-sem-oem-container");

    btnSalvarProcessar.disabled = true;
    resultado.innerHTML = '<div class="processing"><span class="loading-spinner"></span> Procesando artículos...</div>';
    sucessoDiv.innerHTML = "<h3>Productos procesados correctamente</h3><p>Procesando...</p>";
    erroDiv.innerHTML = "<h3>Productos con error en el procesamiento</h3><p>Procesando...</p>";
    automacaoContainer.style.display = "none";

    fetch("/processar_itens_editados", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultado.innerHTML = `<div class="error">${data.error}</div>`;
            sucessoDiv.innerHTML = "<h3>Productos procesados correctamente</h3><p>Error en el procesamiento.</p>";
            erroDiv.innerHTML = "<h3>Productos con error en el procesamiento</h3><p>Error en el procesamiento.</p>";
            automacaoContainer.style.display = "none";
        } else {
            resultado.innerHTML = `<div class="success">${data.message}</div>`;

            itensProcessados = data.sucesso || [];

            if (itensProcessados.length > 0) {
                renderizarItensProcessados(itensProcessados);
                automacaoContainer.style.display = "block";
            } else {
                sucessoDiv.innerHTML = "<h3>Productos procesados correctamente</h3><p>Ningún producto procesado correctamente.</p>";
                automacaoContainer.style.display = "none";
            }

            if (data.erro && data.erro.length > 0) {
                let html = `<h3>Productos con error en el procesamiento (${data.total_erro})</h3><ul>`;
                data.erro.forEach(item => {
                    html += `<li><strong>${item.Código} - ${item.Descripción}</strong><div class="item-details">Motivo: ${item.motivo_erro || 'Desconocido'}</div></li>`;
                });
                html += "</ul>";
                erroDiv.innerHTML = html;
            } else {
                erroDiv.innerHTML = "<h3>Productos con error en el procesamiento</h3><p>Ningún error encontrado.</p>";
            }

            itensSemOemContainer.style.display = "none";
        }
    })
    .catch(error => {
        resultado.innerHTML = `<div class="error">Error en el procesamiento: ${error}</div>`;
        automacaoContainer.style.display = "none";
    })
    .finally(() => {
        btnSalvarProcessar.disabled = false;
    });
}

function renderizarItensProcessados(itens) {
    const sucessoDiv = document.getElementById("sucesso");  
    
    
    let html = `<h3>Productos procesados correctamente (${itens.length})</h3><ul>`;
    itens.forEach((item, index) => {       
        
        html += `<li data-index="${index}">
            <strong>${item.Código} - ${item.Descripción}</strong>
            <div class="item-details">
                Precio: <input type="text" class="input-preco" value="${item.preco_scraping || ''}" onchange="atualizarPreco(${index}, this.value)" />
                <button class="btn-excluir" onclick="removerItem(${index})" title="Excluir artículo">x</button>
                ${item.link_scraping ? `<a href="${item.link_scraping}" target="_blank" class="btn-link">Enlace</a>` : 'Sin enlace'}
            </div>
        </li>`;
    });
    html += "</ul>";
        
    sucessoDiv.innerHTML = html;
}

function enviarAtualizacaoJson() {
    fetch('/atualizar-json', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ itens: itensProcessados })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            alert('Error al actualizar JSON: ' + (data.error || 'Desconocido'));
        }
    })
    .catch(err => {
        alert('Error en la comunicación con el servidor: ' + err);
    });
}

function atualizarPreco(index, novoPreco) {
    if (itensProcessados[index]) {
        itensProcessados[index].preco_scraping = novoPreco;
        enviarAtualizacaoJson();
    }
}

function removerItem(index) {
    if (index >= 0 && index < itensProcessados.length) {
        itensProcessados.splice(index, 1);
        renderizarItensProcessados(itensProcessados);
        enviarAtualizacaoJson();
    }
}

function iniciarAutomacao() {
    if (itensProcessados.length === 0) {
        alert("No hay artículos para automatización.");
        return;
    }

    if (!confirm("Asegúrate de que el CRM está abierto y listo para recibir los clics. ¿Continuar?")) {
        return;
    }

    const btnAutomacao = document.getElementById("btnAutomacao");
    const logContainer = document.getElementById("log-container");
    const logAutomacao = document.getElementById("log-automacao");
    const logStatus = document.getElementById("log-status");

    btnAutomacao.disabled = true;
    btnAutomacao.textContent = "Iniciando automatización...";

    logAutomacao.textContent = "Iniciando automatización...";
    logContainer.style.display = "block";
    logAutomacao.style.display = "block";
    logStatus.textContent = "En curso";
    logStatus.classList.remove("concluido");

    fetch("/iniciar-automacao", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`Error: ${data.error}`);
                logAutomacao.textContent = `Error: ${data.error}`;
                btnAutomacao.disabled = false;
                btnAutomacao.textContent = "Iniciar Automatización de Clics";
            } else {
                iniciarVerificacaoStatus();
            }
        })
        .catch(error => {
            alert(`Error al iniciar automatización: ${error}`);
            logAutomacao.textContent = `Error al iniciar automatización: ${error}`;
            btnAutomacao.disabled = false;
            btnAutomacao.textContent = "Iniciar Automatización de Clics";
        });
}

function iniciarVerificacaoStatus() {
    if (statusInterval) clearInterval(statusInterval);
    statusInterval = setInterval(verificarStatusAutomacao, 2000);
}

function verificarStatusAutomacao() {
    const logAutomacao = document.getElementById("log-automacao");
    const logStatus = document.getElementById("log-status");
    const btnAutomacao = document.getElementById("btnAutomacao");

    fetch("/status-automacao")
        .then(response => response.json())
        .then(data => {
            if (data.log && data.log.length > 0) {
                logAutomacao.textContent = data.log.join("\n");
                logAutomacao.scrollTop = logAutomacao.scrollHeight;
            }

            if (data.concluida) {
                clearInterval(statusInterval);
                statusInterval = null;
                logStatus.textContent = "Concluida";
                logStatus.classList.add("concluido");
                btnAutomacao.disabled = false;
                btnAutomacao.textContent = "Iniciar Automatización de Clics";
                alert("Automatización concluida correctamente!");
            } else if (!data.em_andamento && !data.concluida) {
                clearInterval(statusInterval);
                statusInterval = null;
                logStatus.textContent = "Interrumpida";
                btnAutomacao.disabled = false;
                btnAutomacao.textContent = "Iniciar Automatización de Clics";
                alert("Automatización interrumpida. Verifica el registro para más detalles.");
            }
        })
        .catch(error => {
            console.error("Error al verificar estado:", error);
        });
}