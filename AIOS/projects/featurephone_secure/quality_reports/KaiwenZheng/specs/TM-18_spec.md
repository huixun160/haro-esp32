# Frozen Specification — TM-18: AIOS Workflow Feedback Exit Path

## MUST
- [ ] Create `AIOS/feedback/` directory
- [ ] Create `workflow/templates/feedback_template.md` with sections: Execution Summary, Completed Work, Incomplete Work, Blocking Issues, Verification Status, Next Actions
- [ ] Create `workflow/skills/close-feedback.md` defining the procedure for generating feedback artifacts
- [ ] Extend the existing aios-close workflow to include feedback generation step
- [ ] Define three terminal outcomes: SUCCESS, PARTIAL, BLOCKED
- [ ] Naming convention: `AIOS/feedback/TM-XXX-feedback.md`
- [ ] Generate example feedback artifact: `AIOS/feedback/TM-018-feedback.md`

## SHOULD
- [ ] Feedback generation should be automated (minimal manual effort)
- [ ] Template should include metadata fields (date, memo ref, outcome, author)

## MAY
- [ ] Add a retroactive TM-15 feedback artifact as a second example

## OUT OF SCOPE
- Automated failure classification agents
- Failure analytics dashboards
- CI integration for feedback validation
- Advanced telemetry or build pipeline reporting
