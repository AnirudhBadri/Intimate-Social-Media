# ZenTab Provenance & Action Tracker (`zentab-provenance`)

A lightweight, zero-cloud-dependency **Mozilla Firefox / Zen Browser WebExtension** that captures rich **origin provenance** at the exact moment you `Ctrl+Click` (or Middle-Click) a link, maintains per-tab **Notes**, **To-Dos**, and **Target-Times**, and organizes your vertical tabs by **Referrer Lineage Tree**, **Purpose**, or **Session Burst**.

---

## ✨ Key Features (MVP v1.0 — 100% Local & Zero-LLM Cost)

1. **Instant `Ctrl+Click` & Middle-Click Provenance Capture**
   - Intercepts link opens in the capture phase (`content/provenance_capture.js`) and correlates them with `browser.tabs.onCreated` and `browser.webNavigation.onCreatedNavigationTarget`.
   - Records **when** the tab was opened (`openedAt`), **cumulative active viewing time** (`activeDurationMs`), **which parent page** spawned it (`sourceUrl`, `sourceTitle`, `openerTabId`), the **clicked anchor text** (`linkText`), the **surrounding DOM snippet** (e.g., GitHub repo description, Hacker News subtext, or article paragraph), **highlighted selection text**, and **Firefox Container / Zen Workspace label**.
2. **4.5-Second On-Page Zen Micro-HUD Toast**
   - Right when you `Ctrl+Click` a link to read later, a sleek dark-glass toast appears in the bottom-right corner of your current page for 4.5 seconds.
   - Press <kbd>T</kbd> to jot a quick **To-Do / Note** or press <kbd>1</kbd>–<kbd>4</kbd> (`+30m`, `+2h`, `Tonight 9pm`, `Tomorrow`) to assign a **Target-Time** to the newly spawned background tab without ever leaving the hub page you are reading.
3. **Per-Tab Note, To-Do & Target-Time Alarms (`Alt+Shift+Z`)**
   - Inspect any tab's full provenance lineage (including a **Jump to Parent Tab** button if the opener tab is still open).
   - Add a **To-Do**, **Target-Time** (triggers a desktop notification via `browser.alarms` that focuses the tab when clicked), **Zen Space tag**, **Purpose Category**, and **Scratchpad Note**.
   - **URL Archive Persistence:** Notes, To-Dos, and Provenance are automatically cached by normalized URL so closing and reopening a tab restores its context.
4. **Provenance Tree, Deterministic Grouping & 1-Click Zen Tab Sorting**
   - Group all open tabs by **Origin / Referrer Page**, **Purpose Category** (*AI Safety & SecOps*, *Code & Repositories*, *Research & Papers*, *Docs & Reference*, *Cloud & Billing Admin*), **To-Do & Target-Time Queue**, **15-Minute Open-Time Burst**, or **Zen Space / Container**.
   - Click **⇄ Sort Zen Tabs** to physically reorder unpinned tabs in Zen Browser's vertical sidebar using `browser.tabs.move()`.
5. **1-Click Calendar Focus Block (`.ics` / Google Calendar) & Antigravity Markdown Export**
   - Bundle all tabs with an active To-Do or Target-Time into a single **Google Calendar Focus Block** or downloadable `.ics` invite, or copy a structured Markdown checklist with full provenance links.
6. **On-Install Interactive Click-Through Tutorial**
   - Automatically launches `onboarding/tutorial.html` upon installation (and is accessible anytime via the **? Tutorial** button in the popup), featuring a **live `Ctrl+Click` sandbox** where you can test DOM snippet extraction and the Micro-HUD in real time.

---

## 🚀 Quick Start: Loading in Zen Browser (or Firefox)

1. Open **Zen Browser** and navigate to:
   ```text
   about:debugging#/runtime/this-firefox
   ```
2. Click **Load Temporary Add-on…**
3. Select the file:
   ```text
   extension/manifest.json
   ```
4. **Automatic Onboarding:** As soon as the extension loads, the **5-Step Interactive Click-Through Tutorial** will open in a new tab. Go to **Step 2** in the tutorial and `Ctrl+Click` one of the mock GitHub Star repository links to see the live provenance capture and bottom-right Micro-HUD toast!

### Keyboard Shortcuts
| Shortcut | Action |
| :--- | :--- |
| <kbd>Alt+Shift+Z</kbd> | Open **ZenTab Provenance Popup** (Active Tab Inspector + Provenance Tree) |
| <kbd>Alt+Shift+X</kbd> | Toggle **ZenTab Provenance Sidebar** |
| <kbd>Ctrl+Click</kbd> / Middle-Click | Open link in background tab + trigger **On-Page Micro-HUD Toast** |
| <kbd>T</kbd> *(while Micro-HUD is visible)* | Focus the quick To-Do input on the parent page |
| <kbd>1</kbd> / <kbd>2</kbd> / <kbd>3</kbd> / <kbd>4</kbd> *(while Micro-HUD is visible)* | Set Target-Time (`+30m`, `+2h`, `Tonight 9pm`, `Tomorrow 10am`) |

---

## 📂 Repository Structure

```text
proud-chandrasekhar/
├── README.md                           # Installation, features, ecosystem & timeline guide
├── docs/
│   └── ARCHITECTURE.md                 # Deep-dive system architecture + Future Cheap LLM/MCP Blueprint
└── extension/                          # Mozilla / Zen Browser WebExtension
    ├── manifest.json                   # WebExtension Manifest (MV2 for broad Gecko/Zen compatibility)
    ├── icons/
    │   └── icon.svg                    # Vector lineage icon
    ├── background/
    │   └── background.js               # 3-Layer Provenance Correlation Engine, storage & alarms
    ├── content/
    │   ├── provenance_capture.js       # Capture-phase Ctrl+Click DOM interceptor & Micro-HUD
    │   └── micro_hud.css               # Dark-glass bottom-right Micro-HUD styles
    ├── ui/
    │   ├── panel.html                  # Popup & Sidebar layout
    │   ├── panel.css                   # Zen dark-glass stylesheet
    │   └── panel.js                    # Inspector, Provenance Tree, Tab Sorter & Calendar/MD Exporter
    └── onboarding/
        ├── tutorial.html               # 5-step on-install interactive click-through tutorial
        ├── tutorial.css                # Onboarding layout & animations
        └── tutorial.js                 # Stepper controller & live Ctrl+Click telemetry sandbox
```

---

## 🧭 Open-Source Repositories & Similar Products Comparison

| Project / Codebase | Repository & License | Core Strength | How ZenTab Provenance Differs / Borrows |
| :--- | :--- | :--- | :--- |
| **Tree Style Tab (TST)** | [`piroor/treestyletab`](https://github.com/piroor/treestyletab) (MPL-2.0) | Tracks `openerTabId` parent-child hierarchy in a sidebar tree. | TST only tracks tab hierarchy; it does not capture **DOM snippets**, **clicked anchor text**, **per-tab Notes/To-Dos**, or **Target-Time alarms**. We borrow TST's `openerTabId` + `webNavigation` correlation pattern. |
| **Sidebery** | [`mbnuqw/sidebery`](https://github.com/mbnuqw/sidebery) (MIT) | Full-featured vertical tabs, panels, containers, and snapshots. | Sidebery creates a heavy second sidebar that clashes with Zen Browser's native vertical sidebar. ZenTab is popup-first (`Alt+Shift+Z`) + on-page Micro-HUD. |
| **Tab Stash** | [`josh-berry/tab-stash`](https://github.com/josh-berry/tab-stash) (MPL-2.0) | Saves batches of open tabs into structured bookmark folders. | Great for archiving closed tabs, but lacks live provenance tracking and scheduled Target-Time notifications for *open* tabs. |
| **Tab Session Manager** | [`sienori/Tab-Session-Manager`](https://github.com/sienori/Tab-Session-Manager) (MPL-2.0) | Cross-restart session persistence using `browser.storage.local`. | We borrow its normalized-URL archive fallback (`urlArchive`) so tab notes and provenance survive browser restarts. |
| **Zen Browser Desktop** | [`zen-browser/desktop`](https://github.com/zen-browser/desktop) (MPL-2.0) | Native Firefox fork with Workspaces (`ZenWorkspaces.mjs`), Split Views, and Compact Mode. | ZenTab reads `contextualIdentities` (`cookieStoreId`) and sorts unpinned tabs directly inside Zen's native vertical tab bar via `browser.tabs.move()`. |

---

## ⏱️ Difficulty & Engineering Timeline Estimate

| Phase | Milestone | Difficulty | Time Estimate | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Phase 1** | **3-Layer Provenance Engine** (`provenance_capture.js` + `background.js` correlation + `storage.local` + URL archive) | **3 / 5** (Medium) | **3–4 hrs** | ✅ **Completed in MVP** |
| **Phase 2** | **On-Page Micro-HUD + Popup/Sidebar UI + On-Install Click-Through Tutorial** (`ui/` + `onboarding/`) | **3 / 5** (Medium) | **4–5 hrs** | ✅ **Completed in MVP** |
| **Phase 3** | **Deterministic Clustering, Physical Zen Tab Sorting & `.ics`/GCal/Markdown Exports** | **2.5 / 5** (Low–Med) | **2 hrs** | ✅ **Completed in MVP** |
| **Phase 4 (Future)** | **Ultra-Cheap LLM Batching (`gemini-2.5-flash-lite` / Ollama) + Local MCP Bridge** (Calendar MCP + Antigravity push) | **3 / 5** (Medium) | **2–3 hrs** | 📄 **Documented in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)** |
