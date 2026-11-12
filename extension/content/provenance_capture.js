/**
 * ZenTab Provenance & Action Tracker — Content Script (provenance_capture.js)
 *
 * Captures rich link provenance at the exact moment of Ctrl+Click, Cmd+Click,
 * Middle-Click, or target="_blank" link activation, and displays a sleek
 * 4.5-second Zen Micro-HUD Toast on the parent page for instant To-Do / Target-Time tagging.
 */

(function () {
  if (window.__zentabProvenanceInjected) return;
  window.__zentabProvenanceInjected = true;

  let lastCapturedKey = "";
  let lastCapturedTime = 0;
  let activeHudCleanup = null;

  /**
   * Finds the anchor element from a click/mousedown event, supporting Shadow DOM.
   */
  function findAnchorFromEvent(event) {
    if (typeof event.composedPath === "function") {
      const path = event.composedPath();
      for (const node of path) {
        if (node && node.tagName && node.tagName.toLowerCase() === "a" && node.href) {
          return node;
        }
      }
    }
    return event.target && event.target.closest ? event.target.closest("a[href]") : null;
  }

  /**
   * Extracts clean, human-readable surrounding context (e.g., GitHub repo card description,
   * HackerNews comment/subtext, article paragraph, or nearest section heading).
   */
  function extractSurroundingSnippet(anchor, linkText) {
    try {
      const containerSelectors = [
        "li",
        "article",
        "tr",
        "[role='listitem']",
        "[data-testid]",
        ".Box-row",
        ".col-12",
        ".card",
        ".post",
        ".item",
        "p",
        "blockquote",
        "section",
        "div"
      ];

      let bestText = "";
      let curr = anchor.parentElement;
      let depth = 0;

      while (curr && curr !== document.body && depth < 6) {
        const raw = (curr.innerText || curr.textContent || "")
          .replace(/\s+/g, " ")
          .trim();

        // Remove the link text itself so the snippet highlights the surrounding context
        const cleaned = raw
          .replace(linkText, "")
          .replace(/\b(Star|Starred|Fork|Watch|Sponsor)\b/gi, "")
          .replace(/\s+/g, " ")
          .trim();

        if (cleaned.length >= 20 && cleaned.length <= 360) {
          bestText = cleaned;
          break;
        }
        if (cleaned.length > 360 && !bestText) {
          bestText = cleaned.slice(0, 280) + "…";
          break;
        }
        curr = curr.parentElement;
        depth++;
      }

      // Also check nearest preceding heading (h1, h2, h3) for section context
      let headingText = "";
      const section = anchor.closest("section, article, main, div");
      if (section) {
        const heading = section.querySelector("h1, h2, h3, h4");
        if (heading) {
          const h = (heading.innerText || "").replace(/\s+/g, " ").trim();
          if (h && h !== linkText && h.length < 100) {
            headingText = h;
          }
        }
      }

      if (headingText && bestText && !bestText.includes(headingText)) {
        return `[${headingText}] ${bestText}`.slice(0, 300);
      }
      return bestText || headingText || "";
    } catch {
      return "";
    }
  }

  function computePresetTimestamp(presetKey) {
    const now = new Date();
    if (presetKey === "30m") {
      return Date.now() + 30 * 60 * 1000;
    }
    if (presetKey === "2h") {
      return Date.now() + 2 * 60 * 60 * 1000;
    }
    if (presetKey === "tonight") {
      const tonight = new Date(now);
      tonight.setHours(21, 0, 0, 0);
      if (tonight.getTime() <= Date.now()) {
        tonight.setTime(Date.now() + 3 * 60 * 60 * 1000);
      }
      return tonight.getTime();
    }
    if (presetKey === "tomorrow") {
      const tom = new Date(now);
      tom.setDate(tom.getDate() + 1);
      tom.setHours(10, 0, 0, 0);
      return tom.getTime();
    }
    return null;
  }

  /**
   * Renders the non-intrusive bottom-right Micro-HUD toast on the parent page
   * right after the user Ctrl+Clicks or Middle-Clicks a link.
   */
  function showMicroHudToast(clickId, linkText, targetUrl, triggerType, durationMs = 4500) {
    if (activeHudCleanup) {
      activeHudCleanup();
    }

    const host = document.createElement("div");
    host.id = "zentab-micro-hud-root";
    host.className = "zentab-hud-card";

    const shortLabel = (linkText || targetUrl || "New Tab").slice(0, 56);
    const badgeLabel = triggerType === "middle-click" ? "Middle-Click" : "Ctrl+Click";

    host.innerHTML = `
      <div class="zentab-hud-header">
        <span class="zentab-hud-dot"></span>
        <span class="zentab-hud-badge">${badgeLabel}</span>
        <span class="zentab-hud-title" title="${targetUrl.replace(/"/g, "&quot;")}">${shortLabel}</span>
        <button type="button" class="zentab-hud-close" aria-label="Dismiss">×</button>
      </div>
      <div class="zentab-hud-row">
        <input
          type="text"
          class="zentab-hud-input"
          placeholder="Tap [T] to attach a To-Do or context note…"
        />
        <button type="button" class="zentab-hud-save-btn">Save ↵</button>
      </div>
      <div class="zentab-hud-pills">
        <span class="zentab-hud-pill-label">Target:</span>
        <button type="button" class="zentab-hud-pill" data-preset="30m"><kbd>1</kbd> +30m</button>
        <button type="button" class="zentab-hud-pill" data-preset="2h"><kbd>2</kbd> +2h</button>
        <button type="button" class="zentab-hud-pill" data-preset="tonight"><kbd>3</kbd> Tonight</button>
        <button type="button" class="zentab-hud-pill" data-preset="tomorrow"><kbd>4</kbd> Tomorrow</button>
      </div>
      <div class="zentab-hud-status" hidden></div>
      <div class="zentab-hud-timer-track">
        <div class="zentab-hud-timer-bar" style="animation-duration: ${durationMs}ms !important;"></div>
      </div>
    `;

    document.documentElement.appendChild(host);

    const inputEl = host.querySelector(".zentab-hud-input");
    const saveBtn = host.querySelector(".zentab-hud-save-btn");
    const closeBtn = host.querySelector(".zentab-hud-close");
    const statusEl = host.querySelector(".zentab-hud-status");
    const pills = host.querySelectorAll(".zentab-hud-pill");

    let timer = null;
    let isInteracting = false;

    function startDismissTimer(ms = durationMs) {
      if (timer) clearTimeout(timer);
      timer = setTimeout(() => {
        if (!isInteracting) cleanup();
      }, ms);
    }

    function showConfirmation(text) {
      statusEl.textContent = text;
      statusEl.hidden = false;
      isInteracting = false;
      startDismissTimer(1400);
    }

    function sendAnnotationPatch(patch, confirmMessage) {
      if (typeof browser !== "undefined" && browser.runtime && browser.runtime.sendMessage) {
        browser.runtime.sendMessage({
          type: "UPDATE_CLICK_ANNOTATION",
          clickId,
          patch
        }).catch(() => {});
      }
      window.dispatchEvent(new CustomEvent("zentab:annotation-updated", {
        detail: { clickId, patch }
      }));
      showConfirmation(confirmMessage);
    }

    function commitTodoInput() {
      const val = inputEl.value.trim();
      if (!val) return;
      sendAnnotationPatch({ todo: val }, `✓ Saved To-Do: "${val}"`);
    }

    saveBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      commitTodoInput();
    });

    inputEl.addEventListener("focus", () => {
      isInteracting = true;
      if (timer) clearTimeout(timer);
    });

    inputEl.addEventListener("keydown", (e) => {
      e.stopPropagation();
      if (e.key === "Enter") {
        e.preventDefault();
        commitTodoInput();
      } else if (e.key === "Escape") {
        e.preventDefault();
        cleanup();
      }
    });

    pills.forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        pills.forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        const preset = btn.getAttribute("data-preset");
        const targetTime = computePresetTimestamp(preset);
        const todoVal = inputEl.value.trim();
        const patch = { targetTime };
        if (todoVal) patch.todo = todoVal;
        sendAnnotationPatch(patch, `⏰ Target set (${btn.textContent.replace(/\[\d\]\s*/, "")})`);
      });
    });

    host.addEventListener("mouseenter", () => {
      isInteracting = true;
      if (timer) clearTimeout(timer);
    });

    host.addEventListener("mouseleave", () => {
      if (document.activeElement !== inputEl) {
        isInteracting = false;
        startDismissTimer(2200);
      }
    });

    closeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      cleanup();
    });

    // Global keyboard shortcut while HUD is visible (if user isn't typing in another field)
    function onWindowKeyDown(e) {
      const activeTag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
      const isEditable =
        activeTag === "input" ||
        activeTag === "textarea" ||
        (document.activeElement && document.activeElement.isContentEditable);

      if (isEditable) return;

      if (e.key === "t" || e.key === "T") {
        e.preventDefault();
        isInteracting = true;
        inputEl.focus();
      } else if (["1", "2", "3", "4"].includes(e.key)) {
        const idx = Number(e.key) - 1;
        if (pills[idx]) {
          e.preventDefault();
          pills[idx].click();
        }
      }
    }

    window.addEventListener("keydown", onWindowKeyDown, true);

    function cleanup() {
      if (timer) clearTimeout(timer);
      window.removeEventListener("keydown", onWindowKeyDown, true);
      if (host && host.parentNode) {
        host.parentNode.removeChild(host);
      }
      if (activeHudCleanup === cleanup) {
        activeHudCleanup = null;
      }
    }

    activeHudCleanup = cleanup;
    startDismissTimer(durationMs);
  }

  /**
   * Core handler for link clicks that open a new tab.
   */
  function handlePotentialNewTabLink(event) {
    const anchor = findAnchorFromEvent(event);
    if (!anchor || !anchor.href) return;

    const href = anchor.href;
    if (href.startsWith("javascript:") || href === "#") return;

    const isCtrlOrCmd = Boolean(event.ctrlKey || event.metaKey);
    const isMiddleClick = event.button === 1;
    const isShiftClick = Boolean(event.shiftKey && event.button === 0);
    const isTargetBlank = anchor.target === "_blank" && event.button === 0;

    if (!isCtrlOrCmd && !isMiddleClick && !isShiftClick && !isTargetBlank) {
      return;
    }

    // Deduplicate mousedown + click/auxclick for the same interaction within 450ms
    const dedupKey = `${href}|${event.button}|${isCtrlOrCmd}`;
    const now = Date.now();
    if (dedupKey === lastCapturedKey && now - lastCapturedTime < 450) {
      return;
    }
    lastCapturedKey = dedupKey;
    lastCapturedTime = now;

    const linkText = (
      anchor.innerText ||
      anchor.getAttribute("aria-label") ||
      anchor.getAttribute("title") ||
      anchor.textContent ||
      ""
    )
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 160);

    const surroundingSnippet = extractSurroundingSnippet(anchor, linkText);
    const selectedText = (window.getSelection ? window.getSelection().toString() : "")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 240);

    const triggerType = isCtrlOrCmd
      ? "ctrl+click"
      : isMiddleClick
        ? "middle-click"
        : isShiftClick
          ? "shift+click"
          : "target-blank";

    const payload = {
      type: "RECORD_PENDING_CLICK",
      targetUrl: href,
      sourceUrl: window.location.href,
      sourceTitle: document.title || window.location.hostname,
      linkText: linkText || href,
      surroundingSnippet,
      selectedText,
      triggerType,
      modifiers: {
        ctrlKey: Boolean(event.ctrlKey),
        metaKey: Boolean(event.metaKey),
        shiftKey: Boolean(event.shiftKey),
        altKey: Boolean(event.altKey),
        button: event.button
      }
    };

    // Dispatch local DOM event so the interactive tutorial sandbox can react immediately
    window.dispatchEvent(new CustomEvent("zentab:provenance-captured", { detail: payload }));

    if (typeof browser !== "undefined" && browser.runtime && browser.runtime.sendMessage) {
      browser.runtime
        .sendMessage(payload)
        .then((res) => {
          if (res && res.ok) {
            const enableHud = res.settings ? res.settings.enableMicroHud !== false : true;
            const hudMs = res.settings && res.settings.hudDurationMs ? res.settings.hudDurationMs : 4500;
            if (enableHud) {
              showMicroHudToast(res.clickId, payload.linkText, payload.targetUrl, triggerType, hudMs);
            }
          }
        })
        .catch(() => {
          // Fallback if background is restarting or in standalone preview
          showMicroHudToast(`local-${Date.now()}`, payload.linkText, payload.targetUrl, triggerType, 4500);
        });
    } else {
      showMicroHudToast(`local-${Date.now()}`, payload.linkText, payload.targetUrl, triggerType, 4500);
    }
  }

  // Listen in capture phase so SPA routers cannot block provenance capture
  window.addEventListener("mousedown", handlePotentialNewTabLink, true);
  window.addEventListener("auxclick", handlePotentialNewTabLink, true);
  window.addEventListener("click", handlePotentialNewTabLink, true);
})();
