# Skill: Record API

## Purpose
Register a discovered or implemented API into the AIOS API registry.

## Input
- API function name
- Metadata (as much as available)

## Procedure

1. **Gather metadata** for the API:
   - `api`: Function name (e.g. `DAP_RegisterApp`)
   - `layer_from`: Caller layer (APP / DAP / Adapter / OS)
   - `layer_to`: Callee layer
   - `owner`: Engineer or team (check `ownership.yaml`, use `TBD` if unknown)
   - `stability`: alpha / beta / stable / deprecated
   - `thread_context`: Expected calling context (e.g. `app_task`, `mmi_task`)
   - `input`: Parameter types (e.g. `app_manifest_t*`)
   - `output`: Return type (e.g. `int`)
   - `error_codes`: List of return codes (e.g. `[DAP_OK, DAP_EINVAL]`)
   - `description`: Brief description of the API's purpose

2. **Check for duplicates** — Ensure the API is not already in `registry/apis.yaml`

3. **Append to registry** — Add the new entry to `AIOS/registry/apis.yaml`

4. **Notify engineer** — Confirm the registration and highlight any `TBD` fields that need manual review

## Rules
- If metadata is incomplete, register with `TBD` values and flag for review
- Never remove existing registry entries without explicit engineer approval
- Maintain alphabetical order by API name in the registry

## Output
Updated `AIOS/registry/apis.yaml` with the new entry.
