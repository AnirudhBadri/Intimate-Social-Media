/**
 * ZenTab Provenance — Interactive Product Tour Controller (tutorial.js)
 *
 * Drives the 5-step Bento tour, Live Ctrl+Click Sandbox, Interactive SVG Radial
 * Target-Time Simulator, and Embedded Live Popup Preview Drawer.
 */

(function () {
  const slides = Array.from(document.querySelectorAll(".tut-slide"));
  const stepDots = Array.from(document.querySelectorAll(".step-dot"));
  const prevStepBtn = document.getElementById("prevStepBtn");
  const nextStepBtn = document.getElementById("nextStepBtn");
  const stepCounterText = document.getElementById("stepCounterText");

  // Slide 2 Sandbox Elements
  const simulateCtrlClickBtn = document.getElementById("simulateCtrlClickBtn");
  const sandboxStatusBadge = document.getElementById("sandboxStatusBadge");
  const sandboxPayloadOutput = document.getElementById("sandboxPayloadOutput");
  const sandboxLinks = document.querySelectorAll(".sandbox-link");

  // Slide 3 Radial Simulator Elements
  const simRingArc = document.getElementById("simRingArc");
  const simRingVal = document.getElementById("simRingVal");
  const simRingSub = document.getElementById("simRingSub");
  const simStatusDesc = document.getElementById("simStatusDesc");
  const simPresetBtns = document.querySelectorAll(".sim-preset-btn");

  // Slide 5 Launchpad & Live Preview Modal
  const tutHudToggle = document.getElementById("tutHudToggle");
  const tutDefaultSpace = document.getElementById("tutDefaultSpace");
  const toggleLivePopupModalBtn = document.getElementById("toggleLivePopupModalBtn");
  const livePopupModal = document.getElementById("livePopupModal");
  const closePopupModalBtn = document.getElementById("closePopupModalBtn");

  let currentStep = 0;
  let lastCapturedPayload = null;

  function goToStep(index) {
    currentStep = Math.max(0, Math.min(slides.length - 1, index));

    slides.forEach((slide, idx) => {
      slide.classList.toggle("active", idx === currentStep);
    });

    stepDots.forEach((dot, idx) => {
      dot.classList.toggle("active", idx === currentStep);
    });

    prevStepBtn.disabled = currentStep === 0;
    const padStep = String(currentStep + 1).padStart(2, "0");
    stepCounterText.textContent = `Step ${padStep} of 05 · Use ← → Arrow Keys`;

    if (currentStep === slides.length - 1) {
      nextStepBtn.textContent = "Finish & Start Browsing ✓";
    } else {
      nextStepBtn.textContent = "Next Step →";
    }
  }

  prevStepBtn.addEventListener("click", () => goToStep(currentStep - 1));

  nextStepBtn.addEventListener("click", async () => {
    if (currentStep < slides.length - 1) {
      goToStep(currentStep + 1);
      return;
    }

    if (typeof browser !== "undefined" && browser.runtime && browser.runtime.sendMessage) {
      try {
        await browser.runtime.sendMessage({
          type: "UPDATE_SETTINGS",
          patch: {
            enableMicroHud: tutHudToggle.checked,
            defaultSpace: tutDefaultSpace.value.trim() || "AI Safety Lab"
          }
        });
      } catch {
        // Standalone mode
      }
    }

    nextStepBtn.textContent = "✦ Workspace Ready! Press Alt+Shift+Z Anytime";
    setTimeout(() => {
      if (typeof browser !== "undefined" && browser.tabs && browser.tabs.getCurrent) {
        browser.tabs.getCurrent().then((tab) => {
          if (tab && tab.id) browser.tabs.remove(tab.id);
        }).catch(() => {});
      }
    }, 1200);
  });

  stepDots.forEach((dot) => {
    dot.addEventListener("click", () => {
      const target = Number(dot.getAttribute("data-step"));
      goToStep(target);
    });
  });

  window.addEventListener("keydown", (e) => {
    const tag = document.activeElement ? document.activeElement.tagName.toLowerCase() : "";
    if (tag === "input" || tag === "textarea") return;
    if (e.key === "Escape" && livePopupModal && !livePopupModal.hidden) {
      livePopupModal.hidden = true;
      return;
    }
    if (e.key === "ArrowRight") goToStep(currentStep + 1);
    if (e.key === "ArrowLeft") goToStep(currentStep - 1);
  });

  // -------------------------------------------------------------------------
  // Slide 2: Live Ctrl+Click Sandbox
  // -------------------------------------------------------------------------

  sandboxLinks.forEach((link) => {
    link.addEventListener("click", (e) => {
      // Keep tutorial open while allowing provenance_capture.js capture-phase listener to fire
      e.preventDefault();
      if (e.ctrlKey || e.metaKey) {
        if (typeof browser !== "undefined" && browser.tabs && browser.tabs.create) {
          browser.tabs.create({ url: link.href, active: false }).catch(() => {});
        }
      }
    });
  });

  simulateCtrlClickBtn.addEventListener("click", () => {
    const targetLink = sandboxLinks[0];
    if (!targetLink) return;
    const simulatedEvent = new MouseEvent("click", {
      bubbles: true,
      cancelable: true,
      ctrlKey: true,
      button: 0
    });
    targetLink.dispatchEvent(simulatedEvent);
  });

  window.addEventListener("zentab:provenance-captured", (e) => {
    lastCapturedPayload = e.detail;
    sandboxStatusBadge.textContent = "✦ Provenance Captured + HUD Active";
    sandboxStatusBadge.className = "status-pill captured";
    sandboxPayloadOutput.textContent = JSON.stringify(
      {
        capturedAt: new Date().toLocaleTimeString(),
        triggerType: lastCapturedPayload.triggerType,
        sourceTitle: lastCapturedPayload.sourceTitle,
        linkText: lastCapturedPayload.linkText,
        targetUrl: lastCapturedPayload.targetUrl,
        surroundingSnippet: lastCapturedPayload.surroundingSnippet
      },
      null,
      2
    );
  });

  window.addEventListener("zentab:annotation-updated", (e) => {
    const { patch } = e.detail || {};
    const merged = {
      ...(lastCapturedPayload || {}),
      liveMicroHudAnnotation: {
        todo: patch?.todo || "(unchanged)",
        targetTime: patch?.targetTime ? new Date(patch.targetTime).toLocaleString() : "(unchanged)"
      }
    };
    sandboxStatusBadge.textContent = "✓ Micro-HUD To-Do & Target Saved!";
    sandboxPayloadOutput.textContent = JSON.stringify(merged, null, 2);
  });

  // -------------------------------------------------------------------------
  // Slide 3: Interactive Radial Target-Time Simulator
  // -------------------------------------------------------------------------

  const SIM_STATES = {
    "30m": {
      offset: "65",
      color: "#F59E0B",
      val: "30m",
      sub: "DUE SOON",
      desc: "⏰ <strong>Amber State (&lt;60m):</strong> Fires a desktop notification via <code>browser.alarms</code> when time is up; clicking the notification focuses the tab."
    },
    "2h": {
      offset: "35",
      color: "#22D3EE",
      val: "2h",
      sub: "SCHEDULED",
      desc: "🌐 <strong>Cyan State (&gt;60m):</strong> Scheduled for a deep-focus reading block and ready for 1-click Google Calendar / .ICS export."
    },
    overdue: {
      offset: "0",
      color: "#F43F5E",
      val: "-14m",
      sub: "OVERDUE",
      desc: "🚨 <strong>Coral Rose State (Overdue):</strong> Automatically floats to the top of your <em>To-Do &amp; Target Queue</em> in the Lineage Tree."
    },
    done: {
      offset: "0",
      color: "#10B981",
      val: "DONE",
      sub: "COMPLETE",
      desc: "✓ <strong>Emerald State (Completed):</strong> Archived in your persistent URL index so your notes remain searchable even if you close the tab."
    }
  };

  simPresetBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      simPresetBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      const key = btn.getAttribute("data-sim");
      const cfg = SIM_STATES[key];
      if (!cfg) return;
      simRingArc.style.strokeDashoffset = cfg.offset;
      simRingArc.style.stroke = cfg.color;
      simRingVal.textContent = cfg.val;
      simRingSub.textContent = cfg.sub;
      simStatusDesc.innerHTML = cfg.desc;
    });
  });

  // -------------------------------------------------------------------------
  // Slide 5: Live Inspector Preview Drawer
  // -------------------------------------------------------------------------

  if (toggleLivePopupModalBtn && livePopupModal) {
    toggleLivePopupModalBtn.addEventListener("click", () => {
      livePopupModal.hidden = false;
    });
  }

  if (closePopupModalBtn && livePopupModal) {
    closePopupModalBtn.addEventListener("click", () => {
      livePopupModal.hidden = true;
    });
    livePopupModal.addEventListener("click", (e) => {
      if (e.target === livePopupModal) livePopupModal.hidden = true;
    });
  }
})();
