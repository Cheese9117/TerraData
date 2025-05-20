function togglePanel(button) {
  const panelId = button.dataset.panel;
  const panel = document.getElementById(panelId);
  const isOpen = panel.classList.contains("open");

  document.querySelectorAll(".panel.open").forEach((p) => {
    if (p !== panel) {
      p.style.maxHeight = null;
      p.classList.remove("open");
    }
  });

  if (!isOpen) {
    panel.classList.add("open");
    panel.style.maxHeight = panel.scrollHeight + "px";
  } else {
    panel.style.maxHeight = null;
    panel.classList.remove("open");
  }
}

document.querySelectorAll(".sensor-btn").forEach((btn) => {
  btn.addEventListener("click", () => togglePanel(btn));
});

const websocket = new WebSocket('ws://dress.ip:8765');

websocket.onopen = () => {
  console.log('Conectado al servidor WebSocket');
  websocket.send(JSON.stringify({ "request": "latest_data" }));
};

websocket.onmessage = (event) => {
  console.log('Datos recibidos:', event.data);
  try {
    const data = JSON.parse(event.data);
    
    if (data.humedad !== undefined) {
      const humedad = parseFloat(data.humedad);
      document.getElementById('humedad-value').textContent = humedad.toFixed(1);
      
      const waterElement = document.getElementById('water');
      if (waterElement) {
        waterElement.style.height = `${humedad}%`;
      }
    }
    
    if (data.valor_analogico !== undefined) {
      document.getElementById('valor-analogico-value').textContent = data.valor_analogico;
    }
    
    if (data.temperatura !== undefined) {
      const temperatura = parseFloat(data.temperatura);
      document.getElementById('temp-value').textContent = temperatura.toFixed(1);
      
      const thermometerFluid = document.getElementById('thermometer-fluid');
      const tempHeight = ((temperatura - 20) / 10) * 100;
      thermometerFluid.style.height = `${tempHeight}%`;
    }
  } catch (error) {
    console.error('Error al parsear JSON:', error);
  }
};

websocket.onclose = () => {
  console.log('Desconectado del servidor WebSocket');
};

websocket.onerror = (error) => {
  console.error('Error del WebSocket:', error);
};
