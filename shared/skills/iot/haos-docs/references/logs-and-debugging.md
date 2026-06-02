# Logs And Debugging

Use this for HA runtime inspection after a config or automation change.

## Basic Checks

```sh
ssh haos 'ha core logs | tail -n 160'
ssh haos 'ha core info'
ssh haos 'ha supervisor info'
```

Filter carefully:

```sh
ssh haos 'ha core logs | grep -i "automation\\|pyscript\\|xiaomi\\|mqtt" | tail -n 120'
```

Do not paste secrets from logs into the final answer.

## Entity State

Use HA UI Developer Tools for precise entity state and attributes when possible. From SSH, prefer HA CLI only for broad checks because entity state inspection may require HA API access.

For a bridge issue, collect:

- inbound event entity and attributes
- target entity state before and after action
- outbound notification or service call result
- automation trace or Pyscript log entry

## Service Testing

Test the smallest safe service call before a full bridge flow:

- send a harmless notification
- call a non-destructive script
- query or observe state

Avoid testing destructive actions such as unlocking, opening, or disabling alarms unless explicitly authorized.

## Debug Report

Lead with findings:

- what fired
- what did not fire
- what state was observed
- what log line or trace proves it
- what minimal fix is recommended
