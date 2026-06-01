# Setup And Login

Use this reference when the user asks how to enter 米家自动化极客版, why the browser page does not open, what prerequisites are needed, or how to safely prepare the gateway before editing flows.

## Source Of Truth Order

1. The user's current 米家 App and central gateway plugin pages.
2. The local geek-mode browser page at the gateway IP.
3. Gateway logs and card-level logs.
4. Public tutorials and community posts.

Public tutorials establish common workflow, but the local UI decides what is available for the user's gateway firmware and devices.

## Basic Requirements

- A Xiaomi / Mi Home central gateway or device with central-gateway capability that exposes 自动化极客版.
- The gateway should be the active main central gateway in the home.
- Computer and gateway should be on the same LAN.
- Use a Chromium-based browser. The public 米家 launch note recommended Chromium 107 or newer, with Chrome and Edge as examples.
- Gateway firmware and plugin UI must support geek mode. Older public launch notes mentioned upgrading the central gateway to `2.0.0_0039` or later, but verify the current requirement in the user's 米家 App.

Reference: 易举不易, `抢跑米家极客版。小米终于出图形化编程编辑智能场景了，可玩性大大增加`, BV1wM411k7g6, and `米家极客版 番外篇之10大疑问解答`, BV1ag411n72L.

## Entry Flow

1. Open 米家 App.
2. Enter the central gateway device page.
3. Confirm which gateway is the main central gateway.
4. Enter the main gateway plugin.
5. Open more settings and find 自动化极客版.
6. Request a login code.
7. On the computer browser, visit the gateway LAN IP.
8. Enter the login code on the geek-mode page.

Do not ask the user to paste the login code into chat unless there is no alternative. Prefer asking them to enter it locally.

If the user cannot get a login code, first verify they entered the main central gateway. In multi-gateway homes, only the main gateway exposes the login-code path in the tutorial demonstration.

If the browser cannot open the page, first verify the computer and gateway are on the same LAN. The practical check is "same router / same local network", not merely "both devices have internet". Remote access or port forwarding is outside the normal safe path and should be treated as an advanced network task.

Refreshing the geek-mode page or reopening it may require entering a fresh login code again. Avoid assuming a long-lived browser session.

## First-Time Checks

After login, check:

- Whether existing automation list loads.
- Whether the card canvas opens.
- Whether logs can be viewed.
- Whether the target devices appear under card selection.
- Whether each target device exposes the needed event, state, query, or action.

Also inspect the device list. The geek-mode UI can show whether a device can be scheduled by the central gateway and whether it can act as a trigger. In the video walkthrough, devices failed central scheduling for three different reasons: not on the same LAN, offline, or not adapted for local control. Treat those as separate causes when debugging.

For Zigbee, Bluetooth Mesh, or other gateway-attached devices, the tutorials show they are often more likely to be both schedulable and trigger-capable, but do not generalize blindly. Always inspect the user's current device list.

For device capability questions, do not assume that a device's 米家 App feature is available in geek mode. Some devices can execute actions but cannot act as local triggers. Some App-only features require a virtual-event bridge.

## Privacy Boundaries

Treat these as private:

- Home LAN IPs and gateway IP.
- Login codes.
- Room names and household layout.
- Device names that reveal location or family habits.
- Xiaomi account identifiers.
- Screenshots containing family routines or security devices.

When creating reusable documentation, use generic names such as `客厅灯`, `观影模式`, `洗衣完成`, or `离家状态` unless the user explicitly asks to preserve exact names.

## Troubleshooting Entry Problems

- Cannot open gateway IP: verify same LAN, gateway online, correct main gateway, browser not forcing HTTPS, VPN/proxy not routing local addresses away.
- Login code rejected: generate a fresh code from the 米家 App plugin and retry soon.
- Empty or missing device cards: verify the device is bound to the same home, central gateway can see it, and the device supports the requested capability in geek mode.
- Page loads but operation fails: capture the card log and browser-visible error before changing the flow.

## Relationship To 米家 App Automations

Geek mode and 米家 App smart scenes are independent automation systems. If the App has `motion -> turn on light` and geek mode has `motion -> turn off light`, both may run and the final device state depends on ordering. When reviewing a user's behavior complaint, always ask whether a parallel 米家 App automation exists.

Use geek mode as a stronger canvas for complex local graph logic and use the App for App-only triggers or actions. Prefer virtual events for App/geek-mode bridging. Use a harmless device/property relay only as a fallback when no direct virtual-event path exists, and make that workaround visible in names or notes.
