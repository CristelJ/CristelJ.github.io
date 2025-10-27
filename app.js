// Inicializar Firebase
const firebaseConfig = {
  apiKey: "AIzaSyBn7_bv7pZ-5cve8eZ4xOsk4B0VsUlpLzI",
  authDomain: "ambiental-f92b9.firebaseapp.com",
  projectId: "ambiental-f92b9",
  storageBucket: "ambiental-f92b9.firebasestorage.app",
  messagingSenderId: "516743723611",
  appId: "1:516743723611:web:27edeae06f3084eef69d7e",
  measurementId: "G-BER0G04HSD"
};
firebase.initializeApp(firebaseConfig);
const db = firebase.firestore();

// Referencias
const videoFondo = document.getElementById("video-fondo");
const fechaInicioInput = document.getElementById("fechaInicio");
const fechaFinInput = document.getElementById("fechaFin");
const variableSelect = document.getElementById("variable");
const botonConsultar = document.getElementById("consultar");
const botonModo = document.getElementById("modo");
const resumen = document.getElementById("resumen");
const toggleGrafico = document.getElementById("toggleGrafico");
const botonDescargar = document.getElementById("descargarPDF");
const graficoArea = document.getElementById("grafico-area");

const ctx1 = document.getElementById("grafico1").getContext("2d");
const ctx2 = document.getElementById("grafico2").getContext("2d");
const ctx3 = document.getElementById("grafico3").getContext("2d");
const wrapper2 = document.getElementById("grafico-wrapper-2");
const wrapper3 = document.getElementById("grafico-wrapper-3");

let charts = [];

// Modo oscuro
if (localStorage.getItem("modoOscuro") === "true") {
  document.body.classList.add("dark-mode");
  botonModo.textContent = "☀️ Modo Claro";
  videoFondo.src = "videos/noche.mp4";
} else {
  videoFondo.src = "videos/dia.mp4";
}

botonModo.addEventListener("click", () => {
  document.body.classList.toggle("dark-mode");
  const oscuro = document.body.classList.contains("dark-mode");
  localStorage.setItem("modoOscuro", oscuro);
  botonModo.textContent = oscuro ? "☀️ Modo Claro" : "🌙 Modo Oscuro";
  videoFondo.src = oscuro ? "videos/noche.mp4" : "videos/dia.mp4";
  charts.forEach(c => {
    const color = oscuro ? "#fff" : "#000";
    c.options.scales.x.ticks.color = color;
    c.options.scales.y.ticks.color = color;
    c.options.plugins.legend.labels.color = color;
    c.update();
  });
});

// Mostrar/Ocultar gráficos
toggleGrafico.addEventListener("change", () => {
  const visible = toggleGrafico.checked;
  document.querySelectorAll(".grafico-wrapper").forEach(div => {
    div.style.display = visible ? "block" : "none";
  });
  if (visible) setTimeout(() => charts.forEach(c => c.resize()), 100);
});

// Crear gráfico
function crearGrafico(ctx, label, datos, colorLinea, etiquetas, colorTexto) {
  const minVal = Math.min(...datos);
  const maxVal = Math.max(...datos);

  return new Chart(ctx, {
    type: "line",
    data: { labels: etiquetas, datasets: [{label, data: datos, borderColor: colorLinea, backgroundColor: colorLinea+"33", fill:true, tension:0.35}] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend:{labels:{color:colorTexto}}, zoom:{pan:{enabled:true, mode:"x"}} },
      scales: {
        x: { ticks:{color:colorTexto, autoSkip:true, maxTicksLimit:12} },
        y: { min:minVal, max:maxVal, ticks:{color:colorTexto} }
      }
    }
  });
}

function minMaxPromedio(valores){
  const min=Math.min(...valores).toFixed(2);
  const max=Math.max(...valores).toFixed(2);
  const promedio=(valores.reduce((a,b)=>a+b,0)/valores.length).toFixed(2);
  return {min,max,promedio};
}

// Consultar datos
botonConsultar.addEventListener("click", async () => {
  const inicio = fechaInicioInput.value;
  const fin = fechaFinInput.value;
  const variable = variableSelect.value;

  if(!inicio||!fin) return alert("⚠️ Selecciona rango de fechas");
  if(!variable) return alert("⚠️ Selecciona una variable");

  charts.forEach(c=>c.destroy());
  charts=[];
  resumen.textContent="";
  graficoArea.style.display="none";

  const snapshot = await db.collection("datos").where("fecha",">=",inicio).where("fecha","<=",fin).get();
  if(snapshot.empty) return resumen.textContent="❌ No hay datos.";

  const registros = [];
  snapshot.forEach(d=>{const data=d.data(); registros.push({fecha:data.fecha, hora:data.hora, temperatura:data.temperatura, humedad:data.humedad, viento_kmh:data.viento_kmh})});
  registros.sort((a,b)=>(`${a.fecha} ${a.hora}`).localeCompare(`${b.fecha} ${b.hora}`));
  const etiquetas = registros.map(r=>`${r.fecha} ${r.hora}`);
  const oscuro = document.body.classList.contains("dark-mode");
  const colorTexto = oscuro?"#fff":"#000";

  graficoArea.style.display="block";

  if(variable==="todas"){
    wrapper2.style.display="block"; wrapper3.style.display="block";
    const temp=registros.map(r=>r.temperatura);
    const hum=registros.map(r=>r.humedad);
    const viento=registros.map(r=>r.viento_kmh);
    charts.push(
      crearGrafico(ctx1,"🌡️ Temperatura (°C)",temp,"#ff5555",etiquetas,colorTexto),
      crearGrafico(ctx2,"💧 Humedad (%)",hum,"#44ff44",etiquetas,colorTexto),
      crearGrafico(ctx3,"🌬️ Viento (km/h)",viento,"#448aff",etiquetas,colorTexto)
    );
    const tempS=minMaxPromedio(temp), humS=minMaxPromedio(hum), vientoS=minMaxPromedio(viento);
    resumen.innerHTML=`<b>🌡️ Temp</b> Prom:${tempS.promedio} Min:${tempS.min} Max:${tempS.max}<br>
                       <b>💧 Humedad</b> Prom:${humS.promedio} Min:${humS.min} Max:${humS.max}<br>
                       <b>🌬️ Viento</b> Prom:${vientoS.promedio} Min:${vientoS.min} Max:${vientoS.max}`;
  } else {
    wrapper2.style.display="none"; wrapper3.style.display="none";
    const valores=registros.map(r=>r[variable]);
    const color = variable==="temperatura"?"#ff5555":variable==="humedad"?"#44ff44":"#448aff";
    charts.push(crearGrafico(ctx1,variable.toUpperCase(),valores,color,etiquetas,colorTexto));
    const s=minMaxPromedio(valores);
    resumen.innerHTML=`<b>${variable.toUpperCase()}</b><br>Prom:${s.promedio}<br>Min:${s.min}<br>Max:${s.max}`;
  }
});

// Descargar PDF
botonDescargar.addEventListener("click", async ()=>{
  const pdf=new jspdf.jsPDF('p','mm','a4');
  let yOffset=10;
  for(let c of charts){
    const img=c.canvas.toDataURL("image/png");
    const props=pdf.getImageProperties(img);
    const width=180;
    const height=(props.height*width)/props.width;
    pdf.addImage(img,'PNG',15,yOffset,width,height);
    yOffset+=height+10;
    if(yOffset>270){ pdf.addPage(); yOffset=10; }
  }
  pdf.save("graficos.pdf");
});
