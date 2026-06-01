# Source Map

Use this reference when the user asks where the guidance came from or when the public behavior needs refreshing. Prefer current official UI and docs over these links if they conflict.

Do not keep separate video notes by default. When a video teaches a reusable concept, fold that concept into the relevant topic reference and mention the video near that section. Use this file only as the source index and refresh map.

## Official Or Semi-Official Entry

- `https://www.asmslight.com/41.html` - Reposted 米家 launch note. Useful for the entry path: central gateway requirement, same-LAN computer, main gateway plugin, login code, Chromium browser, and virtual events as a bridge.

## Text Guides And Cases

- `https://inkss.cn/post/78a787b3/` - 米家自动化极客版使用指南. Useful for card concepts, custom state, variables, loops, and caution around loop use.
- `https://inkss.cn/post/430ddf15/` - 米家中枢自动化极客版案例分享. Useful for practical patterns such as traditional-device integration, camera position correction, movie mode, washing machine completion, and air-conditioner door/window reminders.
- `https://phuker.github.io/posts/xiaomi-central-gateway-thermostat.html` - 恒温控制 example. Useful for a larger system that mixes geek mode, virtual events, central gateway logic, and 米家 App controls.

## Home Assistant Bridge References

- `https://github.com/XiaoMi/ha_xiaomi_home` - Official Xiaomi Home Integration for Home Assistant. Useful for the current Xiaomi-supported HA integration, OAuth login, cloud/local messaging architecture, and limitations such as unsupported Bluetooth, infrared, and virtual devices.
- `https://www.home-assistant.io/integrations/xiaomi_miio/` - Home Assistant built-in Xiaomi Home / miio integration docs. Useful for legacy Xiaomi gateway and device setup, Mi Home prerequisite, and subnet/VLAN caveats.
- `https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger` - HA webhook trigger docs. Useful when a verified Xiaomi-side action can call an HA local webhook.
- `https://www.home-assistant.io/integrations/mqtt/` - HA MQTT integration docs. Useful when a bridge publishes events into HA through Mosquitto or another MQTT broker.
- `https://www.home-assistant.io/integrations/rest_command/` - HA RESTful Command docs. Useful when HA needs to send HTTP requests outward from scripts or automations.
- `https://www.home-assistant.io/integrations/matter/` - HA Matter docs. Useful for distinguishing HA as a Matter controller from third-party Matter bridge add-ons that may expose HA entities outward.

## Integrated Video Tutorials

- `https://www.bilibili.com/video/BV1wM411k7g6/` -> setup requirements, App/geek-mode independence, device schedulability, graph layout and editing tips.
- `https://www.bilibili.com/video/BV1ag411n72L/` -> main-gateway login code, same-LAN requirement, event/state distinction, query-on-rule-start, event-to-state workarounds, device-property relays.
- `https://www.bilibili.com/video/BV1yM411c7nR/` -> basic graph execution, active trigger cards versus passive query cards, port colors, fan-out and input rules.
- `https://www.bilibili.com/video/BV1thiQBSE8Z/` -> virtual events as App/geek-mode bridge, text-matched event naming, App-only trigger categories, finer App scene control.
- `https://www.bilibili.com/video/BV1oH4y1a7r6/` -> variable scope/type conventions, six variable card patterns, numeric operation, text concatenation, temperature-difference example.
- `https://www.bilibili.com/video/BV1TSoYB7EXK/` -> 米家 App execution loops, finite versus always-loop modes, action order, and current local/cloud verification caution.
- `https://www.bilibili.com/video/BV1fYruYiE26/` -> official `ha_xiaomi_home` bridge pattern: HA watches central-gateway virtual-service event-name changes to run HA scripts, and HA can emit central-gateway virtual events back into 米家/geek mode.
- `https://www.bilibili.com/video/BV1NwNLexEqt/` -> state-machine caveat for HA-watched virtual events: repeated same event names may not retrigger because the observed event-name value did not change. Use alternating or reset values.
- `https://www.bilibili.com/video/BV1gYKHepEoE/` -> HA-side acknowledgement/failure feedback pattern: HA emits success events after script completion, while geek mode uses variables and delays to announce timeout/failure.
- `https://www.bilibili.com/video/BV1pXE9zHEvW/` -> four-month Xiaomi Home integration experience: official integration supports many Xiaomi entities, central-gateway local mode depends on gateway/software support, LAN control covers only IP devices, and HA HomeKit Bridge can selectively expose HA entities to Apple Home.

## Indexed But Not Yet Distilled

- `https://www.bilibili.com/video/BV1nm4y1k78U/` - 米家自动化极客版 full-series playlist from 我是你八哥啊. Potentially useful for virtual states, App interop, logs, custom cards, count cards, delay interruption, loops, and practical cases.
- `https://www.bilibili.com/video/BV1FW4y1p7SM/` - Introductory tutorial series. Potentially useful for onboarding if the current setup notes are not enough.
- `https://www.bilibili.com/video/av479852970/` - Tutorial series referenced in search results for basic logic, logs, device cards, time cards, flow cards, logic cards, and variable cards. Basic logic has been distilled from BV1yM411c7nR, but dedicated log/device/time/flow/logic-card deep dives have not yet been fully distilled.

## Known Gaps

- Dedicated log-reading tutorial content has not been separately distilled. The current log guidance is inferred from graph-review practice and available tutorials.
- Device cards, time cards, flow cards, and logic cards are covered at the concept level, but not as a complete card-by-card catalog.
- The GreasyFork helper script is indexed but not yet turned into a workflow for inspecting device, variable, and automation references.
- 米家 -> HA and HA -> 米家 bridge behavior has been documented at the architecture-pattern level. The official Xiaomi Home central-gateway virtual-event path is now represented as a verified tutorial pattern, but exact HA entity/action names must still be checked in the user's live HA instance.
- No current official/public source in this index confirms a generic 米家 App or geek-mode HTTP/MQTT outbound action. Keep direct HTTP/MQTT from Xiaomi as a live-UI verification item rather than a default assumption.

## Helper And Capability References

- `https://greasyfork.org/scripts/495520-%E7%B1%B3%E5%AE%B6%E4%B8%AD%E6%9E%A2%E6%9E%81%E5%AE%A2%E7%89%88%E5%8A%A9%E6%89%8B/code` - 米家中枢极客版助手 userscript. Useful for finding which devices, variables, and automations reference each other on the geek-mode page.
- `https://mijia.wiki/` - Community device capability pages. Useful for checking possible device event/state/action definitions, while remembering exact geek-mode availability depends on central-gateway local support.

## Refresh Guidance

Refresh sources when:

- The user asks about a new gateway, router gateway, or firmware behavior.
- A device's trigger/action support is central to the answer.
- The question depends on whether execution is local or cloud.
- The public UI changed.
- A tutorial claim conflicts with the user's current page.
