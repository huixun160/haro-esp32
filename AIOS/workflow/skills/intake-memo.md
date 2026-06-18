# Skill: Intake Memo

## Purpose
Parse a Technical Memo and extract structured information for downstream processing.

## Input
A Technical Memo document (markdown).

## Procedure

1. Read the memo in its entirety
2. Extract the following fields:
   - **Title** — the memo title
   - **Objective** — what the memo aims to achieve
   - **Scope** — what is in scope
   - **Out of Scope** — what is excluded (if stated)
   - **Constraints** — technical or process constraints
   - **Deliverables** — expected outputs
   - **Verification Requirements** — how to validate success
   - **Potential Risks** — known risks or dependencies
   - **Background / Context** — any additional context
3. Present the extracted information as a structured summary
4. Identify any fields that are missing or incomplete
5. Flag missing fields for the `clarify-memo` skill

## Output
Structured memo summary with completeness assessment.
