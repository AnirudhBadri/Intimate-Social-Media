/**
 * ZenTab Space — Chrono-Spatial Tab Sanctuary Controller (space_view.js)
 * 
 * Manages dynamic constellation node positioning, SVG connection rays,
 * live tab correlation, provenance inspector sync, and Zen tab ordering.
 */

(function () {
  let state = {
    activeTabId: null,
    records: {},
    settings: {},
    activeFilter: 'all',
    viewMode: 'constellation' // 'constellation' | 'cards'
  };

  // DOM Elements
  const nodesLayer = document.getElementById('nodesLayer');
  const constellationSvg = document.getElementById('constellationSvg');
  const currentSpaceBadge = document.getElementById('currentSpaceBadge');
  const sanctuaryStats = document.getElementById('sanctuaryStats');
  const spaceSearchInput = document.getElementById('spaceSearchInput');
  const taxonomyFilters = document.querySelectorAll('.space-pill');
  const sortZenTabsBtn = document.getElementById('sortZenTabsBtn');

  // Metrics
  const metricParentCount = document.getElementById('metricParentCount');
  const metricActionCount = document.getElementById('metricActionCount');
  const metricReadingTime = document.getElementById('metricReadingTime');

  // Dock Elements
  const dockTriggerBadge = document.getElementById('dockTriggerBadge');
  const dockFavicon = document.getElementById('dockFavicon');
  const dockTabTitle = document.getElementById('dockTabTitle');
  const dockTabDomain = document.getElementById('dockTabDomain');
  const dockCopyUrlBtn = document.getElementById('dockCopyUrlBtn');
  const dockOpenedAt = document.getElementById('dockOpenedAt');
  const dockActiveDuration = document.getElementById('dockActiveDuration');
  const dockContainer = document.getElementById('dockContainer');

  const dockOriginSubtext = document.getElementById('dockOriginSubtext');
  const dockOriginUrl = document.getElementById('dockOriginUrl');
  const dockJumpParentBtn = document.getElementById('dockJumpParentBtn');
  const dockAnchorText = document.getElementById('dockAnchorText');
  const dockSnippet = document.getElementById('dockSnippet');
  const dockCopySnippetBtn = document.getElementById('dockCopySnippetBtn');

  const dockSaveStatus = document.getElementById('dockSaveStatus');
  const dockTodoCheck = document.getElementById('dockTodoCheck');
  const dockTodoInput = document.getElementById('dockTodoInput');
  const dockTargetStatus = document.getElementById('dockTargetStatus');
  const dockTargetInput = document.getElementById('dockTargetInput');
  const dockClearTargetBtn = document.getElementById('dockClearTargetBtn');
  const dockNoteInput = document.getElementById('dockNoteInput');
  const presetPills = document.querySelectorAll('.preset-pill[data-min], .preset-pill[data-preset]');

  const dockCalendarExportBtn = document.getElementById('dockCalendarExportBtn');
  const dockCopyMdBtn = document.getElementById('dockCopyMdBtn');

  // Mode Toggles
  const modeConstellationBtn = document.getElementById('modeConstellationBtn');
  const modeCardsBtn = document.getElementById('modeCardsBtn');

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------
  function formatRelativeAge(timestampMs) {
    if (!timestampMs) return '—';
    const diffSec = Math.max(0, Math.floor((Date.now() - timestampMs) / 1000));
    if (diffSec < 60) return `${diffSec}s ago`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ${diffMin % 60}m`;
    return `${Math.floor(diffHr / 24)}d ago`;
  }

  function formatDuration(ms) {
    if (!ms || ms < 1000) return '1s';
    const totalSec = Math.floor(ms / 1000);
    if (totalSec < 60) return `${totalSec}s`;
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    if (mins < 60) return `${mins}m ${secs}s`;
    return `${Math.floor(mins / 60)}h ${mins % 60}m`;
  }

  function toLocalDatetimeInputValue(ms) {
    if (!ms) return '';
    const d = new Date(ms);
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function escapeHtml(str = '') {
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // -------------------------------------------------------------------------
  // Fallback State Seed (Rich default for preview)
  // -------------------------------------------------------------------------
  function buildFallbackState() {
    const now = Date.now();
    return {
      activeTabId: 101,
      settings: { defaultSpace: 'AI Safety Sanctuary' },
      records: {
        '100': {
          tabId: 100,
          index: 0,
          url: 'https://github.com/stars',
          domain: 'github.com',
          title: 'Your Stars · GitHub',
          openedAt: now - 50 * 60000,
          activeDurationMs: 420000,
          container: { name: 'Personal', color: 'blue' },
          spaceTag: 'AI Safety Sanctuary',
          purposeCategory: 'Code & Repositories',
          provenance: {
            triggerType: 'direct',
            sourceUrl: '',
            sourceTitle: 'Root Hub Origin'
          },
          todo: 'Review weekly starred AI defense repos',
          todoDone: false,
          targetTime: now + 60 * 60000,
          note: 'Primary research springboard for safety evaluations.'
        },
        '101': {
          tabId: 101,
          index: 1,
          url: 'https://github.com/wuyoscar/Internal-Safety-Collapse',
          domain: 'github.com',
          title: 'wuyoscar/Internal-Safety-Collapse: Adversarial Codespace Setup',
          openedAt: now - 22 * 60000,
          activeDurationMs: 184000,
          container: { name: 'AI Safety', color: 'purple' },
          spaceTag: 'AI Safety Sanctuary',
          purposeCategory: 'AI Safety & SecOps',
          provenance: {
            triggerType: 'ctrl+click',
            openerTabId: 100,
            sourceUrl: 'https://github.com/stars',
            sourceDomain: 'github.com',
            sourceTitle: 'Your Stars · GitHub',
            linkText: 'wuyoscar / Internal-Safety-Collapse',
            surroundingSnippet: '[NeurIPS 2026] We built an adversarial codespace setup. Place any AI agent into a normal workflow inside it, and the agent will fill in whatever is missing.'
          },
          todo: 'Audit harness sandboxing & reproduce baseline runs',
          todoDone: false,
          targetTime: now + 30 * 60000,
          note: 'Key paper for prompt injection and codespace escapes.'
        },
        '102': {
          tabId: 102,
          index: 2,
          url: 'https://github.com/splunk/attack_data',
          domain: 'github.com',
          title: 'splunk/attack_data: Curated datasets from various attacks',
          openedAt: now - 18 * 60000,
          activeDurationMs: 95000,
          container: { name: 'AI Safety', color: 'purple' },
          spaceTag: 'AI Safety Sanctuary',
          purposeCategory: 'AI Safety & SecOps',
          provenance: {
            triggerType: 'ctrl+click',
            openerTabId: 100,
            sourceUrl: 'https://github.com/stars',
            sourceDomain: 'github.com',
            sourceTitle: 'Your Stars · GitHub',
            linkText: 'splunk / attack_data',
            surroundingSnippet: 'A repository of curated datasets from various attacks for security telemetry.'
          },
          todo: 'Compare log schemas against our internal benchmarks',
          todoDone: true,
          targetTime: now + 120 * 60000,
          note: ''
        },
        '103': {
          tabId: 103,
          index: 3,
          url: 'https://github.com/Wang-Yanting/PIMiner',
          domain: 'github.com',
          title: 'Wang-Yanting/PIMiner: Indirect Prompt Injection Miner',
          openedAt: now - 15 * 60000,
          activeDurationMs: 45000,
          container: { name: 'AI Safety', color: 'purple' },
          spaceTag: 'AI Safety Sanctuary',
          purposeCategory: 'AI Safety & SecOps',
          provenance: {
            triggerType: 'ctrl+click',
            openerTabId: 100,
            sourceUrl: 'https://github.com/stars',
            sourceDomain: 'github.com',
            sourceTitle: 'Your Stars · GitHub',
            linkText: 'Wang-Yanting / PIMiner',
            surroundingSnippet: 'Automated mining and evaluation framework for indirect prompt injection vulnerabilities.'
          },
          todo: '',
          todoDone: false,
          targetTime: null,
          note: ''
        }
      }
    };
  }

  // -------------------------------------------------------------------------
  // Data Loading & Sync
  // -------------------------------------------------------------------------
  async function refreshSpaceState() {
    try {
      if (typeof browser !== 'undefined' && browser.runtime && browser.runtime.sendMessage) {
        const res = await browser.runtime.sendMessage({ type: 'GET_ALL_STATE' });
        if (res && res.ok && Object.keys(res.records || {}).length > 0) {
          state.activeTabId = res.activeTabId;
          state.records = res.records || {};
          state.settings = res.settings || {};
          renderSpace();
          return;
        }
      }
    } catch {
      // preview environment
    }
    const seed = buildFallbackState();
    state.activeTabId = seed.activeTabId;
    state.records = seed.records;
    state.settings = seed.settings;
    renderSpace();
  }

  function getRecordsArray() {
    return Object.values(state.records).sort((a, b) => (a.index || 0) - (b.index || 0));
  }

  // -------------------------------------------------------------------------
  // Rendering the Spatial Constellation
  // -------------------------------------------------------------------------
  function renderSpace() {
    const records = getRecordsArray();
    const query = (spaceSearchInput.value || '').toLowerCase().trim();

    // Update Header
    currentSpaceBadge.textContent = state.settings.defaultSpace || 'AI Sanctuary';
    const totalCount = records.length;
    const provCount = records.filter(r => r.provenance && r.provenance.sourceUrl).length;
    sanctuaryStats.textContent = `${totalCount} open nodes · ${provCount} provenance-linked`;

    // Metrics
    const parentIds = new Set(records.map(r => r.provenance?.openerTabId).filter(Boolean));
    metricParentCount.textContent = String(parentIds.size || 1);
    const withTodo = records.filter(r => r.todo && !r.todoDone).length;
    metricActionCount.textContent = String(withTodo);
    const totalMs = records.reduce((acc, r) => acc + (r.activeDurationMs || 0), 0);
    metricReadingTime.textContent = formatDuration(totalMs);

    // Filter
    const filtered = records.filter(rec => {
      // Taxonomy pill check
      if (state.activeFilter === 'with-todo' && (!rec.todo || rec.todoDone)) return false;
      if (state.activeFilter === 'target-soon' && (!rec.targetTime || rec.targetTime > Date.now() + 86400000)) return false;
      if (state.activeFilter !== 'all' && state.activeFilter !== 'with-todo' && state.activeFilter !== 'target-soon') {
        if (rec.purposeCategory !== state.activeFilter) return false;
      }
      // Search query check
      if (query) {
        const hay = [
          rec.title,
          rec.url,
          rec.domain,
          rec.todo,
          rec.note,
          rec.provenance?.linkText,
          rec.provenance?.surroundingSnippet,
          rec.provenance?.sourceTitle
        ].filter(Boolean).join(' ').toLowerCase();
        return hay.includes(query);
      }
      return true;
    });

    renderConstellationNodes(filtered);
    renderDockInspector();
  }

  function renderConstellationNodes(records) {
    nodesLayer.innerHTML = '';
    constellationSvg.innerHTML = '<defs><linearGradient id="beamGradient" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="var(--p-accent)" stop-opacity="0.8"/><stop offset="100%" stop-color="#a855F7" stop-opacity="0.2"/></linearGradient></defs>';

    if (records.length === 0) {
      nodesLayer.innerHTML = `<div style="padding: 40px; color: var(--p-muted); text-align: center;">No tab nodes match your current space filter.</div>`;
      return;
    }

    const nodeCoords = new Map();
    const isCardsMode = state.viewMode === 'cards';

    // Layout Algorithm: Constellation Organic Orbit vs Cards Grid
    if (isCardsMode) {
      nodesLayer.style.display = 'grid';
      nodesLayer.style.gridTemplateColumns = 'repeat(auto-fill, minmax(260px, 1fr))';
      nodesLayer.style.gap = '16px';
      nodesLayer.style.position = 'static';
    } else {
      nodesLayer.style.display = 'block';
      nodesLayer.style.position = 'relative';

      // Constellation tree layout: place root hubs on the left, child tabs branching out rightward
      let hubY = 60;
      records.forEach((rec, idx) => {
        const isRoot = !rec.provenance || !rec.provenance.openerTabId || !state.records[String(rec.provenance.openerTabId)];
        let x, y;
        if (isRoot) {
          x = 40;
          y = hubY;
          hubY += 190;
        } else {
          // Children positioned in radial/staggered column
          const col = 1 + (idx % 2);
          x = 340 + (col - 1) * 270;
          y = 40 + ((idx - 1) * 140);
        }
        nodeCoords.set(rec.tabId, { x, y });
      });
    }

    // Render node elements
    records.forEach((rec) => {
      const card = document.createElement('div');
      card.className = `spatial-node ${rec.tabId === state.activeTabId ? 'selected' : ''} ${!rec.provenance?.openerTabId ? 'is-root-hub' : ''}`;
      card.id = `node-${rec.tabId}`;

      if (!isCardsMode) {
        const pos = nodeCoords.get(rec.tabId) || { x: 40, y: 40 };
        card.style.left = `${pos.x}px`;
        card.style.top = `${pos.y}px`;
      } else {
        card.style.position = 'static';
        card.style.width = '100%';
      }

      const snippet = rec.provenance?.surroundingSnippet 
        ? escapeHtml(rec.provenance.surroundingSnippet) 
        : `Trigger: ${rec.provenance?.triggerType || 'direct'}`;

      let actionHtml = '';
      if (rec.todo) {
        actionHtml = `<span class="node-todo-indicator ${rec.todoDone ? 'done' : ''}">⚡ ${escapeHtml(rec.todo)}</span>`;
      }

      card.innerHTML = `
        <div class="node-halo-header">
          <div class="node-fav-wrap">
            <img src="${rec.favIconUrl || '../icons/icon.svg'}" class="node-fav-img" onerror="this.src='../icons/icon.svg'" />
          </div>
          <span class="node-category-tag">${escapeHtml(rec.purposeCategory || 'General')}</span>
        </div>
        <div class="node-card-title">${escapeHtml(rec.title || rec.url)}</div>
        <div class="node-card-snippet">${snippet}</div>
        <div class="node-card-footer">
          <span class="node-time-badge">${formatRelativeAge(rec.openedAt)}</span>
          ${actionHtml}
        </div>
      `;

      card.addEventListener('click', () => {
        state.activeTabId = rec.tabId;
        if (typeof browser !== 'undefined' && browser.runtime) {
          browser.runtime.sendMessage({ type: 'FOCUS_TAB', tabId: rec.tabId }).catch(() => {});
        }
        renderSpace();
      });

      nodesLayer.appendChild(card);
    });

    // Draw connecting bezier constellation lines between parent and children
    if (!isCardsMode) {
      records.forEach(rec => {
        if (rec.provenance && rec.provenance.openerTabId && nodeCoords.has(rec.provenance.openerTabId)) {
          const parentCoord = nodeCoords.get(rec.provenance.openerTabId);
          const childCoord = nodeCoords.get(rec.tabId);
          if (parentCoord && childCoord) {
            const startX = parentCoord.x + 250;
            const startY = parentCoord.y + 60;
            const endX = childCoord.x;
            const endY = childCoord.y + 60;
            const ctrlX = (startX + endX) / 2;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', `M ${startX} ${startY} C ${ctrlX} ${startY}, ${ctrlX} ${endY}, ${endX} ${endY}`);
            const isRelated = rec.tabId === state.activeTabId || rec.provenance.openerTabId === state.activeTabId;
            path.setAttribute('class', `constellation-edge ${isRelated ? 'highlighted' : ''}`);
            constellationSvg.appendChild(path);
          }
        }
      });
    }
  }

  // -------------------------------------------------------------------------
  // Rendering the Dock Inspector
  // -------------------------------------------------------------------------
  function renderDockInspector() {
    const rec = state.activeTabId ? state.records[String(state.activeTabId)] : null;
    if (!rec) {
      dockTabTitle.textContent = 'Select any tab node in the space';
      dockTabDomain.textContent = '—';
      return;
    }

    dockTriggerBadge.textContent = rec.provenance?.triggerType || 'direct';
    dockFavicon.src = rec.favIconUrl || '../icons/icon.svg';
    dockFavicon.onerror = () => { dockFavicon.src = '../icons/icon.svg'; };
    dockTabTitle.textContent = rec.title || rec.url;
    dockTabDomain.textContent = rec.domain || rec.url;

    dockOpenedAt.textContent = formatRelativeAge(rec.openedAt);
    dockActiveDuration.textContent = formatDuration(rec.activeDurationMs);
    dockContainer.textContent = rec.container?.name || 'Default';

    // Provenance Circuit
    const prov = rec.provenance || {};
    if (prov.sourceUrl) {
      dockOriginSubtext.textContent = prov.sourceTitle || prov.sourceDomain || 'Parent Hub';
      dockOriginUrl.href = prov.sourceUrl;
      dockOriginUrl.hidden = false;
    } else {
      dockOriginSubtext.textContent = 'Direct Navigation / Root Origin';
      dockOriginUrl.hidden = true;
    }

    if (prov.openerTabId && state.records[String(prov.openerTabId)]) {
      dockJumpParentBtn.hidden = false;
      dockJumpParentBtn.onclick = () => {
        state.activeTabId = prov.openerTabId;
        renderSpace();
      };
    } else {
      dockJumpParentBtn.hidden = true;
    }

    dockAnchorText.textContent = prov.linkText || rec.title || '—';
    dockSnippet.textContent = prov.surroundingSnippet || 'Directly opened without DOM snippet context.';

    // Action Forge Inputs
    dockTodoCheck.checked = Boolean(rec.todoDone);
    if (document.activeElement !== dockTodoInput) {
      dockTodoInput.value = rec.todo || '';
    }
    if (document.activeElement !== dockNoteInput) {
      dockNoteInput.value = rec.note || '';
    }
    if (document.activeElement !== dockTargetInput) {
      dockTargetInput.value = toLocalDatetimeInputValue(rec.targetTime);
    }

    if (!rec.targetTime) {
      dockTargetStatus.textContent = 'Unscheduled';
      dockTargetStatus.style.color = 'var(--p-muted)';
    } else {
      const diffMin = Math.round((rec.targetTime - Date.now()) / 60000);
      if (diffMin < 0) {
        dockTargetStatus.textContent = `Overdue (${Math.abs(diffMin)}m ago)`;
        dockTargetStatus.style.color = 'var(--color-rose)';
      } else if (diffMin < 60) {
        dockTargetStatus.textContent = `Due in ${diffMin}m`;
        dockTargetStatus.style.color = 'var(--color-amber)';
      } else {
        dockTargetStatus.textContent = `Due in ${Math.floor(diffMin / 60)}h`;
        dockTargetStatus.style.color = 'var(--p-accent)';
      }
    }
  }

  // -------------------------------------------------------------------------
  // Interactivity & Event Handlers
  // -------------------------------------------------------------------------
  async function patchActiveTab(patch) {
    if (!state.activeTabId) return;
    const key = String(state.activeTabId);
    if (state.records[key]) {
      Object.assign(state.records[key], patch);
    }
    if (typeof browser !== 'undefined' && browser.runtime && browser.runtime.sendMessage) {
      try {
        await browser.runtime.sendMessage({
          type: 'UPDATE_TAB_RECORD',
          tabId: state.activeTabId,
          patch
        });
      } catch {}
    }
    dockSaveStatus.textContent = '✦ Saved';
    setTimeout(() => { dockSaveStatus.textContent = '● Synced'; }, 800);
    renderSpace();
  }

  dockTodoCheck.addEventListener('change', () => {
    patchActiveTab({ todoDone: dockTodoCheck.checked });
  });

  let todoTimer;
  dockTodoInput.addEventListener('input', () => {
    clearTimeout(todoTimer);
    todoTimer = setTimeout(() => {
      patchActiveTab({ todo: dockTodoInput.value.trim() });
    }, 240);
  });

  let noteTimer;
  dockNoteInput.addEventListener('input', () => {
    clearTimeout(noteTimer);
    noteTimer = setTimeout(() => {
      patchActiveTab({ note: dockNoteInput.value.trim() });
    }, 240);
  });

  dockTargetInput.addEventListener('change', () => {
    const val = dockTargetInput.value;
    const ms = val ? new Date(val).getTime() : null;
    patchActiveTab({ targetTime: ms });
  });

  dockClearTargetBtn.addEventListener('click', () => {
    dockTargetInput.value = '';
    patchActiveTab({ targetTime: null });
  });

  presetPills.forEach(btn => {
    btn.addEventListener('click', () => {
      const min = btn.getAttribute('data-min');
      const preset = btn.getAttribute('data-preset');
      let targetMs = null;
      if (min) {
        targetMs = Date.now() + Number(min) * 60000;
      } else if (preset === 'tonight') {
        const d = new Date();
        d.setHours(21, 0, 0, 0);
        if (d.getTime() <= Date.now()) d.setTime(Date.now() + 2 * 3600000);
        targetMs = d.getTime();
      } else if (preset === 'tomorrow') {
        const d = new Date();
        d.setDate(d.getDate() + 1);
        d.setHours(10, 0, 0, 0);
        targetMs = d.getTime();
      }
      if (targetMs) {
        dockTargetInput.value = toLocalDatetimeInputValue(targetMs);
        patchActiveTab({ targetTime: targetMs });
      }
    });
  });

  taxonomyFilters.forEach(pill => {
    pill.addEventListener('click', () => {
      taxonomyFilters.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      state.activeFilter = pill.getAttribute('data-filter');
      renderSpace();
    });
  });

  spaceSearchInput.addEventListener('input', () => {
    renderSpace();
  });

  window.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement !== spaceSearchInput) {
      e.preventDefault();
      spaceSearchInput.focus();
    }
  });

  modeConstellationBtn.addEventListener('click', () => {
    modeConstellationBtn.classList.add('active');
    modeCardsBtn.classList.remove('active');
    state.viewMode = 'constellation';
    renderSpace();
  });

  modeCardsBtn.addEventListener('click', () => {
    modeCardsBtn.classList.add('active');
    modeConstellationBtn.classList.remove('active');
    state.viewMode = 'cards';
    renderSpace();
  });

  dockCopyUrlBtn.addEventListener('click', () => {
    const rec = state.activeTabId ? state.records[String(state.activeTabId)] : null;
    if (rec && rec.url) {
      navigator.clipboard?.writeText(rec.url);
      dockCopyUrlBtn.innerHTML = '✓';
      setTimeout(() => {
        dockCopyUrlBtn.innerHTML = '<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>';
      }, 900);
    }
  });

  dockCopySnippetBtn.addEventListener('click', () => {
    const text = dockSnippet.textContent || '';
    navigator.clipboard?.writeText(text);
    dockCopySnippetBtn.textContent = '✓ Copied';
    setTimeout(() => { dockCopySnippetBtn.textContent = 'Copy'; }, 1000);
  });

  sortZenTabsBtn.addEventListener('click', async () => {
    if (typeof browser !== 'undefined' && browser.runtime) {
      await browser.runtime.sendMessage({ type: 'CLUSTER_TABS_IN_BROWSER', mode: 'referrer' }).catch(() => {});
    }
    sortZenTabsBtn.querySelector('span').textContent = '✓ Sorted in Zen!';
    setTimeout(() => {
      sortZenTabsBtn.querySelector('span').textContent = 'Sort Zen Tabs';
      refreshSpaceState();
    }, 1200);
  });

  // Calendar and Markdown Exports
  dockCalendarExportBtn.addEventListener('click', () => {
    const rec = state.activeTabId ? state.records[String(state.activeTabId)] : null;
    const target = rec?.targetTime || Date.now() + 30 * 60000;
    const end = target + 45 * 60000;
    const pad = (n) => String(n).padStart(2, '0');
    const fmt = (ms) => {
      const d = new Date(ms);
      return `${d.getUTCFullYear()}${pad(d.getUTCMonth()+1)}${pad(d.getUTCDate())}T${pad(d.getUTCHours())}${pad(d.getUTCMinutes())}00Z`;
    };
    const details = `ZenTab Focus Block: ${rec?.title || 'Open Tabs'}\nOrigin: ${rec?.provenance?.sourceUrl || 'Direct'}\nNote: ${rec?.note || ''}`;
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(`Zen Focus: ${rec?.title || 'Research Block'}`)}&dates=${fmt(target)}/${fmt(end)}&details=${encodeURIComponent(details)}`;
    window.open(url, '_blank');
  });

  dockCopyMdBtn.addEventListener('click', () => {
    const records = getRecordsArray();
    const lines = [`# ZenTab Space Sanctuary Tasks (${new Date().toLocaleDateString()})`, ''];
    records.forEach(r => {
      const chk = r.todoDone ? '[x]' : '[ ]';
      const todo = r.todo ? `**${r.todo}** — ` : '';
      const orig = r.provenance?.sourceUrl ? ` *(From: [${r.provenance.sourceTitle || r.provenance.sourceDomain}](${r.provenance.sourceUrl}))*` : '';
      lines.push(`- ${chk} ${todo}[${r.title || r.url}](${r.url})${orig}`);
      if (r.provenance?.surroundingSnippet) {
        lines.push(`  - *Snippet:* "${r.provenance.surroundingSnippet}"`);
      }
    });
    navigator.clipboard?.writeText(lines.join('\n'));
    dockCopyMdBtn.querySelector('span').textContent = '✓ Copied Markdown!';
    setTimeout(() => { dockCopyMdBtn.querySelector('span').textContent = '📋 Copy Markdown'; }, 1200);
  });

  // Initial Boot
  refreshSpaceState();
})();
