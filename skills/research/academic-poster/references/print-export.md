# Print Export

Final exports are always:

- editable PPTX
- PDF
- PNG

## DPI

Default to 300 DPI. If the user or conference provides final pixels or a lower submission limit, follow that requirement.

Compute final PNG dimensions from poster size:

```text
pixel_width = width_in * dpi
pixel_height = height_in * dpi
```

Example:

```text
52 x 39 inches at 300 DPI -> 15600 x 11700 px
```

A smaller image such as `5200 x 3900` is a 100 DPI export for the same physical size.

## Figure DPI

For each placed PDF-derived figure:

```text
required_px_width = element_width_in * target_dpi
required_px_height = element_height_in * target_dpi
```

The rendered PNG should meet or exceed these values. If it does not, rerender the PDF master at a higher DPI.

## QA Checks

Before delivery:

- PPTX exists and is non-empty
- PDF exists and is non-empty
- PNG exists and has expected dimensions
- PNG orientation matches poster canvas
- all referenced assets exist
- no obvious missing image placeholders
- figure derivatives meet required pixel dimensions
- final render has no visible clipping, overlaps, or unreadably small text

Automated checks do not replace visual inspection.
