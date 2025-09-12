async function loadMetrics(){
  const res = await fetch('metrics.json');
  const data = await res.json();
  const labels = Object.keys(data.latest.dmaic);
  const baseline = labels.map(k => data.baseline.dmaic[k]);
  const latest = labels.map(k => data.latest.dmaic[k]);
  Plotly.newPlot('radar', [
    {type:'scatterpolar', r:baseline, theta:labels, fill:'toself', name:'Baseline'},
    {type:'scatterpolar', r:latest, theta:labels, fill:'toself', name:'Latest'}
  ], {polar:{radialaxis:{visible:true,range:[0,100]}}, showlegend:true});
  document.getElementById('radar').on('plotly_click', ev => {
    const step = ev.points[0].theta;
    window.open('reports/CURRENT_CHAT_REPORT.md#' + step, '_blank');
  });

  Plotly.newPlot('violin', [
    {y:data.baseline.distribution, type:'violin', name:'Baseline', box:{visible:true}},
    {y:data.latest.distribution, type:'violin', name:'Latest', box:{visible:true}}
  ], {showlegend:true});

  const diff = labels.map(k => data.latest.dmaic[k] - data.baseline.dmaic[k]);
  Plotly.newPlot('waterfall', [{
    type:'waterfall',
    x:labels,
    y:diff,
    measure: labels.map(()=>'relative'),
    text: diff.map(v => v.toString()),
    textposition:'outside'
  }], {});

  Plotly.newPlot('trend', [{
    x:data.trend.dates,
    y:data.trend.values,
    mode:'lines+markers',
    name:'KPI'
  }], {xaxis:{title:'Date'}, yaxis:{title:'Score'}});
}

async function loadArtefacts(){
  const res = await fetch('artefact_index_markdown.md');
  const text = await res.text();
  document.getElementById('artefact-index').innerHTML = marked.parse(text);

  const lines = text.split('\n').slice(2); // skip header
  const rows = lines.filter(line => line.startsWith('| RQ'));
  const table = document.createElement('table');
  table.className = 'table';
  const header = document.createElement('tr');
  ['Requirement ID','Artefact ID','File'].forEach(h => {
    const th = document.createElement('th');
    th.textContent = h;
    header.appendChild(th);
  });
  table.appendChild(header);
  rows.forEach(line => {
    const cells = line.split('|').map(c => c.trim()).slice(1,4);
    const tr = document.createElement('tr');
    cells.forEach(c => {
      const td = document.createElement('td');
      td.textContent = c;
      tr.appendChild(td);
    });
    table.appendChild(tr);
  });
  const gt = document.getElementById('golden-thread-table');
  gt.innerHTML = '';
  gt.appendChild(table);
}

async function loadSession(){
  const res = await fetch('session_index.json');
  const data = await res.json();
  const list = document.getElementById('session-list');
  data.sessions.forEach(s => {
    const li = document.createElement('li');
    li.textContent = `${s.title} (${s.id})`;
    list.appendChild(li);
  });
}

function initAgents(){
  const output = document.getElementById('agent-output');
  document.getElementById('agent-loose').onclick = () => {
    output.textContent = 'Loose-Ends: no unresolved items.';
    output.style.opacity = 1;
  };
  document.getElementById('agent-open').onclick = () => {
    output.textContent = 'Open: active session CURRENT_SESSION_YYYYMMDDThhmmssZ';
    output.style.opacity = 1;
  };
  document.getElementById('agent-dementor').onclick = () => {
    output.textContent = 'Dementor activated...';
    output.style.opacity = 1;
    setTimeout(() => { output.style.transition = 'opacity 1s'; output.style.opacity = 0; }, 500);
  };
}

window.addEventListener('DOMContentLoaded', () => {
  loadMetrics();
  loadArtefacts();
  loadSession();
  initAgents();
});
