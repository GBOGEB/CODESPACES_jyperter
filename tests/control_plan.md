# Test & Control Plan (focused)

Objective. Demonstrate stable relief without chatter; confirm backpressure limits and velocities for 200 g/s worst case, and functional margins for 3 g/s nominal.

1. **Bench Set & Leak-Tightness**
   1. Set PSV at 1.50 bar(a) (document CDTP & tolerance).
   2. Seat leakage per manufacturer class at ambient and cold (if applicable).
2. **Backpressure Simulation (Flow Bench / Site with Orifice Restrictor)**
   1. Impose superimposed 1.05 bar(a) at outlet.
   2. Emulate built-up for DN100 and DN125 with calibrated K-elements to target 0.07 bar and 0.035 bar respectively at 200 g/s.
   3. Record: lift pressure, mass flow, outlet ripple (RMS), no chatter criterion.
3. **Velocity / Mach Checks**
   1. Verify v at tail-pipe exit ≤ 0.3 Ma (calculate from measured flow & local T).
   2. If >0.3 Ma, qualify diffuser/silencer; re-run Step 2.
4. **Integrated Routing Verification**
   1. Measure actual line length, bends, K-factors; recompute Δp_built.
   2. Acceptance: Δp_built ≤ 0.10 bar (gas) and total backpressure within PSV allowable per device type.
   3. For balanced-bellows, confirm bellows area/limit pressure and stability with variable backpressure.
5. **Controls Interaction**
   1. Confirm CV remains NC through lift; apply dead-band & rate limit; CV may trim only after reseat margin restored.
   2. Alarm thresholds: pre-lift at ≥ 0.9×1.50 = 1.35 bar(a); backpressure alarm at ≥ 80% of allowable.
6. **Documentation (PED/CE)**
   1. Sizing sheet (inputs, equations, margins).
   2. Tail-pipe calc with as-built geometry.
   3. FAT/SAT reports including traces and KPIs (lifts/1000 h, max Δp_built, RMS ripple).
