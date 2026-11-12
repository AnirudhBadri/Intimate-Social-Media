# The Den: Intimate Social Media

> *"Namma panradhu nammala mudinjadha pannittu, meedhiya Perumal-ta vittudanum."*  
> (Do what is within your power; surrender the outcome to the universe.)  
> — Traditional Tamil dictum / *Bhagavad Gita* 2.47

---

> [!WARNING]
> **Work-in-Progress & Prototype Notice:**  
> **The Den is an experimental prototype and design exploration.** Most features described in this document are currently either in-progress proofs-of-concept or architectural milestones on the roadmap.  
> 
> This README documents the **core ethos, design philosophy, and system invariants** of the project—the antidote to algorithmic broadcast feeds and audience capture. For an honest breakdown of what is currently working in the prototype versus what is planned, see the [Feature Status & Roadmap](#feature-status--roadmap) section below.

---

### The Premise: We Built Broadcast Engines and Called Them Friends

Every major social network is an algorithmic strip-mine. 

They take an evolutionary animal designed to maintain maybe a dozen high-trust relationships, shove a megaphone in its hands, drop it into an arena with eight billion strangers, and measure its worth by how much noise it can provoke before midnight.

When you broadcast to an audience:
1. **Context collapses into a performance:** You cannot speak the same way to your mother, your old college roommate, your manager, and an anonymous teenager looking for blood in quote-tweets. When all four sit in the same room, you stop speaking honestly; you produce sanitized PR or provocative slop.
2. **Conversation becomes debt:** A red notification bubble is a digital subpoena. Read receipts and unread badges turn casual contact into an endless administrative backlog of guilt.
3. **The feed rewards spectacle over presence:** The algorithm doesn't care if you had an honest 2 AM talk with your best friend. It cares whether your post made 500 strangers angry enough to scroll for another twenty minutes.

**The Den** is an experiment in the opposite direction. It is a standalone, bounded digital sanctuary built on three immovable boundaries.

---

### The Three Invariants

```
+---------------------------------------------------------------------------------------+
|                                  THE DEN INVARIANTS                                   |
+---------------------------------------------------------------------------------------+
| 1. HARD DUNBAR CEILING (N <= 15) :: Mathematically blocked at 15. No audience to farm.|
| 2. AMBIENT EXHAUST OVER SPECS     :: Presence through telemetry, not performative text. |
| 3. ZERO-DEBT RECIPROCITY         :: Embers, shared hearths, and asynchronous slow turns.|
+---------------------------------------------------------------------------------------+
```

#### 1. The Hard Dunbar Boundary ($N \le 15$)
A Den has a hard, mathematical ceiling of fifteen people. Not as a soft guideline, but as an engine assertion:
```python
if len(self.users) >= self.dunbar_cap:  # dunbar_cap = 15
    return {"success": False, "error": "Dunbar Limit Reached: Cannot exceed 15 members."}
```
If you want to add a sixteenth person, someone has to leave or you build another Den. This single constraint kills audience capture at the root: there is no virality, no follower count, and no reason to perform.

#### 2. Ambient Exhaust over Performative Broadcast
You shouldn't have to write a status update to prove you're alive. In The Den, presence is shared through passive exhausts:
- What you're actually listening to right now (Spotify real-time stream).
- What you watched last night and gave three stars to (Letterboxd logs).
- What code you actually committed to a repository (GitHub exhaust).
- What room in the 3D living room your avatar is idling in.

You see your friends the way you saw roommates in college: you glance into the living room, see someone on the couch with headphones on, and you know they're there without forcing them to talk.

#### 3. Zero-Debt Presence
The biggest friction in modern messaging is the asymmetry of reply obligations:
- **Embers:** Send a transient warmth ping to a friend's hearth. It leaves no unread counter, expects no reply, and creates no administrative guilt.
- **Mutual Lore Consecration:** Inside jokes don't become permanent artifacts on the wall because one person posted them; they require multi-party consensus to be consecrated into the space's permanent history.
- **Asynchronous Slow Games:** One board, one turn every few days. The game moves at the pace of human life, not push notifications.
- **Acoustic Corner Booth:** A private 1-on-1 audio sanctuary for deep sparring, voice dispatches, and raw reflection without a broadcast feed.

---

### Conversation Memory: Tangent Cards & Unfinished Threads

Most AI in messaging apps is useless theater—chatbots pretending to be human or generating corporate "meeting notes" for casual hangouts.

The Den's **Tangent Indexer** is basically a quiet index card box on the coffee table. Real friends drop conversations all the time because life happens. You don't need a summary with bulleted action items; you just want a trigger so you don't default to *"How's work?"* or *"Long time no see."*

#### 1. What It Tracks

- **Unfinished Debates (`unfinished_debate`)**  
  You spent two hours arguing about monoliths vs. microservices, or whether a film was brilliant or pretentious. Work interrupted, nobody conceded, and you both went to sleep. A card saves the crux so next week you can jump back in without reheating the soup.  
  *Context:* Dave: *"Microservices are overkill for three people."* / Badri: *"Network boundaries prevent monolith rot!"*  
  *Opener:* *"Hey Dave, did you ever find an actual counter-argument on monolith rot, or are we calling it a draw?"*

- **Pending Crossroads (`unresolved_decision`)**  
  A friend mentions weighing a job offer in Tokyo, moving cities, or quitting a startup. Two weeks pass, and people forget because daily routines take over. The card flags that a major pivot was on the table so you actually remember to ask what happened.  
  *Context:* Dave: *"Got an engineering leadership ping for Tokyo, weighing the timezone shift."*  
  *Opener:* *"Dave, did you ever make a call on that Tokyo offer, or did you stay put?"*

- **Shared Rabbit Holes (`deep_rabbit_hole`)**  
  You both fell down a 2 AM rabbit hole about vintage 80s Casio synth modifications or 70s Japanese city pop. The card saves the link cluster so the shared obsession doesn't evaporate into the bottom of a WhatsApp export.  
  *Context:* Two hours sharing schematics for 1980s Casio keyboard solder mods.  
  *Opener:* *"Still thinking about that vintage synth modification rabbit hole from Tuesday."*

#### 2. The Architecture & Privacy Contract

- **No Public Model Training:** Chat exports and voice transcripts are processed in-memory. Nothing is ever sent to train third-party foundation models.
- **Local-First / On-Device:** Runs against a local lightweight model (Ollama / quantized local weights) or ephemeral in-memory processors.
- **Encrypted at Rest:** Tangent index cards live strictly inside your Den’s local database. No central server reads your cards.

---

### Feature Status & Roadmap

> [!NOTE]
> This project is an ongoing engineering and design exploration. Below is an honest breakdown of what is actually running in the prototype today versus what is partially built or planned.

| Feature Area | Component | Status | Reality Check |
| :--- | :--- | :--- | :--- |
| **Dunbar Core** | $N \le 15$ Member Ceiling | **[PROTOTYPE WORKING]** | Enforced mathematically in `den_prototype/engine.py`. Hard error on 16th user. |
| **Spatial Presence** | 3D Living Room Canvas | **[PROTOTYPE WORKING]** | Three.js WebGL room with fireplace, desk, and furniture states running on `localhost:8090`. |
| **Ambient Telemetry** | Passive Exhaust Feeds | **[PROTOTYPE WORKING]** | Mocked live streams for Spotify playing tracks, Letterboxd logs, and GitHub commits. |
| **Zero-Debt Rituals** | Embers & Hearth Timers | **[PROTOTYPE WORKING]** | Transient warmth pings (no unread counters) and shared focus fireplace timers. |
| **Conversation Memory** | Tangent Index Cards | **[PARTIALLY DONE]** | In-memory schema & classifier in `tangent_service.py` extracts debates, crossroads, and rabbit holes from pasted text. Local LLM (Ollama) integration for noisy audio transcripts is in progress. |
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
  [ 3D Living Room ]          [ Ambient Exhausts ]           [ The Sanctums ]
Three.js WebGL canvas:       Passive real-time telemetry:  Air-gapped contexts:
• Spatial avatar presence    • Spotify playing stream      • Buddies Den (15)
• Hearth, bookshelf, desk    • Letterboxd reviews          • Family Sanctum
• Interactive furnishings    • GitHub commit feeds         • Sovereign Hearth
```

---

### Running The Den

The prototype runs locally as a standalone Python / Three.js service:

```powershell
# Run the complete test suite (Dunbar limit, ambient streams, lore voting)
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
