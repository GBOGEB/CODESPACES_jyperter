# Master_0602 System Integration Requirements

## 3.8 Ancillary Equipment Integration

### 3.8.1 Specific Requirements for the Warm Compressor Station (WCS) – Interface Considerations
The Applicant shall define and analyze interface requirements for the WCS and supporting infrastructure, ensuring seamless integration with Client-provided utilities and cooling systems. Interface considerations shall cover:
- **Electrical Supply and Controls:** Power demand, redundancy planning, and integration with the existing electrical grid.
- **Cooling Systems (Water, Air, and Heat Recovery):** Assessment of cooling loads, required heat extraction rates, and interactions with PS01 (Primary Cooling System) and HV06 (Heat Recovery System).
- **HVAC Exhaust and Ventilation Strategies:** Airflow control for temperature regulation and heat rejection.
- **Heat Integration with Adjacent Process Systems:** Optimization of waste heat recovery and mitigation of thermal losses.

### 3.8.2 HP Compressors: Performance & Integration Analysis
The Applicant shall provide a comprehensive evaluation of HP compressors, focusing on their impact on system cooling, heat rejection, and overall reliability. The analysis must address:
- **Thermal Management & Heat Dissipation:** Heat rejection to the environment and cooling water interfaces; integration with Client-provided inlet and outlet cooling water terminal points.
- **Internal Cooling Piping Distribution:** Contractor scope of internal piping for compressor cooling and LOD 100 3D modeling within equipment layout drawings.
- **Flow Rate & Load Quantification:** Minimum, nominal, and maximum operational envelopes for compressor flow rates; impact of pressure variations and temperature conditions on compressor operation.
- **Cooling Strategies for Performance Optimization:** Evaluation of heat rejection strategies to maximize compressor lifecycle and efficiency.
- **Long-Term Operational Strategy: 72 Hz vs. 60 Hz Operation:** Flexibility in compressor frequency control demonstrating maximum flow and pressure at ~72 Hz, reduced load operation at 60 Hz, inventory management and recovery strategies in conceptual design, minimum turndown capabilities, and impact of compressor speed on skid reliability with justification for N+1 redundancy for critical operations and performance considerations for N or derogated state operation.

### 3.8.3 PVPS Vacuum Pumps: Performance Evaluation & Integration
The Applicant shall perform a quantitative assessment of PVPS vacuum pumps, evaluating their suitability for continuous operation, redundancy, and integration with auxiliary systems. The analysis must include:
- **Pumping Capacity & Operational Limits:** Performance evaluation across various operating conditions and redundancy strategies for N-1 interim and periodic maintenance.
- **Technology Justification & Cost-Benefit Analysis:** Technical rationale for selecting dry vs. oil-based vacuum pumps and lifecycle cost assessment balancing performance, reliability, and maintenance.
- **Heat Load & Thermal Management:** Quantification of heat dissipation to air and water and impact on cooling water flow and overall system efficiency.
- **Integration with Auxiliary Systems:** Compatibility with HVAC, cooling loops, and dynamic load adjustments; assessment of turn-down capabilities and very low pressure (VLP ~24 mbar) feasibility.
- **Control & Safety Considerations:** CC recovery assistance in conceptual design, safety interlocks and fail-safe instrumentation to prevent operational failures, and analysis of upset conditions including loss of offsite power and loss of pneumatic instrument air.

### 3.8.4 Heat Recovery System: 3D Layout & Auxiliary Interfaces
The Applicant shall develop a conceptual design for the Heat Recovery System, including 3D representations and key interface identification. The system must:
- Optimize integration of HP compressor waste heat into the Client’s hot water network.
- Define auxiliary interfaces with Client’s HVAC and utility systems.
- Characterize flow rates and temperature profiles of recovered heat streams.
- Establish a control strategy for balancing cooling water (PS01) vs. HV06 heat integration.
- Optimize space and layout for future expansion, such as adding an extra HP compressor skid for N+1 redundancy to improve uptime and mitigate helium inventory loss while supporting recovery.
- Develop overheating and energy utilization mitigation strategies.
- Identify critical I/O signals required for interface management and automation.

### 3.8.5 Process Cooling System (PS01 & HV06) – Functional Role & Interfaces
The PS01 and HV06 heat sinks must be seamlessly integrated to ensure optimal process cooling performance.
- **PS01 (Primary Cooling System):** Primary and most reliable heat sink for system cooling providing supply and return headers and terminal points inside the WCS room.
- **HV06 (Secondary Heat Sink):** Designed for sustainable operation and energy conservation, functioning as an alternative cooling path to optimize thermal balance.
Both systems must be designed to accommodate variable loads and process conditions, ensuring reliable operation and minimal downtime risks.

### 3.8.6 HVAC Scope Boundary Definition
The Contractor shall define the HVAC system boundary and quantify critical parameters to ensure effective heat dissipation and ventilation for the Warm Compressor Station (CCB). The cooling strategy must:
- Accommodate both ambient and direct air cooling.
- Provide a structured breakdown of heat loads and airflows.
- Validate residual heat loads (in kW) released into the compressor room.
- Define exhaust integration with HVAC ducting, ensuring proper exhaust panel location, size, and compatibility.
- Establish proper airflow management, preventing recirculation of heated air within the compressor room.
- Integrate system interlocks to detect and mitigate blockages or restricted airflow.

### 3.8.7 System Alarms, Interlocks & System Integration
The Applicant shall define and implement alarms, interlocks, and permissives within the control system to ensure robust system protection and operational reliability.
- **Critical System Alarms & Interlocks:** Detection of flow loss, temperature deviations, and pressure faults; HVAC overpressure and over-temperature conditions; loss of pneumatic supply, electrical faults, and UPS battery backup failures; interlocks for valve position control ensuring safe and reliable isolation mechanisms.
- **Integration with Existing Control & Monitoring Systems:** Full integration with QPLANT and Client automation infrastructure, ensuring data acquisition from all critical systems is properly formatted and structured.

### 3.8.8 Piping & Distribution Layout
The final piping and cabling distribution layout shall be delivered by the end of the Conceptual Design Phase, ensuring structured spatial integration. Minimum deliverables include:
- 2D layout and assembly drawings detailing piping and cooling interconnections and penetrations (roof/wall) with execution details for Client review.
- Spatial integration requirements for all critical process components.
- Hardwired and software interlocks to detect loss of cooling accident (LOCA) scenarios.
- Definition of fault scenarios, recovery strategies, interlocks, and alarm triggers.

