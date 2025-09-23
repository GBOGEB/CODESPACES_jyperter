document.addEventListener('DOMContentLoaded', function () {
  // Load metrics and render charts
  fetch('metrics.json').then(r => r.json()).then(drawCharts);

  // Build artefact tree
  fetch('session_index.json').then(r => r.json()).then(buildTree);

  // Render DMAIC cycle
  renderDmaic();

  // Golden thread viewer
  fetch('artefact_index_markdown.md').then(r => r.text()).then(t => {
    document.getElementById('golden-thread').innerHTML = marked.parse(t);
  });

  // Agent buttons
  document.getElementById('agent-loose').addEventListener('click', () => {
    alert('Loose-Ends triggered');
  });
  document.getElementById('agent-open').addEventListener('click', () => {
    alert('Open triggered');
  });
  document.getElementById('agent-dementor').addEventListener('click', () => {
    const out = document.getElementById('agent-output');
    out.textContent = 'Dementor sucked stale blobs';
    out.classList.add('fade');
  });
});

function drawCharts(data) {
  const radar = [
    {type: 'scatterpolar', r: data.baseline, theta: data.metric_labels, fill:'toself', name:'Baseline'},
    {type: 'scatterpolar', r: data.latest, theta: data.metric_labels, fill:'toself', name:'Latest'}
  ];
  Plotly.newPlot('radar-chart', radar, {polar:{radialaxis:{visible:true}}});

  const line = [
    {x: data.metric_labels, y: data.baseline, name:'Baseline'},
    {x: data.metric_labels, y: data.latest, name:'Latest'}
  ];
  Plotly.newPlot('line-chart', line, {});

  const violin = data.metric_labels.map((lbl, i) => ({
    type:'violin', y:[data.baseline[i], data.latest[i]], name:lbl
  }));
  Plotly.newPlot('violin-chart', violin, {violinmode:'group'});

  const waterfall = [{
    type:'waterfall',
    x: data.metric_labels,
    measure: Array(data.metric_labels.length).fill('relative'),
    y: data.latest.map((v,i)=>v-data.baseline[i]),
    textposition:'outside'
  }];
  Plotly.newPlot('waterfall-chart', waterfall, {});
}

function buildTree(tree) {
  const data = Object.keys(tree).map(dir => ({
    text: dir,
    children: tree[dir].map(f => ({ text: f, a_attr:{ href: dir + '/' + f, target: '_blank' } }))
  }));
  $('#artefact-tree').jstree({ 'core': { 'data': data } });
}

function renderDmaic() {
  const stages = ['Define','Measure','Analyze','Improve','Control'];
  const trace = [{
    type:'scatterpolar',
    r:Array(stages.length).fill(1),
    theta:stages,
    mode:'markers',
    marker:{size:12}
  }];
  const layout = {polar:{radialaxis:{visible:false}},showlegend:false};
  Plotly.newPlot('dmaic-cycle', trace, layout);
  const links = {
    'Define':'handover/README.md',
    'Measure':'metrics.json',
    'Analyze':'reports/CURRENT_CHAT_REPORT.md',
    'Improve':'',
    'Control':''
  };
  document.getElementById('dmaic-cycle').addEventListener('plotly_click', function(evt){
    const stage = evt.points[0].theta;
    if (links[stage]) { window.open(links[stage]); }
  });
}
