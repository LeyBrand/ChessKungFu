# Kung-Fu Chess — Scalable Server Design (v1 draft)

**Scope:** Evolving the current single-process `GameServer` (asyncio + websockets,
in-process `PlayerRegistry`) into a small, horizontally-scalable version that can
run as a few cooperating Docker containers, following the reviewed reference
architecture at a reduced scale appropriate for a working Docker Compose demo
(not a literal 100M-user deployment).

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

## 3. Who decides which container runs a room (Game Allocator role)

The container a client is connected to (the Gateway side) is not necessarily
the container that runs that room's game logic — separating "connection edge"
from "game logic host" means the game-running container can be chosen for
speed/load, not just because it happened to accept the socket first.

Whichever Gateway instance handles the *first* join request for a room_id is
the one that decides (and writes) which shard will run it — there's no one
else who could decide earlier, since no one else has seen the room yet.

**Race condition:** two Gateways could both try to allocate a shard for the
same room_id at the same instant. Same fix as before:

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
| `gateway` | connection handling + room registry logic (§2, §3) | 1–2 |
| `game-shard-1`, `game-shard-2` | `GameServer` game-logic instances | 2 |
| `redis` | room registry (Hash per room) | 1 |
| *(postgres — TBD, see §6)* | | |

Containers resolve each other by **service name** as hostname (Docker's
internal DNS) — e.g. `game-shard-1:8765` is reachable by name from any other
container on the same Compose network, no manual IP tracking needed.

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

**Race condition (same pattern as §2/§3, new shape):** two Gateways could
run `seek()` at the same instant, both `ZRANGEBYSCORE` and find the *same*
waiting opponent, and both declare a match with them — a classic
check-then-act gap, this time between "find" (`ZRANGEBYSCORE`) and "use"
(`ZREM`), which unlike `HSETNX` has no single built-in atomic command.

**Fix: a Redis Lua script.** Redis executes a Lua script as one
uninterruptible unit — no other client's command can run in the middle of
it, even though the script itself does multiple internal steps. So:
```
seek(player_id, rating) — atomic Lua script:
  1. ZRANGEBYSCORE waiting_pool (rating-range) (rating+range)
  2. if found: ZREM them from the pool, return them as the match
  3. if not found: ZADD the caller to the pool, return nil
```
Because Redis runs scripts strictly one-at-a-time, a second Gateway's
`seek()` call — even fired milliseconds later — simply won't find that
opponent in the pool anymore; there's no window where two Gateways can both
"win" the same match.

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

## 9. TODO — sections not yet designed

- [ ] **Auth / login** — API Gateway split for REST vs. WS traffic
- [ ] **Game duration (30–90s) → allocator strategy** — why short games mean
      load-based (not sticky) shard assignment

---

*Draft status: sections 1–4 reflect concrete decisions made in design
discussion. Section 5 items still need to be worked through before this is
submission-ready.*