# Rule: API Registration Required

All public APIs must be registered in `AIOS/registry/apis.yaml` before or during implementation.

When AI encounters a new API during implementation:
1. Record the API in `registry/apis.yaml` with all known metadata
2. Include: function name, layer_from, layer_to, owner, stability, input/output types, error codes
3. If any field is unknown, mark it as `TBD` and flag for engineer review

When AI encounters an existing API during a task:
1. Check if it is already registered in `registry/apis.yaml`
2. If not, register it using the `record-api` skill
3. If already registered, verify the metadata is still accurate
