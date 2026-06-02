# Pyscript

Use this when Home Assistant has `pyscript:` in `configuration.yaml`, when `/config/pyscript` exists, or when the user asks to manage Python-based HA automations.

Installation and custom integration setup belong to `haos-addons`. This reference is for using and maintaining scripts after Pyscript is installed.

## References

- Official docs: `https://hacs-pyscript.readthedocs.io/en/latest/`
- Official repository: `https://github.com/custom-components/pyscript`
- Key docs sections to check before non-trivial code: configuration, reloading scripts, state variables, calling services, `@state_trigger`, `@event_trigger`, importing, tasks, and avoiding event-loop I/O.

## Inventory

```sh
ssh haos 'grep -n "^pyscript:" /config/configuration.yaml || true'
ssh haos 'find /config/pyscript -maxdepth 4 -type f -name "*.py" -print 2>/dev/null | sort'
ssh haos 'find /config/pyscript -maxdepth 1 -type f -name "*.py" -exec sed -n "1,220p" {} \; 2>/dev/null'
```

Treat `/config/pyscript/*.py` as automation configuration, not as an unrelated script folder.

## Ownership

Use Pyscript for always-enabled logic that is clearer as code than as many YAML automations, such as:

- event bus adapters
- state mirror synchronization
- retry and timeout logic
- repeated service-call helpers
- compact bridge code across multiple devices

Keep UI automation when the user needs easy toggling, visual traces, or one-off rules that are naturally edited in HA UI.

## Layout

Pyscript is not a normal standalone Python project. Keep the layout aligned with how Pyscript loads files:

- Put trigger-bearing automation code in top-level `/config/pyscript/*.py`, `scripts/`, or configured apps.
- Put shared helper modules under `/config/pyscript/modules/`.
- Do not expect helper modules to autoload. They are imported by top-level scripts.
- Keep local draft copies only as drafts. HA runtime state is whatever is deployed under `/config/pyscript` and loaded by HA.
- During staged migration, keep old YAML and new Pyscript from owning the same transition at the same time. Use explicit enable flags or only enable one side during testing.

Example generic layout:

```text
/config/pyscript/
  bridge.py
  modules/
    bridge_lib/
      __init__.py
      config.py
      helpers.py
```

## Writing Patterns

Prefer small helpers and explicit state/event names:

```python
def emit_event(notify_entity: str, name: str) -> None:
    service.call("notify", "send_message", entity_id=notify_entity, message=name)
```

Use explicit names for command events, observed status events, acknowledgements, and failures. Do not use one event name for both command intent and observed state.

Use Pyscript APIs for HA work:

- Use `state.get(entity_id)` and `state.getattr(entity_id)` when the entity id is dynamic.
- Use `service.call(domain, service, **data)` when the service is dynamic or easier to keep generic.
- Use `task.sleep()` and `task.wait_until()` for waits. Do not use blocking sleeps.
- Avoid blocking network or filesystem I/O in the event loop. If external I/O is required, read the official docs section on executor/off-loop patterns first.
- Guard `unknown`, `unavailable`, and first-load `None` transitions when mirroring device state.
- For bridge code, separate inbound command handling from outbound observed-state sync.
- For logic that should run when Pyscript loads or reloads, use `@time_trigger("startup")`. Do not directly translate a YAML Home Assistant start trigger into an `@event_trigger` unless the actual HA event timing has been verified.

## Import Guidance

Pyscript has its own importer and security model, so do not assume ordinary CPython package behavior.

- Keep `allow_all_imports` disabled unless the script genuinely needs external Python imports.
- Import local shared code from `/config/pyscript/modules`, for example `from bridge_lib.helpers import emit_event`.
- Avoid relative imports inside helper modules unless they have been verified on the target HA instance. Prefer a simple dependency direction where top-level scripts import leaf helper modules.
- If a helper module must depend on another helper module, prefer absolute imports from the `modules` root and verify with a Pyscript reload plus logs.
- If Pyscript reports `ModuleNotFoundError: import from ... not allowed` or `attempted relative import with no known parent package`, simplify the helper graph before enabling broad imports.
- Do not enable `allow_all_imports` just to fix local helper imports. That option is for importing external packages and broader Python modules, not for papering over Pyscript layout mistakes.

Minimal safe shape:

```python
from bridge_lib.config import ENABLED, TARGET_ENTITY
from bridge_lib.helpers import is_enabled


@state_trigger(f"{TARGET_ENTITY} == 'on'")
def target_on(value=None, old_value=None, **kwargs):
    if not is_enabled(ENABLED, "target_on"):
        return
```

Helper module:

```python
def is_enabled(enabled_map: dict[str, bool], rule_name: str) -> bool:
    return enabled_map.get(rule_name, False) is True
```

## Triggers And Services

Keep trigger functions thin:

- read the event or state
- check an enable flag or ownership guard
- call a named helper or service function
- log enough to debug when needed

Prefer conservative state triggers for mirrors. For example, only emit an "opened" event when the old state was definitely `off`, and ignore first-load or unavailable transitions unless startup sync explicitly owns initialization.

For service-like functions exposed by Pyscript, use clear names and avoid accidental service registration for internal helpers. Keep internal helper names ordinary and put external entry points behind `@service` only when the user needs to call them from HA.

## Staged Migration

When migrating YAML automation to Pyscript:

1. Inventory YAML, scripts, UI-owned automations, and existing Pyscript files.
2. Write the Pyscript equivalent with all new rules disabled or otherwise inert.
3. Deploy to `/config/pyscript`.
4. Reload Pyscript and inspect logs before disabling YAML.
5. Disable one YAML automation.
6. Enable only the corresponding Pyscript rule.
7. Test that one rule and inspect logs/traces.
8. Repeat one rule at a time.
9. Remove YAML only after the Pyscript path has been verified and rollback is clear.

Do not delete the previous owner during the same step that introduces the new owner.

## Reload And Logs

After editing Pyscript files, run config check when configuration changed. Then reload Pyscript through the HA integration reload path or the Pyscript reload service if available in that HA instance.

Useful paths:

- HA UI Developer Tools actions: call `pyscript.reload`.
- HA UI integration page: reload the Pyscript integration when available.
- HA Core restart: use only when reload is unavailable, failed, or the integration does not pick up changed files.

Inspect logs:

```sh
ssh haos 'ha core logs | grep -i pyscript | tail -n 120'
ssh haos 'ha core logs | grep -i "pyscript\|<script_name>\|<module_name>" | tail -n 160'
```

File watchers may not always produce a clean reload after a failed import or after changing only helper modules. If logs still show an old import line, touch or redeploy the top-level script, call `pyscript.reload`, and only then consider HA Core restart.

Successful reload evidence can be either an explicit loaded/reloaded log line or the absence of new Pyscript errors after a reload/restart window. Do not treat stale errors from before the latest reload as current failures.

## Safety

- Keep secrets in HA secrets or integration options, not in Python source.
- Do not enable broad imports unless the code actually needs them.
- Do not let both Pyscript and YAML automation own the same state transition without an explicit owner note.
- Do not test destructive services while proving Pyscript loading. First verify load, then a harmless service call, then the real automation path.
- Back up changed Pyscript files before edits just like YAML configuration.

## Verification Checklist

Before reporting success:

- Confirm `/config/pyscript` deployment matches the intended file layout.
- Confirm all staged rules are disabled if the user asked for a disabled draft.
- Run `ha core check` when `configuration.yaml` changed.
- Reload Pyscript or restart HA Core if reload is unavailable.
- Inspect logs after the reload or restart window.
- For behavior changes, verify with entity state, service result, automation trace, or a safe end-to-end test.
