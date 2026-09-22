# Spoken notes

`notes/slideNN.md` contains only the full spoken script. No “口播稿” heading, timing block, source bibliography, layout instructions, checklist, or stage directions. The exporter inserts the entire file into the corresponding PowerPoint speaker notes without selecting a section or summarizing it. Markdown syntax is kept as literal text, not rendered as rich text.

Use natural paragraphs in the user's speaking language. For Chinese talks, retain established model names, method names, formulas, and useful on-slide terms. Do not mechanically replace natural Chinese with English phrases. For example, “把物体名称和对应的三维位置关联起来” may be easier to say than “进行 object binding”. Keep one consistent name for each important concept.

## Page-to-page continuity

Before editing a note, read the preceding note's ending and the next note's opening. Put a transition in one place. If the next page begins “我们来看一个例子”, the previous page does not also need to announce that example. Avoid ending every page with a preview of the next.

The script should explain the visual, its reasoning, and necessary context rather than reading every label aloud. Introduce an unfamiliar symbol when it first becomes useful. Do not repeatedly explain the same example inputs on later pages. Preserve distinctions such as “what to solve” versus “how to solve” when they support the narrative, but do not add new claims or overstate what an illustration proves.

For experimental results, name the comparison and explain what it supports. Distinguish an empirical finding from an intuition or limitation. Keep historical model-strength claims tied to the experiment date when that matters.

## Timing

Count Chinese characters and English words separately as a rough audit. Do not treat raw Markdown length as spoken duration. A useful initial estimate for mixed technical Chinese is `Chinese characters / speaking rate + English words / speaking rate`, with rates calibrated to the speaker. Formula explanations, pauses, pointing, and transitions add time.

Use a range, not a guarantee. Read aloud representative dense pages and scale the estimate. If the talk is too long, remove repeated setup and secondary details before speeding up the delivery. Keep timing estimates in the storyboard, not the note files.

Missing notes export as blank with a warning, including the cover if appropriate. Use `--strict-notes` only when every exported page is expected to have a nonempty script. Do not invent filler narration just to satisfy a checker.
