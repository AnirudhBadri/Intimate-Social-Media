/**
 * ZenTab Provenance — Chrono-Lineage & Action Studio UI Controller (panel.js)
 *
 * Drives the Asymmetric Bento Telemetry Grid, Interactive SVG Radial Target-Time Ring,
 * Provenance Circuit Graph, Linear-style Lineage Tree, and Focus Studio Exports.
 */

(function () {
  const params = new URLSearchParams(window.location.search);
  if (params.get("mode") === "sidebar") {
    document.body.classList.add("sidebar-mode");
  }

  let state = {
    activeTabId: null,
    records: {},
    settings: {}
  };

  // DOM References
  const headerStats = document.getElementById("headerStats");
  const openTabCountBadge = document.getElementById("openTabCountBadge");
  const openTutorialBtn = document.getElementById("openTutorialBtn");
  const navTabs = document.querySelectorAll(".nav-tab");
  const viewPanes = document.querySelectorAll(".view-pane");

  // Bento Identity & Telemetry
  const activeFavicon = document.getElementById("activeFavicon");
  const activeTabTitle = document.getElementById("activeTabTitle");
  const activeTabDomain = document.getElementById("activeTabDomain");
  const copyUrlBtn = document.getElementById("copyUrlBtn");
  const activeOpenedAt = document.getElementById("activeOpenedAt");
  const activeDuration = document.getElementById("activeDuration");
  const activeContainer = document.getElementById("activeContainer");

  // SVG Radial Target-Time Ring
  const targetRingArc = document.getElementById("targetRingArc");
  const ringCenterVal = document.getElementById("ringCenterVal");
  const ringCenterSub = document.getElementById("ringCenterSub");
  const targetTimeStatus = document.getElementById("targetTimeStatus");
  const RING_CIRCUMFERENCE = 2 * Math.PI * 26; // r=26 -> ~163.36

  // Circuit Lineage Elements
  const provenanceTriggerBadge = document.getElementById("provenanceTriggerBadge");
  const provSourceTitle = document.getElementById("provSourceTitle");
  const provSourceLink = document.getElementById("provSourceLink");
  const focusOpenerBtn = document.getElementById("focusOpenerBtn");
  const provLinkText = document.getElementById("provLinkText");
  const provSnippet = document.getElementById("provSnippet");
  const copySnippetBtn = document.getElementById("copySnippetBtn");
  const provSelectionRow = document.getElementById("provSelectionRow");
  const provSelection = document.getElementById("provSelection");

  // Action Studio Inputs
  const saveIndicator = document.getElementById("saveIndicator");
  const todoDoneCheck = document.getElementById("todoDoneCheck");
  const todoInput = document.getElementById("todoInput");
  const targetTimeInput = document.getElementById("targetTimeInput");
  const clearTargetTimeBtn = document.getElementById("clearTargetTimeBtn");
  const presetBtns = document.querySelectorAll(".preset-btn[data-offset-min], .preset-btn[data-preset]");
  const spaceTagInput = document.getElementById("spaceTagInput");
  const purposeSelect = document.getElementById("purposeSelect");
  const noteInput = document.getElementById("noteInput");

  // Tree & Groups Elements
  const groupModeSelect = document.getElementById("groupModeSelect");
  const clusterZenTabsBtn = document.getElementById("clusterZenTabsBtn");
  const treeSearchInput = document.getElementById("treeSearchInput");
  const groupsContainer = document.getElementById("groupsContainer");

  // Focus Studio & Settings
  const openGCalBtn = document.getElementById("openGCalBtn");
  const downloadIcsBtn = document.getElementById("downloadIcsBtn");
  const copyMarkdownBtn = document.getElementById("copyMarkdownBtn");
  const exportPreviewBox = document.getElementById("exportPreviewBox");
  const enableMicroHudCheck = document.getElementById("enableMicroHudCheck");
  const defaultSpaceInput = document.getElementById("defaultSpaceInput");

  // -------------------------------------------------------------------------
  // Formatting & Radial Gauge Helpers
  // -------------------------------------------------------------------------

  function formatRelativeAge(timestampMs) {
    if (!timestampMs) return "—";
    const diffSec = Math.max(0, Math.floor((Date.now() - timestampMs) / 1000));
    if (diffSec < 60) return `${diffSec}s ago`;
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ${diffMin % 60}m`;
    const diffDays = Math.floor(diffHr / 24);
    return `${diffDays}d ago`;
  }

  function formatShortClock(timestampMs) {
    if (!timestampMs) return "";
    const d = new Date(timestampMs);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function formatDuration(ms) {
    if (!ms || ms < 1000) return "1s";
    const totalSec = Math.floor(ms / 1000);
    if (totalSec < 60) return `${totalSec}s`;
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    if (mins < 60) return `${mins}m ${secs}s`;
    const hrs = Math.floor(mins / 60);
    return `${hrs}h ${mins % 60}m`;
  }

  function toLocalDatetimeInputValue(ms) {
    if (!ms) return "";
    const d = new Date(ms);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function updateRadialTargetRing(rec) {
    const targetMs = rec ? rec.targetTime : null;
    if (!targetMs) {
      targetRingArc.style.strokeDashoffset = String(RING_CIRCUMFERENCE);
      targetRingArc.style.stroke = "#64748B";
      ringCenterVal.textContent = "—";
      ringCenterSub.textContent = "IDLE";
      targetTimeStatus.textContent = "Unscheduled";
      targetTimeStatus.style.color = "#94A3B8";
      return;
    }

    const now = Date.now();
    const diffMs = targetMs - now;
    const diffMin = Math.round(diffMs / 60000);
    const totalSpanMs = Math.max(15 * 60000, targetMs - (rec.openedAt || now - 3600000));
    const progress = Math.max(0.06, Math.min(1, diffMs / totalSpanMs));
    const offset = RING_CIRCUMFERENCE * (1 - progress);

    targetRingArc.style.strokeDashoffset = String(diffMs <= 0 ? 0 : offset);

    if (rec.todoDone) {
      targetRingArc.style.stroke = "#10B981";
      ringCenterVal.textContent = "DONE";
      ringCenterSub.textContent = "COMPLETE";
      targetTimeStatus.textContent = "✓ Completed";
      targetTimeStatus.style.color = "#10B981";
    } else if (diffMin < 0) {
      targetRingArc.style.stroke = "#F43F5E";
      ringCenterVal.textContent = `${Math.abs(diffMin)}m`;
      ringCenterSub.textContent = "OVERDUE";
      targetTimeStatus.textContent = `Due ${formatShortClock(targetMs)}`;
      targetTimeStatus.style.color = "#F43F5E";
    } else if (diffMin < 60) {
      targetRingArc.style.stroke = "#F59E0B";
      ringCenterVal.textContent = `${diffMin}m`;
      ringCenterSub.textContent = "REMAIN";
      targetTimeStatus.textContent = `At ${formatShortClock(targetMs)}`;
      targetTimeStatus.style.color = "#F59E0B";
    } else {
      const hrs = Math.floor(diffMin / 60);
      targetRingArc.style.stroke = "#22D3EE";
      ringCenterVal.textContent = `${hrs}h${diffMin % 60 ? ` ${diffMin % 60}m` : ""}`;
      ringCenterSub.textContent = "TARGET";
      targetTimeStatus.textContent = `At ${formatShortClock(targetMs)}`;
      targetTimeStatus.style.color = "#22D3EE";
    }
  }

  function flashSaved() {
    saveIndicator.textContent = "✦ Saved";
    saveIndicator.style.color = "#22D3EE";
    setTimeout(() => {
      saveIndicator.textContent = "● Synced";
      saveIndicator.style.color = "#10B981";
    }, 900);
  }

  // -------------------------------------------------------------------------
  // State Loading & Demo Seed (for standalone preview / verification)
  // -------------------------------------------------------------------------

  function buildDemoFallbackState() {
    const now = Date.now();
    return {
      activeTabId: 101,
      settings: { enableMicroHud: true, defaultSpace: "AI Safety Lab" },
      records: {
        "100": {
          tabId: 100,
          index: 0,
          url: "https://github.com/stars",
          domain: "github.com",
          title: "Your Stars · GitHub",
          openedAt: now - 42 * 60000,
          activeDurationMs: 310000,
          container: { name: "Research", color: "purple" },
          spaceTag: "AI Safety Lab",
          purposeCategory: "Code & Repositories",
          provenance: {
            triggerType: "direct",
            sourceUrl: "",
            sourceTitle: "Root Hub Tab"
          },
          todo: "Triage weekly starred AI security repos",
          todoDone: false,
          targetTime: now + 95 * 60000,
          note: "Curating NeurIPS 2026 red-teaming benchmarks."
        },
        "101": {
          tabId: 101,
          index: 1,
          url: "https://github.com/wuyoscar/Internal-Safety-Collapse",
          domain: "github.com",
          title: "wuyoscar/Internal-Safety-Collapse: Adversarial Codespace Setup",
          openedAt: now - 14 * 60000,
          activeDurationMs: 142000,
          container: { name: "AI Safety", color: "purple" },
          spaceTag: "AI Safety Lab",
          purposeCategory: "AI Safety & SecOps",
          provenance: {
            triggerType: "ctrl+click",
            openerTabId: 100,
            sourceUrl: "https://github.com/stars",
            sourceDomain: "github.com",
            sourceTitle: "Your Stars · GitHub",
            linkText: "wuyoscar / Internal-Safety-Collapse",
            surroundingSnippet: "[NeurIPS 2026] We built an adversarial codespace setup. Place any AI agent into a normal workflow inside it, and the agent will fill in whatever is missing.",
            selectedText: "Place any AI agent into a normal workflow inside it"
          },
          todo: "Audit adversarial codespace sandbox & reproduce eval",
          todoDone: false,
          targetTime: now + 38 * 60000,
          note: "High-priority reference for agentic safety evaluation."
        },
        "102": {
          tabId: 102,
          index: 2,
          url: "https://github.com/splunk/attack_data",
          domain: "github.com",
          title: "splunk/attack_data: Curated datasets from various attacks",
          openedAt: now - 13 * 60000,
          activeDurationMs: 45000,
          container: { name: "AI Safety", color: "purple" },
          spaceTag: "AI Safety Lab",
          purposeCategory: "AI Safety & SecOps",
          provenance: {
            triggerType: "ctrl+click",
            openerTabId: 100,
            sourceUrl: "https://github.com/stars",
            sourceDomain: "github.com",
            sourceTitle: "Your Stars · GitHub",
            linkText: "splunk / attack_data",
            surroundingSnippet: "A repository of curated datasets from various attacks · Python ★ 832"
          },
          todo: "Inspect telemetry attack logs schema",
          todoDone: false,
          targetTime: now + 110 * 60000,
          note: ""
        },
        "103": {
          tabId: 103,
          index: 3,
          url: "https://github.com/Wang-Yanting/PIMiner",
          domain: "github.com",
          title: "Wang-Yanting/PIMiner: Indirect Prompt Injection Miner",
          openedAt: now - 12 * 60000,
          activeDurationMs: 19000,
          container: { name: "AI Safety", color: "purple" },
          spaceTag: "AI Safety Lab",
          purposeCategory: "AI Safety & SecOps",
          provenance: {
            triggerType: "ctrl+click",
            openerTabId: 100,
            sourceUrl: "https://github.com/stars",
            sourceDomain: "github.com",
            sourceTitle: "Your Stars · GitHub",
            linkText: "Wang-Yanting / PIMiner",
            surroundingSnippet: "Automated mining framework for indirect prompt injection payloads."
          },
          todo: "Compare with Grey Swan IPI dataset",
          todoDone: true,
          targetTime: now - 15 * 60000,
          note: ""
        }
      }
    };
  }

  async function refreshState() {
    try {
      if (typeof browser !== "undefined" && browser.runtime && browser.runtime.sendMessage) {
        const res = await browser.runtime.sendMessage({ type: "GET_ALL_STATE" });
        if (res && res.ok && Object.keys(res.records || {}).length > 0) {
          state.activeTabId = res.activeTabId;
          state.records = res.records || {};
          state.settings = res.settings || {};
          renderAll();
          return;
        }
      }
    } catch {
      // Fallback to rich demo state when previewed standalone
    }
    state = buildDemoFallbackState();
    renderAll();
  }

  function getAllOpenRecords() {
    return Object.values(state.records).sort((a, b) => (a.index || 0) - (b.index || 0));
  }

  function renderAll() {
    const recordsList = getAllOpenRecords();
    const todoCount = recordsList.filter((r) => r.todo && !r.todoDone).length;
    const ctrlClickCount = recordsList.filter(
      (r) => r.provenance && (r.provenance.triggerType === "ctrl+click" || r.provenance.triggerType === "middle-click")
    ).length;

    headerStats.textContent = `${recordsList.length} tabs · ${ctrlClickCount} Ctrl+Clicked · ${todoCount} active To-Dos`;
    openTabCountBadge.textContent = String(recordsList.length);

    renderActiveTabInspector();
    renderProvenanceTree();
    renderSettings();
  }

  function renderActiveTabInspector() {
    const rec = state.activeTabId ? state.records[String(state.activeTabId)] : null;
    if (!rec) {
      activeTabTitle.textContent = "No active tab selected";
      return;
    }

    activeFavicon.src = rec.favIconUrl || "../icons/icon.svg";
    activeFavicon.onerror = () => {
      activeFavicon.src = "../icons/icon.svg";
    };
    activeTabTitle.textContent = rec.title || rec.url || "Untitled Tab";
    activeTabDomain.textContent = rec.domain || rec.url || "—";
    activeOpenedAt.textContent = `${formatRelativeAge(rec.openedAt)} (${formatShortClock(rec.openedAt)})`;
    activeDuration.textContent = formatDuration(rec.activeDurationMs);
    activeContainer.textContent = rec.container ? rec.container.name : "Default";

    updateRadialTargetRing(rec);

    // Provenance Circuit Details
    const prov = rec.provenance || {};
    provenanceTriggerBadge.textContent = prov.triggerType || "direct";

    if (prov.sourceUrl) {
      provSourceTitle.textContent = prov.sourceTitle || prov.sourceDomain || prov.sourceUrl;
      provSourceLink.href = prov.sourceUrl;
      provSourceLink.hidden = false;
    } else {
      provSourceTitle.textContent = prov.sourceTitle || "Direct Navigation / External App";
      provSourceLink.hidden = true;
    }

    if (prov.openerTabId && state.records[String(prov.openerTabId)]) {
      focusOpenerBtn.hidden = false;
      focusOpenerBtn.onclick = () => {
        if (typeof browser !== "undefined" && browser.runtime) {
          browser.runtime.sendMessage({ type: "FOCUS_TAB", tabId: prov.openerTabId });
        }
        state.activeTabId = prov.openerTabId;
        renderAll();
      };
    } else {
      focusOpenerBtn.hidden = true;
    }

    provLinkText.textContent = prov.linkText || rec.title || "—";
    provSnippet.textContent =
      prov.surroundingSnippet ||
      "Opened without surrounding DOM text (or opened directly via address bar / external app).";

    if (prov.selectedText) {
      provSelectionRow.hidden = false;
      provSelection.textContent = `“${prov.selectedText}”`;
    } else {
      provSelectionRow.hidden = true;
    }

    // Editor inputs
    todoDoneCheck.checked = Boolean(rec.todoDone);
    if (document.activeElement !== todoInput) {
      todoInput.value = rec.todo || "";
    }
    if (document.activeElement !== noteInput) {
      noteInput.value = rec.note || "";
    }
    if (document.activeElement !== spaceTagInput) {
      spaceTagInput.value = rec.spaceTag || "Main Zen Space";
    }
    if (document.activeElement !== purposeSelect) {
      purposeSelect.value = rec.purposeCategory || "General Exploration";
    }
    if (document.activeElement !== targetTimeInput) {
      targetTimeInput.value = toLocalDatetimeInputValue(rec.targetTime);
    }
  }

  // -------------------------------------------------------------------------
  // Provenance Tree & Grouping Renderer
  // -------------------------------------------------------------------------

  function renderProvenanceTree() {
    const mode = groupModeSelect.value || "referrer";
    const query = (treeSearchInput.value || "").toLowerCase().trim();
    const allRecords = getAllOpenRecords().filter((rec) => {
      if (!query) return true;
      const hay = [
        rec.title,
        rec.url,
        rec.todo,
        rec.note,
        rec.spaceTag,
        rec.purposeCategory,
        rec.provenance?.sourceTitle,
        rec.provenance?.sourceUrl,
        rec.provenance?.linkText,
        rec.provenance?.surroundingSnippet
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return hay.includes(query);
    });

    const groupsMap = new Map();

    allRecords.forEach((rec) => {
      let groupKey = "Other";
      if (mode === "referrer") {
        if (rec.provenance && rec.provenance.sourceUrl) {
          const srcTitle = rec.provenance.sourceTitle || rec.provenance.sourceDomain;
          groupKey = `Origin Hub: ${srcTitle}`;
        } else {
          groupKey = "Root Hubs & Direct Tabs";
        }
      } else if (mode === "purpose") {
        groupKey = rec.purposeCategory || "General Exploration";
      } else if (mode === "todo") {
        if (rec.todoDone) groupKey = "✓ Completed Actions";
        else if (rec.targetTime && rec.targetTime <= Date.now()) groupKey = "🚨 Target-Time Overdue";
        else if (rec.targetTime) groupKey = "⏰ Scheduled Target-Time";
        else if (rec.todo) groupKey = "📌 Active To-Do Queue";
        else groupKey = "Unscheduled Tabs";
      } else if (mode === "burst") {
        const d = new Date(rec.openedAt || Date.now());
        const bucketMin = Math.floor(d.getMinutes() / 15) * 15;
        const labelTime = `${String(d.getHours()).padStart(2, "0")}:${String(bucketMin).padStart(2, "0")}`;
        groupKey = `Burst Window · ${d.toLocaleDateString([], { month: "short", day: "numeric" })} @ ${labelTime}`;
      } else if (mode === "space") {
        groupKey = `${rec.spaceTag || "Main Zen Space"} · ${rec.container?.name || "Default"}`;
      }

      if (!groupsMap.has(groupKey)) {
        groupsMap.set(groupKey, []);
      }
      groupsMap.get(groupKey).push(rec);
    });

    groupsContainer.innerHTML = "";

    if (groupsMap.size === 0) {
      groupsContainer.innerHTML = `<div class="bento-card"><p class="helper-text">No open tabs match your filter.</p></div>`;
      return;
    }

    for (const [groupTitle, items] of groupsMap.entries()) {
      const card = document.createElement("div");
      card.className = "group-card";

      const header = document.createElement("div");
      header.className = "group-header";
      header.innerHTML = `
        <span>${escapeHtml(groupTitle)}</span>
        <span class="tab-pill">${items.length}</span>
      `;
      card.appendChild(header);

      const listEl = document.createElement("div");
      listEl.className = "group-items";

      items.forEach((rec) => {
        const row = document.createElement("div");
        row.className = "tree-tab-item";
        const isCurrent = rec.tabId === state.activeTabId;

        const snippetPreview = rec.provenance?.surroundingSnippet
          ? `“${rec.provenance.surroundingSnippet.slice(0, 68)}…”`
          : `Trigger: ${rec.provenance?.triggerType || "direct"}`;

        row.innerHTML = `
          <div class="tree-tab-top">
            <span class="tree-tab-title">
              ${isCurrent ? "✦ " : ""}${escapeHtml(rec.title || rec.url)}
            </span>
            <span class="tree-tab-age">${formatRelativeAge(rec.openedAt)}</span>
          </div>
          <div class="tree-tab-sub">
            <span>${escapeHtml(snippetPreview)}</span>
            ${rec.todo ? `<span class="badge-todo">${rec.todoDone ? "✓ " : "⚡ "}${escapeHtml(rec.todo)}</span>` : ""}
            ${rec.targetTime ? `<span class="badge-target">⏰ ${formatShortClock(rec.targetTime)}</span>` : ""}
          </div>
        `;

        row.addEventListener("click", () => {
          if (typeof browser !== "undefined" && browser.runtime) {
            browser.runtime.sendMessage({ type: "FOCUS_TAB", tabId: rec.tabId }).catch(() => {});
          }
          state.activeTabId = rec.tabId;
          switchNavTab("inspector");
          renderAll();
        });

        listEl.appendChild(row);
      });

      card.appendChild(listEl);
      groupsContainer.appendChild(card);
    }
  }

  function renderSettings() {
    enableMicroHudCheck.checked = state.settings.enableMicroHud !== false;
    if (document.activeElement !== defaultSpaceInput) {
      defaultSpaceInput.value = state.settings.defaultSpace || "Main Zen Space";
    }
  }

  function escapeHtml(str = "") {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // -------------------------------------------------------------------------
  // Interactive Updates & Event Listeners
  // -------------------------------------------------------------------------

  async function patchActiveRecord(patch) {
    if (!state.activeTabId) return;
    const key = String(state.activeTabId);
    if (state.records[key]) {
      Object.assign(state.records[key], patch);
    }
    if (typeof browser !== "undefined" && browser.runtime && browser.runtime.sendMessage) {
      try {
        const res = await browser.runtime.sendMessage({
          type: "UPDATE_TAB_RECORD",
          tabId: state.activeTabId,
          patch
        });
        if (res && res.ok) {
          state.records[key] = res.record;
        }
      } catch {
        // Standalone preview mode
      }
    }
    flashSaved();
    renderAll();
  }

  let debounceTimer = null;
  function debouncedPatch(patch) {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => patchActiveRecord(patch), 220);
  }

  todoDoneCheck.addEventListener("change", () => {
    patchActiveRecord({ todoDone: todoDoneCheck.checked });
  });

  todoInput.addEventListener("input", () => {
    debouncedPatch({ todo: todoInput.value });
  });

  noteInput.addEventListener("input", () => {
    debouncedPatch({ note: noteInput.value });
  });

  spaceTagInput.addEventListener("input", () => {
    debouncedPatch({ spaceTag: spaceTagInput.value });
  });

  purposeSelect.addEventListener("change", () => {
    patchActiveRecord({ purposeCategory: purposeSelect.value });
  });

  targetTimeInput.addEventListener("change", () => {
    const val = targetTimeInput.value;
    const ms = val ? new Date(val).getTime() : null;
    patchActiveRecord({ targetTime: ms });
  });

  clearTargetTimeBtn.addEventListener("click", () => {
    targetTimeInput.value = "";
    patchActiveRecord({ targetTime: null });
  });

  presetBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const offsetMin = btn.getAttribute("data-offset-min");
      const preset = btn.getAttribute("data-preset");
      let targetMs = null;

      if (offsetMin) {
        targetMs = Date.now() + Number(offsetMin) * 60 * 1000;
      } else if (preset === "tonight") {
        const d = new Date();
        d.setHours(21, 0, 0, 0);
        if (d.getTime() <= Date.now()) d.setTime(Date.now() + 2 * 3600000);
        targetMs = d.getTime();
      } else if (preset === "tomorrow") {
        const d = new Date();
        d.setDate(d.getDate() + 1);
        d.setHours(10, 0, 0, 0);
        targetMs = d.getTime();
      }

      if (targetMs) {
        targetTimeInput.value = toLocalDatetimeInputValue(targetMs);
        patchActiveRecord({ targetTime: targetMs });
      }
    });
  });

  copyUrlBtn.addEventListener("click", () => {
    const rec = state.activeTabId ? state.records[String(state.activeTabId)] : null;
    if (!rec || !rec.url) return;
    navigator.clipboard?.writeText(rec.url).catch(() => {});
    copyUrlBtn.textContent = "✓";
    setTimeout(() => {
      copyUrlBtn.textContent = "⧉";
    }, 900);
  });

  copySnippetBtn.addEventListener("click", () => {
    const text = provSnippet.textContent || "";
    navigator.clipboard?.writeText(text).catch(() => {});
    copySnippetBtn.textContent = "✓ Copied";
    setTimeout(() => {
      copySnippetBtn.textContent = "Copy";
    }, 1000);
  });

  // View Tab Navigation + Keyboard Shortcuts
  function switchNavTab(tabName) {
    navTabs.forEach((btn) => {
      btn.classList.toggle("active", btn.getAttribute("data-tab") === tabName);
    });
    viewPanes.forEach((pane) => {
      pane.classList.toggle("active", pane.id === `view-${tabName}`);
    });
  }

  navTabs.forEach((btn) => {
    btn.addEventListener("click", () => {
      switchNavTab(btn.getAttribute("data-tab"));
    });
  });

  window.addEventListener("keydown", (e) => {
    const tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
    if (tag === "input" || tag === "textarea" || tag === "select") return;
    if (e.key === "1") switchNavTab("inspector");
    if (e.key === "2") switchNavTab("tree");
    if (e.key === "3") switchNavTab("export");
    if (e.key === "/") {
      e.preventDefault();
      switchNavTab("tree");
      treeSearchInput.focus();
    }
  });

  groupModeSelect.addEventListener("change", renderProvenanceTree);
  treeSearchInput.addEventListener("input", renderProvenanceTree);

  clusterZenTabsBtn.addEventListener("click", async () => {
    const mapMode = {
      referrer: "referrer",
      purpose: "purpose",
      todo: "targetTime",
      burst: "openedAt",
      space: "purpose"
    };
    const mode = mapMode[groupModeSelect.value] || "referrer";
    if (typeof browser !== "undefined" && browser.runtime) {
      await browser.runtime.sendMessage({ type: "CLUSTER_TABS_IN_BROWSER", mode }).catch(() => {});
    }
    clusterZenTabsBtn.textContent = "✓ Sorted in Zen!";
    setTimeout(() => {
      clusterZenTabsBtn.textContent = "⇄ Sort Zen Sidebar";
      refreshState();
    }, 1200);
  });

  openTutorialBtn.addEventListener("click", () => {
    if (typeof browser !== "undefined" && browser.runtime && browser.runtime.sendMessage) {
      browser.runtime.sendMessage({ type: "OPEN_TUTORIAL" }).catch(() => {
        window.open("../onboarding/tutorial.html", "_blank");
      });
    } else {
      window.open("../onboarding/tutorial.html", "_blank");
    }
  });

  // -------------------------------------------------------------------------
  // Calendar (.ics & Google Calendar) + Antigravity Markdown Exports
  // -------------------------------------------------------------------------

  function getActionableRecords() {
    const all = getAllOpenRecords();
    const withTodoOrTarget = all.filter((r) => (r.todo && r.todo.trim()) || r.targetTime);
    return withTodoOrTarget.length > 0 ? withTodoOrTarget : all;
  }

  function buildMarkdownChecklist() {
    const items = getActionableRecords();
    const lines = [
      `# ZenTab Provenance & Action Queue (${new Date().toLocaleString()})`,
      ""
    ];

    items.forEach((r) => {
      const check = r.todoDone ? "[x]" : "[ ]";
      const todoLabel = r.todo ? `**${r.todo}** — ` : "";
      const targetStr = r.targetTime ? ` *(Target: ${new Date(r.targetTime).toLocaleString()})*` : "";
      const originStr = r.provenance?.sourceUrl
        ? ` | Origin: [${r.provenance.sourceTitle || r.provenance.sourceDomain}](${r.provenance.sourceUrl}) via \`${r.provenance.triggerType}\``
        : "";
      lines.push(`- ${check} ${todoLabel}[${r.title || r.url}](${r.url})${targetStr}${originStr}`);
      if (r.provenance?.surroundingSnippet) {
        lines.push(`  - *DOM Snippet:* "${r.provenance.surroundingSnippet}"`);
      }
      if (r.note) {
        lines.push(`  - *Note:* ${r.note}`);
      }
    });

    return lines.join("\n");
  }

  copyMarkdownBtn.addEventListener("click", async () => {
    const md = buildMarkdownChecklist();
    exportPreviewBox.textContent = md;
    exportPreviewBox.hidden = false;
    try {
      await navigator.clipboard.writeText(md);
    } catch {
      // Fallback preview shown below
    }
    const titleEl = copyMarkdownBtn.querySelector(".tile-title");
    if (titleEl) {
      const orig = titleEl.textContent;
      titleEl.textContent = "✓ Copied Provenance Checklist to Clipboard!";
      setTimeout(() => {
        titleEl.textContent = orig;
      }, 2000);
    }
  });

  function toIcsUtcTimestamp(ms) {
    const d = new Date(ms);
    return d.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
  }

  openGCalBtn.addEventListener("click", () => {
    const items = getActionableRecords();
    const earliestTarget = items
      .map((r) => r.targetTime)
      .filter(Boolean)
      .sort((a, b) => a - b)[0] || (Date.now() + 30 * 60 * 1000);

    const endMs = earliestTarget + 45 * 60 * 1000;
    const datesParam = `${toIcsUtcTimestamp(earliestTarget)}/${toIcsUtcTimestamp(endMs)}`;
    const details = buildMarkdownChecklist();
    const gcalUrl = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent(
      `ZenTab Focus Block (${items.length} Tabs)`
    )}&dates=${datesParam}&details=${encodeURIComponent(details)}`;

    if (typeof browser !== "undefined" && browser.tabs && browser.tabs.create) {
      browser.tabs.create({ url: gcalUrl, active: true });
    } else {
      window.open(gcalUrl, "_blank");
    }
  });

  downloadIcsBtn.addEventListener("click", () => {
    const items = getActionableRecords();
    const startMs = items
      .map((r) => r.targetTime)
      .filter(Boolean)
      .sort((a, b) => a - b)[0] || (Date.now() + 30 * 60 * 1000);
    const endMs = startMs + 45 * 60 * 1000;
    const desc = buildMarkdownChecklist().replace(/\n/g, "\\n");

    const icsContent = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//ZenTab Provenance//EN",
      "BEGIN:VEVENT",
      `UID:zentab-${Date.now()}@zen.local`,
      `DTSTAMP:${toIcsUtcTimestamp(Date.now())}`,
      `DTSTART:${toIcsUtcTimestamp(startMs)}`,
      `DTEND:${toIcsUtcTimestamp(endMs)}`,
      `SUMMARY:ZenTab Provenance Focus Block (${items.length} Tabs)`,
      `DESCRIPTION:${desc}`,
      "END:VEVENT",
      "END:VCALENDAR"
    ].join("\r\n");

    const blob = new Blob([icsContent], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `zentab-focus-block-${Date.now()}.ics`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 2000);
  });

  enableMicroHudCheck.addEventListener("change", () => {
    if (typeof browser !== "undefined" && browser.runtime) {
      browser.runtime.sendMessage({
        type: "UPDATE_SETTINGS",
        patch: { enableMicroHud: enableMicroHudCheck.checked }
      }).catch(() => {});
    }
  });

  defaultSpaceInput.addEventListener("change", () => {
    if (typeof browser !== "undefined" && browser.runtime) {
      browser.runtime.sendMessage({
        type: "UPDATE_SETTINGS",
        patch: { defaultSpace: defaultSpaceInput.value.trim() || "Main Zen Space" }
      }).catch(() => {});
    }
  });

  if (typeof browser !== "undefined" && browser.tabs && browser.tabs.onActivated) {
    browser.tabs.onActivated.addListener(() => refreshState());
    browser.tabs.onUpdated.addListener((_id, changeInfo) => {
      if (changeInfo.status === "complete" || changeInfo.title) refreshState();
    });
  }

  refreshState();
})();
