# Mechanical Metaphor Dictionary for Software & Math Concepts

Use this catalog to map abstract computational primitives onto concrete physical mechanisms. Never settle for glowing cubes—choose mechanisms whose physical constraints mirror the mathematical constraints of the concept.

---

## 1. Core Concept-to-Mechanism Mappings

| Software / Math Concept | Physical Mechanism Counterpart | Visual Readout & Motion |
| :--- | :--- | :--- |
| **Token Bucket / Rate Limiter** | Overhead drip nozzle + graduated borosilicate glass cylinder + spring-loaded escapement gate | Brass tokens/droplets accumulate up to overflow weir; incoming requests trip the gate only when level >= 1. |
| **LRU / LFU Cache** | Rotary brass carousel / Turntable with indexed slots + pneumatic ejector arm | Cache hit pulls slot to front index (`0°`); cache miss at full capacity ejects rear slot down a cold-storage chute. |
| **Hash Table / Consistent Hashing** | Circular dividing head / Indexed ring gear with radial sorting chutes | Input key turns vernier dial to computed angle; collisions stack vertically inside bucket magazines. |
| **Distributed Consensus (Raft / Paxos)** | Linked mechanical balance beams + ratchet term counter + heartbeat pendulum | Leader pendulum resets follower escapements; split vote leaves balance arm short of the quorum trip-latch. |
| **Backpressure / Bounded Queue** | Pressurized manifold pipe + sight gauge + float-actuated upstream throttle valve | Rising buffer height lifts brass float rod, mechanically closing the intake butterfly valve upstream. |
| **Circuit Breaker** | Thermal bimetal trip latch + spring toggle switch + cooldown sand/dashpot timer | Consecutive fault sparks bend trip bar -> jaws snap open -> dashpot piston slowly bleeds back to half-open test detent. |
| **Mutex / Read-Write Lock** | Pin-tumbler keyway / Single-token brass key interlock | Key extracted from dock physically locks competing levers until returned to the keyway. |
| **Transformer Attention** | Optical prism array / Weighted pantograph linkage | Query beam splits across Key resonators; aperture shutters widen proportionally to softmax weights, focusing Value filaments. |
| **Gradient Descent / Optimization** | Dual-axis lead-screw gantry + plumb-bob slope sensor over contoured terrain plate | Step-size gear (`learning rate`) drives carriage downhill; excessive gear ratio causes visible oscillation across valley walls. |
| **Compiler / AST Pipeline** | Punch-card reader -> lexical sortingieve -> hierarchical cam tree -> machine-code stamping press | Raw token tiles pass through syntax dies, interlock into nested frames, and stamp clean binary plates. |

---

## 2. Four Material & Palette Archetypes

### A. Atelier Brass & Vellum (Default Patent Plate)
- **Canvas**: Warm drafting vellum `#F5F1E8`, hairline frame `#D6CEBF`, carbon ink `#1C1917`.
- **Metals & Glass**: Brushed brass (`#E5B869` top / `#C9963E` left / `#9A6E22` right), cast iron (`#57534E` / `#44403C` / `#292524`), borosilicate glass (`#DFF3F8` @ 45% alpha + crisp `#FFFFFF` specular edge), signal vermilion fluid (`#E04F3E`).

### B. Precision Anodized Lab
- **Canvas**: Cool instrument paper `#F1F5F9`, slate grid `#CBD5E1`, ink `#0F172A`.
- **Materials**: Bead-blasted aluminum (`#E2E8F0` / `#CBD5E1` / `#94A3B8`), cobalt fluid (`#2563EB`), safety amber indicator (`#F59E0B`), emerald pass LED (`#10B981`).

### C. Dark Observatory Cutaway
- **Canvas**: Deep obsidian `#0B1017`, grid `#1E293B`, chalk ink `#F8FAFC`.
- **Materials**: Gunmetal housing (`#334155` / `#1E293B` / `#0F172A`), copper coils (`#F97316` / `#EA580C` / `#9A3412`), cyan plasma/fluid (`#22D3EE`).

### D. Ceramic & Copper Monograph
- **Canvas**: Rice white `#FAF8F5`, stone rule `#E7E5E4`, espresso ink `#292524`.
- **Materials**: Matte porcelain (`#FFFFFF` / `#F5F5F4` / `#D6D3D1`), oxidized verdigris (`#5EEAD4` / `#14B8A6` / `#0F766E`), terracotta counterweight (`#EA580C`).
