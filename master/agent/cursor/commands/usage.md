---
name: usage
description: 查看当前账号的本月 Cursor 用量
---

# Cursor 用量

运行本地 Cursor usage 脚本，并把脚本的标准输出原样粘贴回用户。不要改写、压缩或重新总结脚本输出。脚本输出固定使用这个模板：

````markdown
# 周期统计

* 统计周期：...
* 生成日期：...
* Tokens：总计 ... tokens，输入 ... tokens，缓存 ... tokens，输出 ... tokens
* 额度：$.../$2,000 (...% used)
* Dashboard：...

# 每日用量趋势

```text
...
```

# 按模型统计

* gpt-5.5-medium：...
* composer-2.5：...
````

必须保留 `# 每日用量趋势` 和紧随其后的柱状图代码块。如果需要补充中文说明，只能在完整脚本输出之后追加一句很短的说明。

默认使用这个命令。它统计当前月用量，输出每日用量柱状图，并附上 Cursor Dashboard 链接：

```bash
node "/Users/bytedance/Documents/agent-dotfiles/master/tools/cursor-usage/cursor-usage.mjs"
```

规则：

- 不要打印、保存或上传 Cursor token。
- 不要调用第三方 dashboard 或服务。
- 如果脚本提示登录失效，告诉用户重新登录 Cursor 后再运行 `/usage`。
- 如果用户要求机器可读输出，给同一个脚本加 `--json`。
- 如果用户要求滚动时间窗口，传 `--days=N`，例如 `--days=7`。
- 如果用户要求完整导出范围，传 `--all`。
