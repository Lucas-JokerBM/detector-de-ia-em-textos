(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const KEY = "detector.apiKey";
  let current = null, currentName = "documento.docx";

  // Chave de sessão entregue pelo app desktop local (#key=...). Removida da URL após leitura.
  const m = location.hash.match(/key=([^&]+)/);
  if (m) {
    sessionStorage.setItem(KEY, decodeURIComponent(m[1]));
    history.replaceState(null, "", location.pathname + location.search);
  }
  $("apikey").value = sessionStorage.getItem(KEY) || "";
  $("apikey").addEventListener("change", (e) => sessionStorage.setItem(KEY, e.target.value));

  const el = (tag, props = {}, ...kids) => {
    const n = Object.assign(document.createElement(tag), props); // sempre textContent: sem XSS
    kids.forEach((k) => n.append(k));
    return n;
  };

  async function analyze(file) {
    $("status").textContent = "Analisando…";
    const body = new FormData();
    body.append("file", file);
    const headers = {};
    const key = $("apikey").value.trim();
    if (key) headers["X-API-Key"] = key;
    try {
      const res = await fetch("/api/v1/analyze", { method: "POST", body, headers });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Erro ${res.status}`);
      }
      current = await res.json();
      currentName = file.name;
      $("status").textContent = file.name;
      render(current);
    } catch (e) {
      $("status").textContent = "Falha: " + e.message;
    }
  }

  function render(r) {
    $("result").hidden = false;
    $("score").textContent = `${Math.round(r.score)}/100`;
    $("verdict").textContent = r.verdict;
    $("marker").style.left = `${Math.min(100, Math.max(0, r.score))}%`;
    $("warnings").replaceChildren(...r.warnings.map((w) => el("li", { textContent: w })));

    $("metrics").tBodies[0].replaceChildren(...r.metrics.map((mt) => {
      const bar = el("span", { className: "bar" });
      bar.style.width = `${Math.round(mt.score * 60)}px`;
      const tr = el("tr", {}, el("td", { textContent: mt.name }), el("td", { textContent: mt.value }),
        el("td", {}, bar, ` ${Math.round(mt.score * 100)}%`));
      tr.addEventListener("click", () => showMetric(mt));
      return tr;
    }));

    $("doc").replaceChildren(...r.paragraphs.map((p) => {
      const para = el("p", { className: p.heading ? "head" : "" });
      p.segments.forEach((s) => {
        if (s.flag === null) { para.append(s.text); return; }
        const f = r.flags[s.flag];
        const span = el("span", { textContent: s.text, className: `hl s${f.severity > 1 ? 2 : 1}` });
        span.dataset.flag = s.flag;
        span.addEventListener("click", () => showFlag(s.flag));
        para.append(span);
      });
      return para;
    }));

    $("advice").replaceChildren(...(r.global_advice.length ? r.global_advice
      : ["Nenhuma sugestão geral relevante."]).map((a) => el("li", { textContent: a })));
    $("flags").replaceChildren(...r.flags.map((f) => {
      const li = el("li", { textContent: f.text.length > 80 ? f.text.slice(0, 77) + "…" : f.text });
      li.addEventListener("click", () => showFlag(f.id, true));
      return li;
    }));
    $("detail").textContent = `${r.flags.length} trecho(s) sinalizado(s).`;
  }

  function showFlag(id, scroll = false) {
    const f = current.flags[id];
    document.querySelectorAll(".hl.sel").forEach((n) => n.classList.remove("sel"));
    const span = document.querySelector(`.hl[data-flag="${id}"]`);
    if (span) { span.classList.add("sel"); if (scroll) span.scrollIntoView({ block: "center", behavior: "smooth" }); }
    $("detail").textContent = `“${f.text}”\n\nMOTIVOS\n${f.reasons.map((x) => "• " + x).join("\n")}\n\n` +
      `O QUE ALTERAR\n${f.suggestions.map((x) => "→ " + x).join("\n")}`;
  }

  const showMetric = (mt) => {
    $("detail").textContent = `${mt.name}\nValor: ${mt.value}\nSinal de I.A.: ${Math.round(mt.score * 100)}%\n\n` +
      `${mt.explanation}\n\nO QUE FAZER\n${mt.advice || "—"}`;
  };

  function download(name, text, type) {
    const a = el("a", { href: URL.createObjectURL(new Blob([text], { type })), download: name });
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function textReport(r) {
    const L = [`RELATÓRIO — ${currentName}`, `Pontuação: ${Math.round(r.score)}/100 — ${r.verdict}`, "", "INDICADORES"];
    r.metrics.forEach((m) => L.push(`* ${m.name}: ${m.value} (sinal ${Math.round(m.score * 100)}%)`));
    L.push("", "SUGESTÕES GERAIS", ...r.global_advice.map((a) => "- " + a), "", "TRECHOS SINALIZADOS");
    r.flags.forEach((f) => L.push(`${f.id + 1}. “${f.text}”`, ...f.reasons.map((x) => "   Motivo: " + x),
      ...f.suggestions.map((x) => "   Sugestão: " + x)));
    L.push("", "Aviso: análise heurística; não constitui prova de autoria.");
    return L.join("\n");
  }

  $("dl-txt").addEventListener("click", () => current && download("relatorio_ia.txt", textReport(current), "text/plain"));
  $("dl-json").addEventListener("click", () => current && download("relatorio_ia.json", JSON.stringify(current, null, 2), "application/json"));

  const input = $("file"), drop = $("drop");
  drop.addEventListener("click", (e) => { e.preventDefault(); input.click(); });
  input.addEventListener("change", () => input.files[0] && analyze(input.files[0]));
  ["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
  ["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
  drop.addEventListener("drop", (e) => e.dataTransfer.files[0] && analyze(e.dataTransfer.files[0]));
})();
