/**
 * ZenTab Provenance & Action Tracker — Background Correlation Engine
 *
 * Responsibilities:
 * 1. Correlate Content Script Ctrl+Click / Middle-Click DOM snapshots with
 *    browser.tabs.onCreated and browser.webNavigation.onCreatedNavigationTarget.
 * 2. Persist per-tab Provenance, Notes, To-Dos, Target-Times, and Zen Space tags
 *    in browser.storage.local (with URL fallback archive across session restores).
 * 3. Track cumulative active reading time (activeDurationMs) per tab.
 * 4. Schedule browser.alarms for Target-Time reminders and fire notifications.
 * 5. Provide zero-cost deterministic grouping & physical tab clustering via browser.tabs.move.
 * 6. Launch the interactive click-through tutorial on extension install.
 */

const STORAGE_KEYS = {
  TAB_RECORDS: "zentab_records_v1",
  URL_ARCHIVE: "zentab_url_archive_v1",
  SETTINGS: "zentab_settings_v1",
  TUTORIAL_PROGRESS: "zentab_tutorial_v1"
};

const DEFAULT_SETTINGS = {
  enableMicroHud: true,
  hudDurationMs: 4500,
  autoInferPurpose: true,
  defaultSpace: "Main Zen Space",
  restoreFromUrlArchive: true
};

// In-memory state synced to browser.storage.local
let tabRecords = {};       // { [tabId: string]: TabRecord }
let urlArchive = {};       // { [normalizedUrl: string]: TabRecordSnapshot }
let settings = { ...DEFAULT_SETTINGS };

// Ephemeral correlation buffer for pending Ctrl+Click / Middle-Click actions
// Array of { clickId, sourceTabId, targetUrl, normTargetUrl, sourceUrl, sourceTitle,
//            linkText, surroundingSnippet, selectedText, triggerType, modifiers,
//            spaceHint, clickedAt, matchedTabId, pendingPatch }
const pendingClicks = [];
const PENDING_TTL_MS = 12000;

// Active tab time tracking
let currentActiveTabId = null;
let currentActiveStartMs = null;

// ---------------------------------------------------------------------------
// Utility Helpers
// ---------------------------------------------------------------------------

function normalizeUrl(rawUrl) {
  if (!rawUrl || typeof rawUrl !== "string") return "";
  try {
    const u = new URL(rawUrl);
    if (u.protocol === "about:" || u.protocol === "moz-extension:") return rawUrl;
    // Strip common tracking query params while preserving meaningful query params
    const stripParams = [
      "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
      "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "ref_src"
    ];
    stripParams.forEach((p) => u.searchParams.delete(p));
    u.hash = "";
    return u.toString().replace(/\/$/, "");
  } catch {
    return rawUrl.trim();
  }
}

function extractDomain(rawUrl) {
  if (!rawUrl) return "browser";
  try {
    const u = new URL(rawUrl);
    if (u.protocol === "moz-extension:") return "ZenTab Extension";
    if (u.protocol === "about:") return u.pathname || "about";
    return u.hostname.replace(/^www\./, "");
  } catch {
    return "unknown";
  }
}

/**
 * Zero-LLM deterministic purpose classifier based on URL, title, and DOM snippet.
 */
function inferPurposeCategory(url = "", title = "", snippet = "") {
  const haystack = `${url} ${title} ${snippet}`.toLowerCase();

  if (
    /github\.com|gitlab\.com|bitbucket\.org|commits|pull\/|issues\/|crates\.io|npmjs\.com|pypi\.org/.test(haystack)
  ) {
    if (/attack|security|cve-|red-team|exploit|prompt-injection|safety|adversarial|atlas\.mitre/.test(haystack)) {
      return "AI Safety & SecOps";
    }
    return "Code & Repositories";
  }
  if (
    /arxiv\.org|biorxiv\.org|openreview\.net|scholar\.google|huggingface\.co|paperswithcode|neurips|icml|iclr/.test(haystack)
  ) {
    return "Research & Papers";
  }
  if (
    /attack|security|cve-|red-team|owasp|mitre|greyswan|prompt-injection|safety/.test(haystack)
  ) {
    return "AI Safety & SecOps";
  }
  if (
    /console\.cloud\.google|aistudio\.google|billing|aws\.amazon|dashboard|stripe\.com|netlify|vercel/.test(haystack)
  ) {
    return "Cloud & Billing Admin";
  }
  if (
    /docs\.|developer\.mozilla|stackoverflow\.com|readthedocs|wiki|manual|reference|api/.test(haystack)
  ) {
    return "Docs & Reference";
  }
  if (
    /youtube\.com|vimeo\.com|substack\.com|medium\.com|news\.ycombinator|reddit\.com|blog/.test(haystack)
  ) {
    return "Reading & Media";
  }
  return "General Exploration";
}

async function resolveContainerInfo(cookieStoreId) {
  if (!cookieStoreId || cookieStoreId === "firefox-default") {
    return { name: "Default Container", color: "slate", cookieStoreId: "firefox-default" };
  }
  if (cookieStoreId === "firefox-private") {
    return { name: "Private Window", color: "purple", cookieStoreId };
  }
  try {
    if (browser.contextualIdentities && browser.contextualIdentities.get) {
      const identity = await browser.contextualIdentities.get(cookieStoreId);
      if (identity) {
        return {
          name: identity.name,
          color: identity.color || "blue",
          icon: identity.icon || "",
          cookieStoreId
        };
      }
    }
  } catch {
    // contextualIdentities may not be enabled in all profiles
  }
  return { name: cookieStoreId, color: "blue", cookieStoreId };
}

let saveTimeout = null;
function scheduleStorageSave() {
  if (saveTimeout) clearTimeout(saveTimeout);
  saveTimeout = setTimeout(async () => {
    try {
      await browser.storage.local.set({
        [STORAGE_KEYS.TAB_RECORDS]: tabRecords,
        [STORAGE_KEYS.URL_ARCHIVE]: urlArchive,
        [STORAGE_KEYS.SETTINGS]: settings
      });
    } catch (err) {
      console.error("[ZenTab] Storage save error:", err);
    }
  }, 150);
}

function archiveRecordByUrl(record) {
  if (!record || !record.url) return;
  const norm = normalizeUrl(record.url);
  if (!norm || norm.startsWith("about:")) return;

  // Only archive if it has meaningful provenance or user annotations
  const hasUserAnnotations = Boolean(
    (record.note && record.note.trim()) ||
    (record.todo && record.todo.trim()) ||
    record.targetTime
  );
  const hasRichProvenance = Boolean(
    record.provenance && (record.provenance.sourceUrl || record.provenance.surroundingSnippet)
  );

  if (hasUserAnnotations || hasRichProvenance) {
    urlArchive[norm] = {
      url: record.url,
      title: record.title,
      note: record.note || "",
      todo: record.todo || "",
      todoDone: Boolean(record.todoDone),
      targetTime: record.targetTime || null,
      targetDurationMin: record.targetDurationMin || 25,
      spaceTag: record.spaceTag || settings.defaultSpace,
      purposeCategory: record.purposeCategory || "General Exploration",
      provenance: record.provenance,
      archivedAt: Date.now()
    };

    // Cap archive size to 400 recent URLs to keep storage ultra-light
    const keys = Object.keys(urlArchive);
    if (keys.length > 400) {
      keys
        .sort((a, b) => (urlArchive[a].archivedAt || 0) - (urlArchive[b].archivedAt || 0))
        .slice(0, keys.length - 400)
        .forEach((k) => delete urlArchive[k]);
    }
  }
}

// ---------------------------------------------------------------------------
// Pending Click Correlation Queue
// ---------------------------------------------------------------------------

function pruneExpiredClicks() {
  const cutoff = Date.now() - PENDING_TTL_MS;
  for (let i = pendingClicks.length - 1; i >= 0; i--) {
    if (pendingClicks[i].clickedAt < cutoff) {
      pendingClicks.splice(i, 1);
    }
  }
}

function findMatchingPendingClick(openerTabId, candidateUrl) {
  pruneExpiredClicks();
  const normCandidate = normalizeUrl(candidateUrl);

  // 1. Exact openerTabId + normalized URL match (newest first)
  for (let i = pendingClicks.length - 1; i >= 0; i--) {
    const item = pendingClicks[i];
    if (item.matchedTabId) continue;
    if (openerTabId && item.sourceTabId === openerTabId && normCandidate && item.normTargetUrl === normCandidate) {
      return item;
    }
  }

  // 2. Match by normalized URL across any tab within last 5 seconds (handles no-opener or middle-click quirks)
  if (normCandidate && !normCandidate.startsWith("about:")) {
    for (let i = pendingClicks.length - 1; i >= 0; i--) {
      const item = pendingClicks[i];
      if (item.matchedTabId) continue;
      if (item.normTargetUrl === normCandidate && Date.now() - item.clickedAt < 5000) {
        return item;
      }
    }
  }

  // 3. Fallback: most recent unmatched click from the exact openerTabId within 3500ms
  // (Crucial when tab.url is initially "about:blank" during tabs.onCreated!)
  if (openerTabId !== undefined && openerTabId !== null) {
    for (let i = pendingClicks.length - 1; i >= 0; i--) {
      const item = pendingClicks[i];
      if (item.matchedTabId) continue;
      if (item.sourceTabId === openerTabId && Date.now() - item.clickedAt < 3500) {
        return item;
      }
    }
  }

  return null;
}

// ---------------------------------------------------------------------------
// Core Tab Record Lifecycle
// ---------------------------------------------------------------------------

async function createOrUpdateTabRecord(tab, explicitProvenance = null) {
  const tabIdKey = String(tab.id);
  const now = Date.now();
  const existing = tabRecords[tabIdKey];
  const container = await resolveContainerInfo(tab.cookieStoreId);

  // Check if there is a pending Ctrl+Click match
  const matchedClick = explicitProvenance || findMatchingPendingClick(tab.openerTabId, tab.url);
  if (matchedClick && !matchedClick.matchedTabId) {
    matchedClick.matchedTabId = tab.id;
  }

  // Also check if openerTabId exists in our tabRecords so we can pull parent metadata even without a content script match
  const openerRecord = tab.openerTabId ? tabRecords[String(tab.openerTabId)] : null;

  let provenance = existing ? { ...existing.provenance } : {
    triggerType: tab.openerTabId ? "tab-spawn" : "direct-or-external",
    openerTabId: tab.openerTabId || null,
    sourceUrl: openerRecord ? openerRecord.url : "",
    sourceDomain: openerRecord ? extractDomain(openerRecord.url) : (tab.openerTabId ? "parent-tab" : "Direct / External App"),
    sourceTitle: openerRecord ? openerRecord.title : (tab.openerTabId ? `Tab #${tab.openerTabId}` : "Direct Navigation / External App"),
    linkText: "",
    surroundingSnippet: "",
    selectedText: "",
    modifiers: {},
    capturedAt: now
  };

  if (matchedClick) {
    provenance = {
      triggerType: matchedClick.triggerType || "ctrl+click",
      openerTabId: tab.openerTabId || matchedClick.sourceTabId || null,
      sourceUrl: matchedClick.sourceUrl || provenance.sourceUrl || "",
      sourceDomain: extractDomain(matchedClick.sourceUrl || provenance.sourceUrl),
      sourceTitle: matchedClick.sourceTitle || provenance.sourceTitle || "",
      linkText: matchedClick.linkText || provenance.linkText || "",
      surroundingSnippet: matchedClick.surroundingSnippet || provenance.surroundingSnippet || "",
      selectedText: matchedClick.selectedText || provenance.selectedText || "",
      modifiers: matchedClick.modifiers || {},
      capturedAt: matchedClick.clickedAt || now
    };
  }

  const effectiveUrl = (tab.url && tab.url !== "about:blank")
    ? tab.url
    : (matchedClick && matchedClick.targetUrl ? matchedClick.targetUrl : (existing ? existing.url : "about:blank"));

  const effectiveTitle = (tab.title && tab.title !== "New Tab" && tab.title !== "about:blank")
    ? tab.title
    : (matchedClick && matchedClick.linkText ? matchedClick.linkText : (existing ? existing.title : effectiveUrl));

  // Check URL archive if this is a restored tab
  const normUrl = normalizeUrl(effectiveUrl);
  const archived = (settings.restoreFromUrlArchive && normUrl && urlArchive[normUrl]) ? urlArchive[normUrl] : null;

  const purposeCategory = inferPurposeCategory(
    effectiveUrl,
    effectiveTitle,
    provenance.surroundingSnippet || provenance.linkText
  );

  const record = {
    tabId: tab.id,
    windowId: tab.windowId,
    index: tab.index,
    pinned: Boolean(tab.pinned),
    url: effectiveUrl,
    domain: extractDomain(effectiveUrl),
    title: effectiveTitle,
    favIconUrl: tab.favIconUrl || (existing ? existing.favIconUrl : ""),
    openedAt: existing ? existing.openedAt : (matchedClick ? matchedClick.clickedAt : now),
    lastUpdatedAt: now,
    activeDurationMs: existing ? (existing.activeDurationMs || 0) : 0,
    container,
    spaceTag: existing
      ? existing.spaceTag
      : (matchedClick && matchedClick.spaceHint)
        ? matchedClick.spaceHint
        : (openerRecord && openerRecord.spaceTag)
          ? openerRecord.spaceTag
          : (container.cookieStoreId !== "firefox-default" ? container.name : (archived ? archived.spaceTag : settings.defaultSpace)),
    purposeCategory: existing && existing.userSetPurpose ? existing.purposeCategory : purposeCategory,
    userSetPurpose: existing ? Boolean(existing.userSetPurpose) : false,
    provenance: (
      provenance.sourceUrl || !archived || !archived.provenance
    ) ? provenance : archived.provenance,
    note: existing && existing.note
      ? existing.note
      : (archived && archived.note ? archived.note : ""),
    todo: existing && existing.todo
      ? existing.todo
      : (archived && archived.todo ? archived.todo : ""),
    todoDone: existing ? Boolean(existing.todoDone) : (archived ? Boolean(archived.todoDone) : false),
    targetTime: existing && existing.targetTime
      ? existing.targetTime
      : (archived && archived.targetTime ? archived.targetTime : null),
    targetDurationMin: existing && existing.targetDurationMin
      ? existing.targetDurationMin
      : 25
  };

  // Apply any Micro-HUD annotation patch that arrived while the tab was still being created
  if (matchedClick && matchedClick.pendingPatch) {
    Object.assign(record, matchedClick.pendingPatch);
    if (matchedClick.pendingPatch.targetTime) {
      scheduleTargetAlarm(tab.id, matchedClick.pendingPatch.targetTime, record.title);
    }
  }

  tabRecords[tabIdKey] = record;
  archiveRecordByUrl(record);
  scheduleStorageSave();
  return record;
}

// ---------------------------------------------------------------------------
// Active Tab Time Tracking & Alarms
// ---------------------------------------------------------------------------

function commitActiveTabDuration() {
  if (currentActiveTabId !== null && currentActiveStartMs !== null) {
    const elapsed = Math.max(0, Date.now() - currentActiveStartMs);
    const rec = tabRecords[String(currentActiveTabId)];
    if (rec && elapsed < 3600000) {
      rec.activeDurationMs = (rec.activeDurationMs || 0) + elapsed;
      scheduleStorageSave();
    }
  }
  currentActiveStartMs = Date.now();
}

function scheduleTargetAlarm(tabId, targetTimeMs, tabTitle = "") {
  const alarmName = `zentab-target-${tabId}`;
  browser.alarms.clear(alarmName);
  if (!targetTimeMs || targetTimeMs <= Date.now()) return;
  browser.alarms.create(alarmName, { when: Number(targetTimeMs) });
}

browser.alarms.onAlarm.addListener(async (alarm) => {
  if (!alarm.name.startsWith("zentab-target-")) return;
  const tabId = Number(alarm.name.replace("zentab-target-", ""));
  const rec = tabRecords[String(tabId)];
  if (!rec || rec.todoDone) return;

  try {
    await browser.notifications.create(`zentab-notif-${tabId}`, {
      type: "basic",
      iconUrl: browser.runtime.getURL("icons/icon.svg"),
      title: `ZenTab Target Time Reached`,
      message: `${rec.todo ? `To-Do: ${rec.todo}` : rec.title}\nOrigin: ${rec.provenance?.sourceTitle || rec.domain}`
    });
  } catch (err) {
    console.warn("[ZenTab] Notification error:", err);
  }
});

browser.notifications.onClicked.addListener(async (notificationId) => {
  if (!notificationId.startsWith("zentab-notif-")) return;
  const tabId = Number(notificationId.replace("zentab-notif-", ""));
  try {
    const tab = await browser.tabs.get(tabId);
    if (tab) {
      await browser.tabs.update(tabId, { active: true });
      await browser.windows.update(tab.windowId, { focused: true });
    }
  } catch {
    // Tab may have been closed
  }
});

// ---------------------------------------------------------------------------
// WebExtension Event Listeners
// ---------------------------------------------------------------------------

browser.tabs.onCreated.addListener((tab) => {
  createOrUpdateTabRecord(tab);
});

browser.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url || changeInfo.title || changeInfo.status === "complete" || changeInfo.pinned !== undefined) {
    createOrUpdateTabRecord(tab);
  }
});

browser.tabs.onActivated.addListener(({ tabId }) => {
  commitActiveTabDuration();
  currentActiveTabId = tabId;
  currentActiveStartMs = Date.now();
});

browser.tabs.onRemoved.addListener((tabId) => {
  if (currentActiveTabId === tabId) {
    commitActiveTabDuration();
    currentActiveTabId = null;
  }
  const key = String(tabId);
  if (tabRecords[key]) {
    archiveRecordByUrl(tabRecords[key]);
    delete tabRecords[key];
    scheduleStorageSave();
  }
  browser.alarms.clear(`zentab-target-${tabId}`);
});

if (browser.webNavigation && browser.webNavigation.onCreatedNavigationTarget) {
  browser.webNavigation.onCreatedNavigationTarget.addListener(async (details) => {
    // details: { sourceTabId, sourceFrameId, url, tabId, timeStamp }
    const matchedClick = findMatchingPendingClick(details.sourceTabId, details.url);
    try {
      const tab = await browser.tabs.get(details.tabId);
      if (!tab.openerTabId && details.sourceTabId) {
        tab.openerTabId = details.sourceTabId;
      }
      await createOrUpdateTabRecord(tab, matchedClick);
    } catch {
      // Tab may not be queryable yet
    }
  });
}

// Context menu item to open a link with an immediate To-Do prompt
try {
  browser.menus.create({
    id: "zentab-open-with-todo",
    title: "Open in New Tab + Add ZenTab To-Do",
    contexts: ["link"]
  });

  browser.menus.onClicked.addListener(async (info, tab) => {
    if (info.menuItemId === "zentab-open-with-todo" && info.linkUrl) {
      const clickEntry = {
        clickId: `ctx-${Date.now()}`,
        sourceTabId: tab ? tab.id : null,
        targetUrl: info.linkUrl,
        normTargetUrl: normalizeUrl(info.linkUrl),
        sourceUrl: info.pageUrl || (tab ? tab.url : ""),
        sourceTitle: tab ? tab.title : "",
        linkText: info.linkText || info.linkUrl,
        surroundingSnippet: info.selectionText || "Opened via ZenTab Context Menu",
        selectedText: info.selectionText || "",
        triggerType: "context-menu",
        modifiers: { contextMenu: true },
        spaceHint: tab && tabRecords[String(tab.id)] ? tabRecords[String(tab.id)].spaceTag : settings.defaultSpace,
        clickedAt: Date.now(),
        matchedTabId: null,
        pendingPatch: {
          todo: `Review: ${info.linkText || info.linkUrl}`,
          targetTime: Date.now() + 30 * 60 * 1000 // +30m default
        }
      };
      pendingClicks.push(clickEntry);
      await browser.tabs.create({
        url: info.linkUrl,
        openerTabId: tab ? tab.id : undefined,
        active: false
      });
    }
  });
} catch (err) {
  console.warn("[ZenTab] Context menu registration warning:", err);
}

// ---------------------------------------------------------------------------
// Physical Tab Clustering in Zen Browser (Zero-LLM Heuristic Organizer)
// ---------------------------------------------------------------------------

async function clusterTabsInBrowser(mode = "referrer") {
  const currentWindowTabs = await browser.tabs.query({ currentWindow: true });
  const unpinned = currentWindowTabs.filter((t) => !t.pinned);
  const pinnedCount = currentWindowTabs.length - unpinned.length;

  const enriched = unpinned.map((t) => {
    const rec = tabRecords[String(t.id)] || {};
    return { tab: t, rec };
  });

  if (mode === "referrer") {
    // Sort by parent/origin domain + openerTabId, then by openedAt
    enriched.sort((a, b) => {
      const srcA = a.rec.provenance?.sourceUrl || a.rec.url || "";
      const srcB = b.rec.provenance?.sourceUrl || b.rec.url || "";
      if (srcA !== srcB) return srcA.localeCompare(srcB);
      return (a.rec.openedAt || 0) - (b.rec.openedAt || 0);
    });
  } else if (mode === "purpose") {
    enriched.sort((a, b) => {
      const catA = a.rec.purposeCategory || "General Exploration";
      const catB = b.rec.purposeCategory || "General Exploration";
      if (catA !== catB) return catA.localeCompare(catB);
      return (a.rec.openedAt || 0) - (b.rec.openedAt || 0);
    });
  } else if (mode === "targetTime") {
    enriched.sort((a, b) => {
      const tA = a.rec.targetTime || Number.MAX_SAFE_INTEGER;
      const tB = b.rec.targetTime || Number.MAX_SAFE_INTEGER;
      if (tA !== tB) return tA - tB;
      return (a.rec.openedAt || 0) - (b.rec.openedAt || 0);
    });
  } else if (mode === "openedAt") {
    enriched.sort((a, b) => (b.rec.openedAt || 0) - (a.rec.openedAt || 0));
  }

  for (let i = 0; i < enriched.length; i++) {
    const targetIndex = pinnedCount + i;
    try {
      await browser.tabs.move(enriched[i].tab.id, { index: targetIndex });
    } catch {
      // Ignore if tab cannot be moved
    }
  }
  return { movedCount: enriched.length, mode };
}

// ---------------------------------------------------------------------------
// Runtime Message Router (Content Scripts, Popup, Sidebar, Tutorial)
// ---------------------------------------------------------------------------

browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message || !message.type) return false;

  if (message.type === "RECORD_PENDING_CLICK") {
    const sourceTabId = sender.tab ? sender.tab.id : (message.sourceTabId || null);
    const parentRec = sourceTabId ? tabRecords[String(sourceTabId)] : null;
    const clickId = `clk-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

    const entry = {
      clickId,
      sourceTabId,
      targetUrl: message.targetUrl || "",
      normTargetUrl: normalizeUrl(message.targetUrl || ""),
      sourceUrl: message.sourceUrl || (sender.tab ? sender.tab.url : ""),
      sourceTitle: message.sourceTitle || (sender.tab ? sender.tab.title : ""),
      linkText: message.linkText || "",
      surroundingSnippet: message.surroundingSnippet || "",
      selectedText: message.selectedText || "",
      triggerType: message.triggerType || "ctrl+click",
      modifiers: message.modifiers || {},
      spaceHint: parentRec ? parentRec.spaceTag : settings.defaultSpace,
      clickedAt: Date.now(),
      matchedTabId: null,
      pendingPatch: null
    };

    pendingClicks.push(entry);
    sendResponse({
      ok: true,
      clickId,
      settings
    });
    return false;
  }

  if (message.type === "UPDATE_CLICK_ANNOTATION") {
    const { clickId, patch } = message;
    const entry = pendingClicks.find((c) => c.clickId === clickId);
    if (entry) {
      entry.pendingPatch = { ...(entry.pendingPatch || {}), ...patch };
      if (entry.matchedTabId && tabRecords[String(entry.matchedTabId)]) {
        const rec = tabRecords[String(entry.matchedTabId)];
        Object.assign(rec, patch, { lastUpdatedAt: Date.now() });
        if (patch.targetTime !== undefined) {
          scheduleTargetAlarm(rec.tabId, patch.targetTime, rec.title);
        }
        archiveRecordByUrl(rec);
        scheduleStorageSave();
        sendResponse({ ok: true, updatedTabId: rec.tabId });
        return false;
      }
    }
    sendResponse({ ok: true, queued: true });
    return false;
  }

  if (message.type === "GET_ALL_STATE") {
    commitActiveTabDuration();
    browser.tabs.query({ currentWindow: true }).then(async (openTabs) => {
      // Ensure every currently open tab has a synchronized record
      for (const t of openTabs) {
        if (!tabRecords[String(t.id)]) {
          await createOrUpdateTabRecord(t);
        } else {
          // Keep live tab index/title/pinned in sync
          const r = tabRecords[String(t.id)];
          r.index = t.index;
          r.pinned = Boolean(t.pinned);
          if (t.title && t.title !== "New Tab") r.title = t.title;
          if (t.url && t.url !== "about:blank") {
            r.url = t.url;
            r.domain = extractDomain(t.url);
          }
          if (t.favIconUrl) r.favIconUrl = t.favIconUrl;
        }
      }

      const activeTab = openTabs.find((t) => t.active) || openTabs[0] || null;
      sendResponse({
        ok: true,
        activeTabId: activeTab ? activeTab.id : null,
        records: tabRecords,
        settings
      });
    });
    return true; // Async response
  }

  if (message.type === "UPDATE_TAB_RECORD") {
    const { tabId, patch } = message;
    const key = String(tabId);
    if (tabRecords[key]) {
      if (patch.purposeCategory && patch.purposeCategory !== tabRecords[key].purposeCategory) {
        patch.userSetPurpose = true;
      }
      Object.assign(tabRecords[key], patch, { lastUpdatedAt: Date.now() });
      if (patch.targetTime !== undefined) {
        scheduleTargetAlarm(Number(tabId), patch.targetTime, tabRecords[key].title);
      }
      archiveRecordByUrl(tabRecords[key]);
      scheduleStorageSave();
      sendResponse({ ok: true, record: tabRecords[key] });
    } else {
      sendResponse({ ok: false, error: "Tab record not found" });
    }
    return false;
  }

  if (message.type === "UPDATE_SETTINGS") {
    settings = { ...settings, ...(message.patch || {}) };
    scheduleStorageSave();
    sendResponse({ ok: true, settings });
    return false;
  }

  if (message.type === "CLUSTER_TABS_IN_BROWSER") {
    clusterTabsInBrowser(message.mode || "referrer").then((res) => {
      sendResponse({ ok: true, ...res });
    });
    return true;
  }

  if (message.type === "OPEN_TUTORIAL") {
    const url = browser.runtime.getURL("onboarding/tutorial.html");
    browser.tabs.create({ url, active: true }).then((tab) => {
      sendResponse({ ok: true, tabId: tab.id });
    });
    return true;
  }

  if (message.type === "FOCUS_TAB") {
    const tabId = Number(message.tabId);
    browser.tabs.get(tabId).then(async (tab) => {
      await browser.tabs.update(tabId, { active: true });
      await browser.windows.update(tab.windowId, { focused: true });
      sendResponse({ ok: true });
    }).catch(() => sendResponse({ ok: false }));
    return true;
  }

  return false;
});

// ---------------------------------------------------------------------------
// Initialization & On-Install Interactive Tutorial Trigger
// ---------------------------------------------------------------------------

async function initializeExtension() {
  try {
    const stored = await browser.storage.local.get([
      STORAGE_KEYS.TAB_RECORDS,
      STORAGE_KEYS.URL_ARCHIVE,
      STORAGE_KEYS.SETTINGS
    ]);
    if (stored[STORAGE_KEYS.URL_ARCHIVE]) {
      urlArchive = stored[STORAGE_KEYS.URL_ARCHIVE];
    }
    if (stored[STORAGE_KEYS.SETTINGS]) {
      settings = { ...DEFAULT_SETTINGS, ...stored[STORAGE_KEYS.SETTINGS] };
    }
    const savedRecords = stored[STORAGE_KEYS.TAB_RECORDS] || {};

    // Reconcile against currently open tabs in Zen Browser
    const allTabs = await browser.tabs.query({});
    for (const tab of allTabs) {
      const key = String(tab.id);
      if (savedRecords[key] && savedRecords[key].url === tab.url) {
        tabRecords[key] = savedRecords[key];
      } else {
        await createOrUpdateTabRecord(tab);
      }
      if (tab.active) {
        currentActiveTabId = tab.id;
        currentActiveStartMs = Date.now();
      }
    }
    scheduleStorageSave();
  } catch (err) {
    console.error("[ZenTab] Initialization error:", err);
  }
}

browser.runtime.onInstalled.addListener(async (details) => {
  await initializeExtension();
  if (details.reason === "install") {
    // Open the interactive click-through tutorial automatically on first install!
    const tutorialUrl = browser.runtime.getURL("onboarding/tutorial.html?installed=1");
    await browser.tabs.create({ url: tutorialUrl, active: true });
  }
});

initializeExtension();
