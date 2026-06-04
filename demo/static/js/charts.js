/* Shared Plotly mount + resize + entity-panel helper.

   1. Resize fix — when a card chart is swapped in via HTMX the inline <script>
      runs before the browser has laid out the new nodes, so a responsive Plotly
      read a 0/stale container width and fell back to its ~700px default (the
      chart looked "half size"). A full reload settled layout first, so it filled.
      We mount, then force a resize on the next two animation frames once layout
      has settled, and again after every HTMX swap.

   2. Entity panel (spec A1) — a chart whose traces carry `meta.entity` + `meta.fields`
      becomes clickable: clicking a point slides in a right-hand detail panel built
      from that point's `customdata`. This is the single click->panel handoff the
      design locked in place of simultaneous cross-chart brushing. */
(function () {
  // ── resize ─────────────────────────────────────────────────────────────
  function resizeOne(el) {
    if (el && el.offsetParent !== null && window.Plotly) {
      try { Plotly.Plots.resize(el); } catch (e) { /* not a plot yet */ }
    }
  }
  function resizeAll() { document.querySelectorAll('.js-plotly-plot').forEach(resizeOne); }

  // ── entity panel ───────────────────────────────────────────────────────
  function ensurePanel() {
    var p = document.getElementById('entity-panel');
    if (p) return p;
    var overlay = document.createElement('div');
    overlay.id = 'entity-overlay';
    overlay.className = 'epanel-overlay';
    overlay.addEventListener('click', closePanel);
    p = document.createElement('aside');
    p.id = 'entity-panel';
    p.className = 'epanel';
    p.innerHTML =
      '<div class="epanel-band"></div>' +
      '<div class="epanel-hd">' +
        '<div class="epanel-typerow">' +
          '<span class="epanel-pill" id="epanel-kind"></span>' +
          '<button class="epanel-x" id="epanel-x" aria-label="Close">&times;</button>' +
        '</div>' +
        '<div class="epanel-namerow">' +
          '<div class="epanel-title" id="epanel-title"></div>' +
          '<div class="epanel-hero" id="epanel-hero" style="display:none">' +
            '<div class="epanel-hero-v" id="epanel-hero-v"></div>' +
            '<div class="epanel-hero-l" id="epanel-hero-l"></div>' +
          '</div>' +
        '</div>' +
        '<div class="epanel-sub" id="epanel-sub"></div>' +
      '</div>' +
      '<div class="epanel-body">' +
        '<div class="epanel-metrics" id="epanel-metrics"></div>' +
        '<div class="epanel-list" id="epanel-list" style="display:none"></div>' +
        '<div class="epanel-note" id="epanel-note" style="display:none"></div>' +
      '</div>' +
      '<div class="epanel-foot">' +
        '<button class="epanel-act" id="epanel-export"><span class="epanel-act-ic">PDF</span>Export as PDF<span class="epanel-act-arr">&darr;</span></button>' +
        '<button class="epanel-act" id="epanel-copy"><span class="epanel-act-ic">&#128279;</span><span id="epanel-copy-l">Copy shareable link</span><span class="epanel-act-arr">&rarr;</span></button>' +
      '</div>';
    document.body.appendChild(overlay);
    document.body.appendChild(p);
    p.querySelector('#epanel-x').addEventListener('click', closePanel);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closePanel(); });
    // Footer actions (spec §5.1)
    p.querySelector('#epanel-export').addEventListener('click', function () { window.print(); });
    p.querySelector('#epanel-copy').addEventListener('click', function () {
      var lbl = document.getElementById('epanel-copy-l');
      var done = function () { lbl.textContent = 'Link copied'; setTimeout(function () { lbl.textContent = 'Copy shareable link'; }, 1600); };
      if (navigator.clipboard) { navigator.clipboard.writeText(window.location.href).then(done, done); }
      else { done(); }
    });
    return p;
  }
  function closePanel() {
    var p = document.getElementById('entity-panel');
    var o = document.getElementById('entity-overlay');
    if (p) p.classList.remove('open');
    if (o) o.classList.remove('open');
  }
  function fmt(v, f) {
    if (v === null || v === undefined) return '—';
    if (f === ',') return Number(v).toLocaleString();
    if (f === '%') return (Number(v)).toFixed(0) + '%';
    if (f === '%1') return (Number(v)).toFixed(1) + '%';
    if (f === '₫') return '₫' + Number(v).toLocaleString();
    return v;
  }
  function openPanel(pt) {
    var m = pt.data.meta || {};
    var cd = pt.customdata || [];
    var p = ensurePanel();
    // accent of the active card (falls back to orange)
    var shell = document.querySelector('.card-shell');
    var ac = (shell && getComputedStyle(shell).getPropertyValue('--ac').trim()) || '#E45A2E';
    p.style.setProperty('--ac', ac);

    var kind = m.entity || 'Detail';
    var title = (m.titleIdx != null ? cd[m.titleIdx] : (pt.text || pt.label || ''));
    document.getElementById('epanel-kind').textContent = kind;
    document.getElementById('epanel-title').textContent = title;
    document.getElementById('epanel-sub').textContent = m.sub || '';

    var fields = (m.fields || []).slice();
    var hero = document.getElementById('epanel-hero');
    if (fields.length) {
      var h = fields.shift();          // first field becomes the hero KPI
      document.getElementById('epanel-hero-v').textContent = fmt(cd[h.idx], h.fmt);
      document.getElementById('epanel-hero-l').textContent = h.label;
      hero.style.display = '';
    } else {
      hero.style.display = 'none';
    }

    var grid = document.getElementById('epanel-metrics');
    grid.innerHTML = '';
    fields.forEach(function (f) {
      var c = document.createElement('div');
      c.className = 'epanel-mcard';
      c.innerHTML = '<div class="epanel-mv">' + fmt(cd[f.idx], f.fmt) + '</div>' +
                    '<div class="epanel-ml">' + f.label + '</div>';
      grid.appendChild(c);
    });
    grid.style.display = fields.length ? 'grid' : 'none';

    // optional list section (spec §11: e.g. a school's serving routes)
    var list = document.getElementById('epanel-list');
    var items = (m.list && Array.isArray(cd[m.list.idx])) ? cd[m.list.idx] : [];
    if (items.length) {
      var rows = items.map(function (it) {
        return '<div class="epanel-li"><span class="epanel-li-k">Route ' + it[0] + '</span>' +
               '<span class="epanel-li-v">' + Number(it[1]).toLocaleString() + '</span></div>';
      }).join('');
      list.innerHTML = '<div class="epanel-list-hd">' + m.list.label +
                       (m.list.unit ? ' <span>· ' + m.list.unit + '</span>' : '') + '</div>' + rows;
      list.style.display = '';
    } else {
      list.style.display = 'none';
    }

    var note = document.getElementById('epanel-note');
    if (m.note) { note.textContent = m.note; note.style.display = ''; }
    else { note.style.display = 'none'; }

    var o = document.getElementById('entity-overlay');
    p.classList.add('open');
    if (o) o.classList.add('open');
  }
  function bindPanel(tgt) {
    if (!tgt || tgt.__panelBound) return;
    var hasMeta = (tgt.data || []).some(function (tr) { return tr.meta && tr.meta.entity; });
    if (!hasMeta) return;
    tgt.__panelBound = true;
    tgt.on('plotly_click', function (ev) {
      if (!ev || !ev.points || !ev.points.length) return;
      var pt = ev.points[0];
      if (pt.data && pt.data.meta && pt.data.meta.entity) openPanel(pt);
    });
    tgt.style.cursor = 'pointer';
  }

  // ── mount ──────────────────────────────────────────────────────────────
  function mount(targetId, fig, onReady) {
    (function go() {
      var tgt = document.getElementById(targetId);
      if (!tgt) return;
      if (!window.Plotly) { return setTimeout(go, 40); }
      Plotly.newPlot(tgt, fig.data, fig.layout, { displayModeBar: false, responsive: true })
        .then(function () {
          requestAnimationFrame(function () {
            requestAnimationFrame(function () { resizeOne(tgt); });
          });
          bindPanel(tgt);
          if (typeof onReady === 'function') onReady(tgt);
        });
    })();
  }

  document.addEventListener('htmx:afterSettle', function () {
    requestAnimationFrame(function () { requestAnimationFrame(resizeAll); });
  });
  window.addEventListener('resize', resizeAll);

  window.BusCharts = { mount: mount, resizeAll: resizeAll, resizeOne: resizeOne, closePanel: closePanel };
})();
