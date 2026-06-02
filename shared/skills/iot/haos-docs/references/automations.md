# Automations

Use this for HA YAML automations, UI-managed automations, scripts, and automation inventory.

## Inventory

Start with:

```sh
ssh haos 'sed -n "1,220p" /config/configuration.yaml'
ssh haos 'sed -n "1,260p" /config/automations.yaml'
ssh haos 'sed -n "1,220p" /config/scripts.yaml'
```

If Pyscript is configured or `/config/pyscript` exists, inspect those scripts too.

## UI-Managed Automation Files

HA UI automations often live in `automations.yaml` with generated `id` fields. Preserve those ids unless the user wants to replace the automation.

When reviewing:

- Check trigger ownership.
- Check conditions and template assumptions.
- Check action order.
- Check `mode`.
- Check whether a rule should be disabled, deleted, or migrated.
- Check `last_triggered` in the UI or entity attributes when behavior is unclear.

## Scripts

Use `scripts.yaml` for reusable HA action sequences. Keep scripts generic when multiple automations call the same action path.

Do not hide core device semantics in scripts without naming. A script name should reveal whether it is a command, state sync, acknowledgement, or utility action.

## Reload

After editing automation or script YAML, run `ha core check` first. Then reload the smallest surface through UI services or HA Core reload.

If reload behavior is uncertain, prefer a Core restart only after a successful config check and after warning the user about brief downtime.

## Review Risks

- Event names do not exactly match across systems.
- A state mirror is written by command intent instead of observed device state.
- Startup or unknown-state recovery is missing.
- A repeated event is ignored because the observed event-state value did not change.
- `mode: single` drops a legitimate repeat command while a previous command is still waiting.
- A UI automation and a Pyscript both own the same trigger.
