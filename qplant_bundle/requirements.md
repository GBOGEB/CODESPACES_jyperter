# QPLANT Contract Requirements

## REQ_01 — Cost Control Strategy Stack
**Description.** The Applicant shall implement and maintain Budget Tracking, Cost-Benefit Analysis (CBA), and Value Engineering (VE) across all lifecycle phases, and shall document methods, thresholds, and review cadence in the Offer Documentation and the Project Quality Plan in accordance with ISO 10006 / ISO 9001.
**Rationale.** Ensures disciplined, auditable cost control and savings capture.
**V&V.** Deliverable: Cost Control Plan + VE/CBA templates. Action: gate reviews with minutes. Phase: Preliminary (initial), updated at Conceptual and Detailed.

## REQ_02 — Cost Estimate as Baseline (BSL)
**Description.** The Applicant shall submit an accurate, complete, and auditable Cost Estimate that becomes the cost/scope BSL, mapped WBS↔CBS, with CAPEX/OPEX split, inflation indices, contingency model, and R&O linkages; options and alternates shall be itemized and priced.
**Rationale.** Establishes the definitive reference for multi-year scope, cost and responsibility tracking.
**V&V.** Deliverable: Cost Model workbook + basis-of-estimate (BoE). Action: baseline sign-off; variance rules defined. Phase: Preliminary, re-baselined at Conceptual freeze.

## REQ_03 — Lifecycle Optioning & Stage Gates
**Description.** The Applicant shall structure the estimate and schedule by stage-gates with explicit contractual options (design, test, compliance, acceptance metrics), aligned to ISO 15288 processes, and include priced alternates where method/standard choices exist.
**Rationale.** Transparent optioning clarifies obligations and acceptance criteria by phase.
**V&V.** Deliverable: Options register + priced alternates. Action: gate approval records. Phase: Preliminary→Conceptual.

## REQ_04 — Big-Ticket / Long-Lead Design Freeze
**Description.** The Applicant shall identify and freeze by Conceptual gate the “big-ticket/long-lead” set (e.g., HP compressors, PVPS pumps, QRB mechanical vessel & shell penetrations/internal space allocation), with technical specs, QA/QC, and test plans per EN 13445/13480 and PED.
**Rationale.** Reduces schedule/cost risk from critical procurement.
**V&V.** Deliverable: Freeze list + spec packs. Action: gate freeze memo. Phase: Conceptual (design freeze).

## REQ_05 — Interface Register with Cost Allocation
**Description.** The Applicant shall maintain a living Interface Register (physical, mechanical, electrical, signal—including external MINERVA↔QPLANT signals) with clear cost/schedule responsibility tags (Applicant/Client/Shared) and dependency links.
**Rationale.** Eliminates scope gaps and clarifies responsibility at boundaries.
**V&V.** Deliverable: Interface Register (matrix). Action: monthly closure review. Phase: from Preliminary; baseline at Detailed.

## REQ_06 — FTE Resource Plan (Applicant & Client Reciprocals)
**Description.** The Offer shall include a granular FTE/month plan by phase and discipline, explicitly listing Client reciprocating dedicated resources required to execute through operations readiness.
**Rationale.** Aligns staffing expectations; mitigates resource bottlenecks.
**V&V.** Deliverable: FTE plan (Gantt + table). Action: variance tracking ≤ Y %. Phase: Preliminary, maintained monthly.

## REQ_07 — Construction & Qualification Breakdown
**Description.** The Applicant shall decompose Construction into procurement of COTS, manufacture, assembly, qualification, and isolation testing (I/O wiring, signal latency/speed, bench performance) with methods and acceptance metrics aligned to IEC 61131-3/ISA-5.1 where applicable.
**Rationale.** Ensures verifiable quality and readiness prior to integration.
**V&V.** Deliverable: IQ/OQ packs; bench test reports. Action: witness points. Phase: Construction.

## REQ_08 — Transport Plan
**Description.** The Applicant shall deliver a Transport Plan covering preservation, lifting points/CoG, shock/vibration limits, customs, and insurance; constraints shall be flowed to vendors and the schedule.
**Rationale.** Protects critical equipment and schedule.
**V&V.** Deliverable: Transport dossier. Action: pre-shipment checklist. Phase: Pre-Transport.

## REQ_09 — Installation & Utilities Hook-Up
**Description.** The Applicant shall install equipment to fiducials consistent with the approved 3D model/layout drawings, and complete auxiliary hook-ups (cooling water, oil recovery, heat-recovery integration, HVAC exhaust ducting, main electrical supply). For HP compressors, the Applicant shall provide contractor-side harmonic compensation hardware/software meeting site power-quality requirements.
**Rationale.** Ensures fit, function, and grid compliance.
**V&V.** Deliverable: As-installed survey vs model; power-quality report. Action: site QA checks. Phase: Installation.

## REQ_10 — Controls & IT Integration
**Description.** The Applicant shall integrate with UBMS (building management), MCS, MIS, and MSC (safety-critical) per interface control documents; MIT/site IT requirements (networking, cybersecurity) shall be implemented consistent with ISO 27001 practices.
**Rationale.** Safe, secure, and operable system integration.
**V&V.** Deliverable: ICDs, network diagrams, cyber checklist. Action: integration tests. Phase: Installation→Commissioning.

## REQ_11 — FAT/SAT & Performance Acceptance
**Description.** The Applicant shall conduct FAT (factory) and SAT (site) with objective acceptance criteria (capacity, stability, response, I/O correctness, timing/speed) and a Performance Test protocol tied to contract metrics; nonconformities shall be tracked to closure.
**Rationale.** Objective proof of compliance before handover.
**V&V.** Deliverable: FAT/SAT procedures & reports; NCR log. Action: witnessed tests; pass/fail summary. Phase: Commissioning.

## REQ_12 — Operations Readiness & Handover
**Description.** The Applicant shall supply O&M manuals, training, spare-parts lists, warranty terms, preventive maintenance plan (ISO 55000 mindset), and updated as-built docs; residual risk and open items shall be accepted or mitigated before handover.
**Rationale.** Stable transition to operations with managed residual risk.
**V&V.** Deliverable: ORR checklist; training records; as-builts. Action: handover board sign-off. Phase: Operational Readiness.
