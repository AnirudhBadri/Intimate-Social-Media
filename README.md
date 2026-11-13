# The Den: Intimate Social Media

> *முகநக நட்பது நட்பன்று நெஞ்சத்து*  
> *அகநக நட்பது நட்பு.*  
> — **திருக்குறள் 784 (Tirukkural 784)**  
> *(Friendship is not a pleasant smile performed upon the face; true friendship is that which makes the heart within rejoice.)*

---

> [!WARNING]
> **Work-in-Progress & Prototype Notice:**  
> **The Den is an experimental prototype and design exploration.** Most features described in this document are currently either in-progress proofs-of-concept or architectural milestones on the roadmap.  
> 
> This README documents the **core ethos, design philosophy, and system invariants** of the project—the antidote to algorithmic broadcast feeds and audience capture. For an honest breakdown of what is currently working in the prototype versus what is planned, see the [Feature Status & Roadmap](#feature-status--roadmap) section below.

---

### The Premise: We Built Broadcast Engines and Called Them Friends

Every major social network is an algorithmic strip-mine.

They took an evolutionary creature designed to maintain a small circle of high-trust bonds, shoved a megaphone in its hands, dropped it into an arena with eight billion strangers, and measured its worth by how much noise it could provoke before midnight.

When you broadcast to an audience:
1. **Context collapses into a performance:** You cannot speak the same way to your mother, your old college roommate, your manager, and an anonymous stranger looking for blood in quote-tweets. When all four sit in the same room, honest conversation dies; you produce sanitized PR or provocative slop.
2. **Conversation becomes debt:** A red notification badge is a digital subpoena. Read receipts and unread counters turn casual human contact into an administrative backlog of guilt.
3. **The feed rewards spectacle over presence:** The algorithm does not care if you had an honest 2 AM conversation with your best friend. It cares whether your post made five hundred strangers angry enough to scroll for another twenty minutes.

#### The Brutal Flipside of the Broadcast Age

The downstream consequences of this design aren't just annoying quirks—they systematically dismantle real human connection:

- **People Are Profoundly Lonely (AI Stand-ins are the Consequence):** Beneath the endless stream of notifications, likes, and group chats, people are quietly, deeply lonely. Loneliness is the disease; turning to synthetic AI companions, chatbot stand-ins, and parasocial loops is just a desperate attempt to patch the void. People aren't enamored by bots because machines are great conversationalists; they accept them because genuine human presence has become almost impossible to find in the digital noise.
- **The Effort Asymmetry (Why People Stop Reaching Out):** In almost every friendship, one person is usually the one putting in the effort to reach out first. But after a few delayed replies or getting left on "seen," they start feeling like an annoying bother, a nuisance, or simply forgotten. Eventually, exhausted by the silence and feeling unreciprocated, they quietly stop initiating—and the friendship slowly evaporates into nothingness.
- **The Surface-Level "Catch-Up" Trap:** On the rare occasion you finally jump on a call or meet up, 80% of the time is burned merely catching up on factual logistics: *"Where are you living now? How's work? Did you change teams?"* You run out of time before ever reaching the deep, substantive core of what either of you actually cares about.

**The Den** is an experiment in the opposite direction. It is a standalone, bounded digital sanctuary built on three immovable boundaries.

---

### The Three Invariants

```
+---------------------------------------------------------------------------------------+
|                                  THE DEN INVARIANTS                                   |
+---------------------------------------------------------------------------------------+
| 1. HARD DUNBAR CEILING (N <= 15) :: Mathematically blocked at 15. No audience to farm.|
| 2. AMBIENT TRACES OVER SPECS      :: Presence through everyday life, not fake text.   |
| 3. ZERO-DEBT RECIPROCITY         :: Embers, shared hearths, and asynchronous grace.   |
+---------------------------------------------------------------------------------------+
```

#### 1. The Hard Dunbar Boundary ($N \le 15$)
A Den has a hard, mathematical ceiling of fifteen people. Not as a soft guideline, but as an engine assertion:
```python
if len(self.users) >= self.dunbar_cap:  # dunbar_cap = 15
    return {"success": False, "error": "Dunbar Limit Reached: Cannot exceed 15 members."}
```
If you want to add a sixteenth person, someone has to leave or you build another Den. This single constraint kills audience capture at the root: there is no virality, no follower count, and no reason to perform.

#### 2. Keeping in Touch Shouldn't Be So Hard: Ambient Activity Traces

Remember how you kept in touch as kids or in college? You didn't schedule a 30-minute sync two weeks out on Google Calendar. You just walked into your friend's dorm room or living room, looked at what they were up to—what game was running, what record was spinning, what book was open on their desk—and you asked them about it right then and there.

Recreating that effortless, organic connection for busy adults is the entire point.

You shouldn't have to write a performative status update to prove you're alive. In The Den, presence is shared through passive activity traces:
- What you're actually listening to right now (Spotify real-time stream).
- What you watched last night and gave three stars to (Letterboxd logs).
- What code you actually committed to a repository (GitHub activity traces).
- What room in the 3D living room your avatar is idling in.

These traces remove the terrifying inertia of the cold opener. Asking *"Hey, how have you been?"* demands a 500-word life summary that neither of you has the energy to write. But seeing that your friend just logged an obscure 70s movie or is listening to an album you both loved ten years ago gives you an immediate, low-stakes reason to reach out:
> *"Wait, why are you listening to Loveless at 2 PM on a Tuesday?"*  
> *"Is that film actually good or did you suffer through it?"*

It turns reaching out from an administrative chore back into a casual, organic nudge.

#### 3. Zero-Debt Presence
The biggest friction in modern messaging is the asymmetry of reply obligations:
- **Embers:** Send a transient warmth ping to a friend's hearth. It leaves no unread counter, expects no reply, and creates no administrative guilt.
- **Mutual Lore Consecration:** Inside jokes don't become permanent artifacts on the wall because one person posted them; they require multi-party consensus to be consecrated into the space's permanent history.
- **Asynchronous Slow Games:** One board, one turn every few days. The game moves at the pace of human life, not push notifications.
- **Acoustic Corner Booth:** A private 1-on-1 audio sanctuary for long, quiet talks without a broadcast feed.

---

### Architectural Choice: "There's Already an App for That"

We refuse to build another proprietary app where you have to manually enter your life into a blank box.

You already emit rich behavioral traces every single day as you move through your digital life: Spotify songs, Letterboxd diary entries, GitHub commits, Steam playtime, e-reader highlights, and paper bookmarks.

The tragedy of Web 2.0 is that **none of this data actually benefits you or your relationships**:
- Centralized platforms hoard your activity traces in corporate silos to build ad-targeting dossiers and sell you stuff you don't need.
- You get zero utility from your own digital trail beyond a yearly "Wrapped" marketing infographic.

With modern APIs, webhooks, and local AI pipelines, a modest amount of technical awareness lets you **reclaim your own data and selectively pipe it to your sovereign Dens**:
- **Your College Crew Den:** Receives your Spotify now-playing stream, Letterboxd movie logs, and late-night game status.
- **Your Dev / Systems Den:** Receives your GitHub commit feed, arXiv reading list, and terminal project notes.
- **Your Family Sanctum:** Receives life milestones and photos without the tech noise.

You don't enter data twice. You own the pipe, you decide who sees what, and your everyday activity traces finally serve your friendships instead of an ad broker.

---

### The Tangent Tracker: Rescuing Conversations from Oblivion

The best conversations with close friends are long, rambling, and meandering. You start talking about how your week went, leap into a memory from five years ago, branch into a book recommendation, and end up examining some strange idea about life.

The problem with adult life is that these conversations inevitably get cut off—a train pulls into the station, dinner starts burning, a work call rings, or you fall asleep at 2 AM.

When that happens, **all those wonderful tangents become loose ends**. And without an intentional tool, loose ends get permanently lost in the endless scrollback of WhatsApp, Signal, or Telegram. Weeks pass, and neither of you remembers where the thread went.

With rock-solid privacy guarantees and practically zero-cost local audio transcription (running models like Whisper locally on your own machine), those meandering tangents don't have to evaporate:
- **Private & Local by Design:** Audio calls are transcribed locally on-device or processed in-memory. Your personal conversations are never stored on public servers or used to train third-party models.
- **Catching Dropped Threads:** The Tangent Tracker quietly notes the open ideas, book recommendations, life crossroads, and half-finished thoughts that got abandoned mid-sentence.
- **A Natural Reason to Reconnect:** Weeks later, instead of wondering how to break the silence, you have a natural, warm reason to reach back out:  
  > *"Hey, we got completely sidetracked when your food arrived—what were you saying about that book?"*  
  > *"Did you ever end up making a decision on that Tokyo move you were weighing?"*

It eliminates the friction of starting over. Your conversations have continuity, depth, and memory.

---

### Feature Status & Roadmap

> [!NOTE]
> This project is an ongoing engineering and design exploration. Below is an honest breakdown of what is actually running in the prototype today versus what is partially built or planned.

| Feature Area | Component | Status | Reality Check |
| :--- | :--- | :--- | :--- |
| **Dunbar Core** | $N \le 15$ Member Ceiling | **[PROTOTYPE WORKING]** | Enforced mathematically in `den_prototype/engine.py`. Hard error on 16th user. |
| **Spatial Presence** | 3D Living Room Canvas | **[PROTOTYPE WORKING]** | Three.js WebGL room with fireplace, desk, and furniture states running on `localhost:8090`. |
| **Ambient Traces** | Passive Activity Feeds | **[PROTOTYPE WORKING]** | Mocked live streams for Spotify playing tracks, Letterboxd logs, and GitHub activity. |
| **Zero-Debt Rituals** | Embers & Hearth Timers | **[PROTOTYPE WORKING]** | Transient warmth pings (no unread counters) and shared focus fireplace timers. |
| **Conversation Memory** | Tangent Index Cards | **[PARTIALLY DONE]** | In-memory schema & classifier in `tangent_service.py` extracts dropped threads, crossroads, and rabbit holes. Local LLM (Ollama / Whisper) integration for noisy audio transcripts is in progress. |
| **Privacy & Storage** | Local Encrypted Vault | **[PARTIALLY DONE]** | Currently uses local in-memory/SQLite state; cryptographic at-rest vault for tangent cards is on the roadmap. |
| **Audio Hub** | 1-on-1 Acoustic Booth | **[PLANNED]** | Private WebRTC audio pipe with automatic ambient room soundscapes and ephemeral voice dispatches. |
| **Multi-Den Federation** | Sovereign Private Nodes | **[PLANNED]** | Self-hosted instances communicating peer-to-peer without a centralized cloud platform. |

---

### System Architecture

```
                                  [ THE DEN ]
                   FastAPI + WebSockets (Local / Self-Hosted)
                                       │
        ┌──────────────────────────────┼──────────────────────────────┐
        │                              │                              │
        ▼                              ▼                              ▼
  [ 3D Living Room ]          [ Activity Traces ]            [ The Sanctums ]
Three.js WebGL canvas:       Passive real-time telemetry:  Air-gapped contexts:
• Spatial avatar presence    • Spotify playing stream      • Buddies Den (15)
• Hearth, bookshelf, desk    • Letterboxd reviews          • Family Sanctum
• Interactive furnishings    • GitHub activity feeds       • Sovereign Hearth
```

---

### Running The Den

The prototype runs locally as a standalone Python / Three.js service:

```powershell
# Run the complete test suite (Dunbar limit, activity streams, lore voting)
py -3.14 run_den_prototype.py

# Launch the live interactive living room on localhost:8090
py -3.14 launch_den_server.py
```

Open your browser to:
```text
http://127.0.0.1:8090
```

---

### The Engineering Reality

The temptation is always to make the sandbox bigger—add a discovery tab, let friends of friends peer through the window, build an integration that hooks into X or Bluesky.

The moment you do that, the Shannon floor collapses. You are back in the arena, managing impressions, and optimizing for the spectator instead of the friend sitting across the table. 

The Den stays small, or it has no reason to exist.
