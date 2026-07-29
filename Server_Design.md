# Kung-Fu Chess — Scalable Server Design (v1 draft)

**Scope:** Evolving the current single-process `GameServer` (asyncio + websockets,
in-process `PlayerRegistry`, in-process `Matchmaker`) into a horizontally-scalable
service split — Gateway, Auth, Matchmaker, Game Allocator, Game Server Shards,
Rating Service, Redis, PostgreSQL, NATS — aligned with the reviewed KamaTech
reference architecture, sized down to a working Docker Compose demo (single
instance of each stateful piece, not a literal 100M-user deployment).

---

## 1. What changes vs. the current single-process server

Today, `GameServer` holds all state in memory (which rooms exist, who is in
each, what color they are). That works because there's only one process.

The moment there is more than one container, any state that needs to be seen
by *all* containers has to move out of Python memory and into something all
containers can reach: **Redis**.

**Decision:** the minimum state that must become shared:
- room membership (`white` / `black` usernames per room)
- which container/shard is actually running the game logic for that room

Everything else (rendering, per-connection socket objects) stays local to
whichever container holds that specific connection.

---

## 2. Room Registry (Redis)

**Storage shape:** one Redis **Hash** per room, not a single JSON string.

```
key: room:{room_id}
fields:
  white -> "<username>"
  black -> "<username>"
  shard -> "<hostname>:<port>"      # which container runs this room
```

**Why a Hash and not a JSON string:** a Hash lets us update a single field
(e.g. claim `black`) without reading and rewriting the whole object — which
matters for the next point.

**Why not plain `HSET`:** `HSET` alone is a *read-then-write* — check if a
field is empty, then write. Between the check and the write there's a gap,
and two containers racing to fill the same field can both "win," with one
silently overwriting the other. This is the same class of bug as the
count-based color assignment bug in `PlayerRegistry`, just at network scale.

**Decision: use `HSETNX`.** It's atomic inside Redis (Redis executes commands
one at a time) — "write only if empty" happens as a single, indivisible step.
It returns `1` if it wrote, `0` if the field was already taken.

**`join_room` sequence:**
1. `HSETNX room:{id} white {username}` → if `1`, done, this client is white.
2. If `0`, try `HSETNX room:{id} black {username}` → if `1`, this client is black.
3. If both fail, the room already has two players.

This same pattern (`HSETNX`, check the return value) is used for the `shard`
field too — see §3.

---

## 3. Who decides which container runs a room — Game Allocator (separate service)

**Revision:** originally this role was folded into the Gateway for
simplicity. Aligning with the KamaTech reference, it's a **standalone
service** instead: the Gateway/WS Gateway never decides which shard runs a
room — separating "connection edge" from "allocation decision" means the
allocator can be scaled and reasoned about independently (per §7's
control-plane discussion), and a spike in connections doesn't compete with
allocation logic for resources.

The Game Allocator receives a "matched" event from the Matchmaker (over
NATS, §7) and decides which shard a new room runs on — see §10 for the
least-loaded selection strategy.

**Race condition:** with multiple Game Allocator replicas, two of them could
both try to allocate a shard for the same room_id at the same instant (e.g.
if the "matched" event were somehow delivered twice). Same fix as before:

```
HSETNX room:{id} shard "game-shard-1:8765"
```

If it returns `0`, another Gateway already assigned a shard — read it with
`HGET room:{id} shard` instead of assigning a new one.

---

## 4. Docker Compose — minimal local topology

*(draft — to confirm exact service names against `docker-compose.yml`)*

| service | contains | replicas (local) |
|---|---|---|
| `api-gateway` | REST/HTTP: login forwarding, room CRUD/history | 1 |
| `ws-gateway` | WebSocket terminator, relays moves/state; room registry lookups (§2) | 1–2 |
| `auth-service` | credential check against Postgres, issues session tokens (§11) | 1 |
| `rooms-api` | room CRUD/history, backed by Postgres | 1 |
| `matchmaker` | ELO queue against Redis Sorted Set (§6), publishes "matched" to NATS | 1 |
| `game-allocator` | consumes "matched" from NATS, picks least-loaded shard (§3, §10) | 1 |
| `game-shard-1`, `game-shard-2` | `GameServer` game-logic instances, N worker processes each | 2 |
| `redis` | room registry, waiting pool, heartbeats, sessions, live ratings | 1 |
| `postgres` | users, ratings (durable) | 1 |
| `nats` | control-plane event bus (§7) | 1 |

Containers resolve each other by **service name** as hostname (Docker's
internal DNS) — e.g. `game-shard-1:8765` is reachable by name from any other
container on the same Compose network, no manual IP tracking needed. This
mirrors the KamaTech reference's service list at local-development scale —
no HPA, no multi-region, single instance of Redis/Postgres/NATS.

---

## 5. PostgreSQL — why SQLite doesn't scale, and what actually moves there

**Current state (`PlayerStore`, `players.db`):** a single-file SQLite DB with
one table (`players`: username, password_hash, salt, rating). Every method
(`create_player`, `verify_password`, `get_rating`, `update_rating`) opens
against one `sqlite3.connect(...)` in one process.

**Problem 1 — concurrent writers (exists even at 10 rows):** SQLite locks
the *entire file* on write. If two containers (e.g. two `game-shard`
instances) both hold a connection to the same `players.db` and try to write
at the same time, one is blocked — regardless of how many rows are in the
table. This is a concurrency problem, not a volume problem.

**Problem 2 — single file, single machine (this one *is* about volume/
durability):** SQLite is one file on one disk. At 100M registered users:
- **No replication** — if that machine/disk dies, all 100M rows are gone.
- **No read fan-out** — every `SELECT` (login, `get_rating`) hits the same
  physical file, even if 50 containers are reading at once.

**Decision: PostgreSQL with read replicas.** One primary handles writes;
replicas absorb the read load (login checks, rating lookups) so it's spread
across machines instead of bottlenecked on one file. Replicas also double as
standby copies for durability.

**Rating updates — write path (not straight to Postgres per game):**
- On game end, the new rating is written **immediately** to Redis
  (`HSET rating:{username} value {new_rating}`) — this is what Matchmaker
  reads when the player queues for their next game, so it's never stale.
- Separately, at a slower cadence (e.g. once per second), the batch of
  ratings that changed is flushed to PostgreSQL for durability. Postgres is
  not on the hot path for rating reads — only for making sure the value
  survives a crash.
- Reasoning: at ~10M concurrent games averaging ~60s each, that's roughly
  166K game-endings/sec → 166K+ `UPDATE`s/sec if done naively per-game. A
  single Postgres primary handles roughly 10K–50K simple writes/sec, so
  per-event writes don't fit; batching does.

**Move history — explicitly out of scope for persistence.** Live move
history (what `MoveLogTracker` shows both players during an active game) is
ephemeral — it doesn't need to survive after the game ends, because there is
no post-game replay / spectate-old-games requirement in this project. This
is a deliberate deviation from the reference architecture (which does
persist move history for replay) — noted here explicitly since it's a scope
decision, not an oversight.

---

## 6. Matchmaker — distributing the existing FIFO/ELO pool

**Current state (`tournament/matchmaker.py`):** `Matchmaker.seek(player_id,
username, rating)` scans an in-memory dict `self._waiting` for anyone within
`elo_range` of `rating`; if found, removes and returns them (a match); if
not, adds the caller to the pool and returns `None`. Already
offline-testable, no network imports — same principle as `TournamentManager`.

**What breaks with multiple containers:**
1. `self._waiting` is a plain Python dict — local to whichever process holds
   it. A player whose `seek()` lands on container 1 can never be matched
   with a player whose `seek()` lands on container 2; each container only
   sees its own pool.
2. The range-scan logic (`abs(info["rating"] - rating) <= elo_range`) has no
   direct equivalent in a plain Redis Hash (no "find me values in a range").

**Decision: Redis Sorted Set for the shared waiting pool**, scored by
rating:
```
ZADD waiting_pool {rating} {player_id}
ZRANGEBYSCORE waiting_pool {rating-elo_range} {rating+elo_range}
```
This gives the range lookup `seek()` needs, shared across every container.

**Race condition (same pattern as §2/§3, new shape):** with multiple
Matchmaker replicas, two could run `seek()` at the same instant, both
`ZRANGEBYSCORE` and find the *same* waiting opponent, and both declare a
match with them — a classic check-then-act gap, this time between "find"
(`ZRANGEBYSCORE`) and "use" (`ZREM`), which unlike `HSETNX` has no single
built-in atomic command.

**Fix: a Redis Lua script.** Redis executes a Lua script as one
uninterruptible unit — no other client's command can run in the middle of
it, even though the script itself does multiple internal steps. So:
```
seek(player_id, rating) — atomic Lua script:
  1. ZRANGEBYSCORE waiting_pool (rating-range) (rating+range)
  2. if found: ZREM them from the pool, return them as the match
  3. if not found: ZADD the caller to the pool, return nil
```
Because Redis runs scripts strictly one-at-a-time, a second Matchmaker
replica's `seek()` call — even fired milliseconds later — simply won't find
that opponent in the pool anymore; there's no window where two replicas can
both "win" the same match.

---

## 7. NATS — control-plane event bus between split services

**Why it's needed now (wasn't in v1):** once Matchmaker, Game Allocator,
Auth Service, and the Gateways are *separate* containers (§4), some of them
need to notify each other about things that happen — without becoming
tightly coupled (each one hard-coding the others' addresses) or blocking on
a synchronous call for something that isn't urgent.

**Two communication shapes, and how to tell them apart:**
| Shape | When to use it | Example |
|---|---|---|
| **Sync RPC** (HTTP/gRPC, caller waits) | Caller can't proceed without the answer *right now* | WS Gateway → Auth: "is this session valid?" (must know before relaying anything) |
| **NATS event** (publish, fire-and-forget) | Low frequency, caller doesn't need to wait for a response to keep going | Matchmaker → Game Allocator: "players X,Y matched" |

**Classifying the actual inter-service calls in this design:**
- **WS Gateway → Auth Service** ("is this session valid?") — sync RPC. The
  Gateway cannot relay a message without knowing the answer immediately.
- **WS Gateway → Redis** (resolve `room:{id} → shard`) — not NATS at all,
  a direct Redis read; the Gateway needs the address immediately to route.
- **Matchmaker → Game Allocator** ("matched: player A + player B") — NATS
  event. Happens once per match (every 30–90s per room, not per move — a
  tiny fraction of the 5,000,000 moves/sec from §8), and the Matchmaker
  doesn't need a reply to keep working the queue.
- **Game Server Shard → Rating Service** ("game over, update rating") — NATS
  event, same reasoning: once per game end, fire-and-forget.
- **WS Gateway → Matchmaker** ("I'm looking for a match") is a hybrid: the
  client needs immediate acknowledgment of "you're in the queue" (sync), but
  the *match itself*, when it happens, arrives later as a separate event
  (the Matchmaker → Game Allocator NATS message above, which eventually
  results in the Gateway being told where to route the player).

**What NATS is *not* used for:** live gameplay traffic. Moves and state
updates stay on the direct WS Gateway ↔ Game Server Shard path (address
resolved via Redis, §2/§3) — routing 5,000,000 moves/sec through an event
bus would add a hop to the highest-frequency traffic in the system for no
benefit, since that traffic already has a clear point-to-point destination
once the room is allocated.

---

## 8. Traffic volume — moves/sec, and where the real bottleneck is

**Move rate:** 10M concurrent players, one move every ~2s on average →
`10,000,000 ÷ 2 = 5,000,000` moves/sec system-wide.

**Bandwidth:** a single move JSON (`{"type":"move","room_id":"42","from":
[4,6],"to":[4,4],"time_ms":15234}`) is roughly **80 bytes**.
`80 bytes × 5,000,000/sec = 400,000,000 bytes/sec = 400 MB/s = 3.2 Gbps`
total, across every container combined.

**Conclusion — this is not a bandwidth problem.** A single modern server
NIC handles 10 Gbps as a baseline (25/40/100 Gbps common in data centers).
3.2 Gbps total system load fits comfortably on one NIC, let alone a whole
fleet. It's also not a DB problem — per §5, live moves never touch
PostgreSQL at all (only the much smaller, batched rating-update stream does).

**The real bottleneck is CPU**, specifically Python's GIL. Every move
requires validating game rules and updating board state (`GameEngine`,
Part A) — CPU-bound work, not I/O. CPython's GIL means only one thread runs
Python bytecode at a time *within a single process*, regardless of core
count; `asyncio` gives concurrency for I/O-bound waiting, not parallel
CPU execution.

**Why multiprocessing (not multithreading) fixes this:** each OS *process*
gets its own interpreter and its own independent GIL. N worker processes (one
per CPU core, per §9's diagram) genuinely run in parallel across N cores,
each running its own asyncio event loop internally for the rooms it owns.
This directly motivates why rooms are pinned to one worker process for their
whole lifetime (§9) — matches are short (30–90s), so there's no need for
mid-game migration between workers.

---

## 10. Allocator strategy — which worker gets a new room

**Decision: least-loaded, not round-robin.** Round-robin assumes each unit
of work costs about the same — true for typical short HTTP requests, but not
here: a room occupies a worker for its *entire* 30–90s lifetime (no
mid-game migration, per §8). Round-robin can't react to real imbalance — a
worker that happened to draw several long games in a row stays "due" for
more work by the counter, even while genuinely more loaded than others.
Least-loaded reacts to actual, current load instead.

**Load signal: active room count per worker**, self-reported via a
heartbeat key in Redis:
```
key: heartbeat:{shard_hostname}:{worker_pid}
value: {"active_rooms": <count>}
TTL: short (e.g. 5-10s)
```
Active room count is a reasonable proxy for CPU load without needing to
measure CPU% directly, since each room costs roughly similar work.

**Why the TTL matters:** each worker refreshes its own heartbeat key every
few seconds (well under the TTL), which resets the TTL clock each time. If a
worker crashes, it simply stops refreshing — the key isn't cleaned up
manually, Redis expires it automatically once the TTL elapses.

Without a TTL, a crashed worker's *last* heartbeat (e.g. "only 2 rooms, low
load") would sit in Redis indefinitely. The Allocator would keep seeing it
as a good low-load candidate and route new matches to it — and those rooms
would simply vanish, with both matched players waiting on a worker that no
longer exists. TTL turns "worker went silent" into "entry disappears," so
the Allocator naturally stops considering it.

**Allocation step:** on a new match, the Allocator reads all
`heartbeat:*` keys, picks the one with the lowest `active_rooms`, and
writes that worker's address into `room:{id}` as the `shard` field (§2/§3),
using the same `HSETNX` pattern already established there.

---

## 11. Auth / login — session tokens, not per-message passwords

**Flow:**
1. Client sends username+password over REST/HTTP to **API Gateway**, which
   forwards it to the standalone **Auth Service** (§4) — once, at login.
   This is separate from the **WS Gateway**, which only handles the
   long-lived gameplay connection, not login itself.
2. Auth Service checks credentials against `PlayerStore`/PostgreSQL (same
   `verify_password` logic as today). On success, generates a random
   session token and writes it to Redis:
   ```
   key: session:{token}
   value: {"username": "ley"}
   TTL: a few hours
   ```
3. The client attaches that token (not the password) to every subsequent
   request/WebSocket message.
4. Any Gateway or worker that receives a request does `GET session:{token}`
   — if present, it knows who's calling without touching PostgreSQL at all.

**Why this matters for the numbers in §8:** if every one of the 5,000,000
moves/sec had to re-verify a username+password against PostgreSQL instead
of a cheap Redis lookup, the DB would be on the hottest path in the entire
system — exactly the kind of per-event load that batching (§5) was
designed to avoid. Session tokens keep PostgreSQL off the real-time path
entirely; it's only touched once per login.

**TTL here is for a different reason than the heartbeat TTL (§10):** not
crash detection, but security — a session shouldn't stay valid forever
without renewed activity.

---

## 12. Summary — how all the pieces connect

```
                                    ┌────────────┐
                                    │   Clients   │
                                    └──┬───────┬──┘
                                REST/  │       │ WebSocket
                                HTTP   │       │
                        ┌──────────────▼┐   ┌──▼───────────────┐
                        │  API Gateway   │   │    WS Gateway     │  both stateless,
                        │ login, room    │   │ terminates socket, │  never hold room/
                        │ CRUD, history  │   │ relays moves/state │  game state (§3)
                        └───┬────────┬──┘   └──┬─────────────┬──┘
                            │        │         │             │
                            ▼        ▼         │       resolve room→shard
                     ┌───────────┐ ┌────────┐  │        (direct Redis read,
                     │   Auth    │ │ Rooms  │  │         not NATS — §7)
                     │  Service  │ │  API   │  │             │
                     │ (§11)     │ │        │  │             │
                     └─────┬─────┘ └───┬────┘  │             │
                            │           │      │ session      │
                            │           │      │ check (sync, │
                            │           │      │ §7, §11)     │
                            └─────┬─────┴──────┴──────┬────── ┘
                                  │                    │
                                  ▼                    ▼
                   ┌───────────────────────────────────────────────────┐
                   │                        Redis                        │
                   │  room:{id}       -> {white, black, shard}  HSETNX   │ §2 §3
                   │  waiting_pool    -> Sorted Set, scored by rating     │ §6
                   │                     (Lua script: find+remove atomic)│
                   │  heartbeat:{w}   -> {active_rooms}  TTL=crash-detect│ §10
                   │  rating:{user}   -> value            HSET, immediate│ §5
                   │  session:{token} -> {username}       TTL=security   │ §11
                   └───────────────────────┬───────────────────────────┘
                                            │ resolved shard:worker address
                            ┌───────────────┼───────────────────┐
                            │                                   │
                     "I'm looking      ┌─────────────┐   ┌─────────────┐
                      for a match"     │ game-shard 0 │   │ game-shard N │  1 worker/
                      (sync ack) ──►┌──┤  worker 0    │...│  worker N    │  CPU core
                            │       │  │ GameEngine   │   │ GameEngine   │  (§8) —
                     ┌──────▼─────┐ │  │ (Part A)     │   │ (Part A)     │  separate
                     │ Matchmaker │ │  └──────┬───────┘   └──────┬───────┘  GILs
                     │  (§6)      │ │         │                  │
                     └─────┬──────┘ │         └────────┬─────────┘
                            │        │                  │
                  "matched!"│ NATS   │                  │ "game over,
                  (event,   │(§7)    │                  │  update rating"
                   §7)      │        │                  │ (NATS event, §7)
                            ▼        │                  ▼
                    ┌───────────────┐│          ┌───────────────┐
                    │ Game Allocator││          │ Rating Service │
                    │ least-loaded  ││          │  (elo update)  │
                    │ (§3, §10)     ││          └───────┬────────┘
                    └───────┬───────┘│                  │
                            │  writes shard             │ batched
                            │  to Redis (§3)             │ flush, ~1/sec
                            └────────┘                   ▼
                                                  ┌───────────────────┐
                                                  │    PostgreSQL       │
                                                  │ users, ratings       │  primary +
                                                  │ (durable, off the    │  read replicas
                                                  │  real-time path)      │  (§5)
                                                  └───────────────────┘
```

**Reading the diagram:** solid arrows into Redis are the atomic patterns
worked out above (`HSETNX` for claim-once fields, a Lua script for
find-and-remove) — the same race-condition shape (two replicas hitting the
same decision at once) recurs at every layer, and gets the same fix each
time. Dashed-equivalent paths (Matchmaker→Allocator, Shard→Rating Service)
are NATS events — low-frequency, fire-and-forget, decoupling services that
don't need to block on each other (§7). The live-gameplay path (WS Gateway
↔ Game Server Shard, resolved via Redis) never touches NATS — that's
reserved for high-volume data, not control-plane messages.

---

## 13. TODO — sections not yet designed

*(none remaining — draft complete; ready for review)*

---

*Draft status: full service split (API/WS Gateway, Auth, Rooms API,
Matchmaker, Game Allocator, Rating Service, NATS) now aligned with the
KamaTech reference architecture. Move-history persistence (§5) remains a
deliberate, explicitly-noted scope deviation — no post-game replay
requirement exists in this project.*