# Skill: Clarify Memo

## Purpose
Generate targeted clarification questions for ambiguous or incomplete Technical Memos.

## Input
Structured memo summary from `intake-memo` skill, with flagged missing/ambiguous fields.

## Procedure

1. Review the memo summary for:
   - Missing objectives or deliverables
   - Ambiguous scope boundaries
   - Unspecified constraints
   - Missing verification criteria
   - Conflicting requirements
   - Unclear module ownership
2. For each issue, formulate a specific, actionable clarification question
3. Prioritize questions by impact on implementation

## Example Questions
- Which module should implement this API?
- Is legacy compatibility required for this feature?
- Should verification be done on the simulator, real device, or both?
- Does this API require versioning?
- What are the expected error conditions and error codes?
- Is there a performance constraint (latency, memory)?
- Which engineer owns the affected module?

## Output
Numbered list of clarification questions, ordered by priority.
