const base = "http://127.0.0.1:5055";

async function updateStatus() {
  let r = await fetch(`${base}/status`);
  document.getElementById("status").textContent = await r.text();
}

async function updateMemory() {
  let r = await fetch(`${base}/memory`);
  document.getElementById("memory").textContent = await r.text();
}

async function sendReflect() {
  let txt = document.getElementById("reflectText").value;
  let r = await fetch(`${base}/reflect`, {
    method: "POST",
    headers:{ "Content-Type":"application/json" },
    body: JSON.stringify({ q: txt })
  });
  document.getElementById("reflectOut").textContent = await r.text();
}

setInterval(updateStatus, 2000);
setInterval(updateMemory, 3000);
updateStatus();
updateMemory();

