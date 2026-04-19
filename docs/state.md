# State Schema

The LangGraph pipeline uses a shared `RetentionGraphState` (`TypedDict`) structure that flows through every node. 

## Keys and Lifecycle

State is built progressively. Here is a mapping of the state schema, ordered by the node that populates the fields.

### ── Input
- **`raw_csv_path`** (`str`): File path to raw uploaded data.
- **`questionnaire`** (`dict`): The onboarding form payload (budget, industry, legal constraints).

### ── Node 1: Input Ingest
- **`normalized_df`** (`list[dict]`): The ingested dataframe, serialized as list of dicts.
- **`input_context`** (`dict`): Contains column definitions (which column is id, tenure, etc.)
- **`input_constraints`** (`dict`): Parsed constraints.

### ── Node 2: Data Audit
- **`data_quality_score`** (`float`): Score from 0 to 1 representing data completeness.
- **`data_quality_logs`** (`list[str]`): Text descriptions of anomalies found during audit.

### ── Node 3: Feature Engineering
- **`feature_store`** (`dict`): Augmented data such as RFM scores, LTV predictions, CoxPH risk coefficients.

### ── Node 4: Behavioral Map
- **`behavior_curves`** (`dict`): Kaplan-Meier survival curve data. 
- **`behavior_cohorts`** (`list[dict]`): Risk/Usage segmented cohorts.

### ── Node 5: Diagnosis Pod
- **`forensic_detective_output`** (`dict`): Output from forensic agent.
- **`pattern_matcher_output`** (`dict`): Output from pattern agent.
- **`professional_skeptic_output`** (`dict`): Output from skeptic agent.
- **`diagnosis_results`** (`dict`): Merged output from the discovery pod.

### ── Node 6: Hypothesis Validation
- **`hypothesis_status`** (`str`): `"verified" | "weak_proof" | "unverified"`
- **`verified_root_causes`** (`list[dict]`): The final hypotheses validated against data.

### ── Node 7: Constraint Add
- **`constrained_brief`** (`dict`): Interventions filtered by cost and legal constraints.

### ── Node 8: Adaptive HITL
- **`hitl_questions`** (`list[str]`): Clarifying questions raised to the user.
- **`human_clarification`** (`dict`): The user's answers/feedback.

### ── Node 9: Strategy Pod
- **`unit_economist_output`** (`dict`): Recommended ROI-positive initiatives.
- **`jtbd_specialist_output`** (`dict`): Recommended initiatives based on jobs-to-be-done.
- **`growth_hacker_output`** (`dict`): Experimental activation approaches.
- **`strategy_outputs`** (`dict`): Ranked master list of recommendations.

### ── Node 10: Simulation
- **`simulations`** (`dict`): Monte-Carlo simulation result artifacts.
- **`lift_percent`** (`float`): Expected retention/LTV lift.

### ── Node 11: Strategy Critic
- **`critic_verdict`** (`str`): `"approved" | "low_lift" | "violation"`
- **`criticism`** (`dict`): The critic's line-by-line feedback.
- **`feedback`** (`str`): Overall textual feedback summary.

### ── Node 12: Execution Architect
- **`final_playbook`** (`dict`): The fully assembled 30-60-90 day retention playbook.
- **`playbook_status`** (`str`): Status flag for completion.

### ── Metadata / Control
*Note: Fields use `operator.add` or `_last_value` reducers to prevent conflict during parallel node execution.*
- **`errors`** (`list[str]`): Aggregated exceptions/warnings.
- **`current_node`** (`str`): Name of the currently executing component (used by UI for status streaming).
- **`retry_count`** (`int`): Count of data audit retries/loops.
- **`discovery_attempts`** (`int`): Count of hypothesis generation loops.
- **`iteration_count`** (`int`): Count of strategy critic review loops.
