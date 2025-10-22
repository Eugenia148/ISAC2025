# Performance Radar Visualization - Radial Bar/Beam Chart

## Overview

The Performance Radar is a radial bar/beam chart (not a polygon radar) that displays striker performance metrics across 5 axes. Each axis (sector) contains 2–4 thin bars representing different metrics, with bar length representing the percentile score (0–100).

## Chart Features

### 1. Sectors (5 Axes, 72° Each)

**Axis Order (Clockwise)**:
1. **Finishing Output** (0°) - Gold/Warm colors
2. **Chance Creation** (72°) - Mint/Green colors
3. **Ball Progression & Link Play** (144°) - Cool Blue colors
4. **Defensive Work Rate** (216°) - Clay/Brown colors
5. **Overall Impact** (288°) - Teal/Neutral colors

### 2. Bars (Radial Beams)

- **One bar per metric** within each sector
- **Angular thickness**: 2.5–3.0 degrees
- **Angle offsets** within sector: −6°, 0°, +6°, +12° (for 2, 3, or 4 metrics)
- **Fill color**: Medium shade of axis color family
- **Edge stroke**: Dark shade of axis color family
- **Rounded cap**: Simulated at bar tip with value pill

### 3. Grid & Layout

- **Canvas**: Square, 600×600 px
- **Inner circle**: ~10% radius (empty, clean look)
- **Concentric rings**: At 20%, 40%, 60%, 80%, 100%
- **Grid color**: Light grey (rgba(0,0,0,0.15))
- **No radial spokes**: Sector titles only (clean aesthetic)

### 4. Benchmark Rays

For each metric:
- **Dotted rays** at median and p80 values
- **Length**: 12–15 px
- **Gap**: ~6 px
- **Color**: Dark shade of axis family
- **Stroke width**: 1 px
- **Dash pattern**: Dotted (`:` style)

### 5. Value Pills

Displayed at each bar tip:
- **Position**: +6–10 px radially beyond bar
- **Background**: Dark shade of axis color
- **Text**: White/near-white, 10–11pt semi-bold
- **Padding**: 6–8 px horizontal, 3–4 px vertical
- **Border radius**: 6 px
- **Value format**:
  - If < 1: `0.41`
  - If >= 1: `65.07` or `1.54`

### 6. Axis Titles

- **Position**: Outside rim at r ≈ 108–112
- **Font**: 12–13pt, color = axis family dark
- **Rotation**: Tangential (readable)
- **Alignment**: Center

### 7. Tooltips

On hover of a bar:
```
Axis • Metric Label
Raw: <value with 2 decimals>
Percentile: <0–100>
Median: <value>
P80: <value>
```

### 8. Minutes Badge

If player minutes < 600:
- **Style**: Yellow chip at top-left
- **Text**: `"Low minutes (<600'); percentiles may be noisy"`
- **Color**: Warning orange/yellow

## Color Scheme

| Axis | Light | Medium | Dark |
|------|-------|--------|------|
| **Finishing Output** | #FFF3E0 | #FFB74D | #E65100 |
| **Chance Creation** | #E0F2F1 | #4DB8AC | #00695C |
| **Ball Progression** | #E3F2FD | #64B5F6 | #0D47A1 |
| **Defensive Work** | #EFEBE9 | #A1887F | #3E2723 |
| **Overall Impact** | #E0F7FA | #4DD0E1 | #00838F |

## Geometry Calculations

### Angle for Metric

```python
axis_angle = axis_index * 72  # Each axis: 72° (360/5)
metric_offset = {2: [-3, 3], 3: [-6, 0, 6], 4: [-6, 0, 6, 12]}[num_metrics]
metric_angle = axis_angle + metric_offset[metric_index]
```

### Pill Position

```python
pill_radius = metric_percentile + 8  # Offset from bar tip
pill_x = pill_radius * cos(metric_angle - 90°)
pill_y = pill_radius * sin(metric_angle - 90°)
```

## Performance Data

### Data Input (PerformanceProfilePayload)

```json
{
  "player": { "id": 123, "name": "Player", "minutes": 1200 },
  "season": "2024/25",
  "axes": [
    {
      "key": "finishing_output",
      "label": "Finishing Output",
      "score": 72,
      "metrics": [
        {
          "label": "Touches in Box /90",
          "raw": 4.8,
          "percentile": 76,
          "benchmarks": { "median": 4.2, "p80": 5.6 }
        },
        ...
      ]
    },
    ...
  ],
  "minutes_threshold": 600
}
```

### Metrics per Axis

#### 1. Finishing Output (4 metrics)
- Touches in Box /90
- NP xG /90
- xG / Shot
- PS xG – xG (Finishing Quality)

#### 2. Chance Creation (4 metrics)
- xA /90
- Key Passes /90
- OBV Pass /90
- xA / Key Pass

#### 3. Ball Progression & Link Play (4 metrics)
- Deep Progressions /90
- Passing Ratio
- Dribble Ratio
- OBV Dribble /90

#### 4. Defensive Work Rate (3 metrics)
- Defensive Actions /90
- Tackles & Interceptions /90
- Aerial Ratio

#### 5. Overall Impact (3 metrics)
- NP xG + xA /90
- OBV /90
- Positive Outcome Score

## Rendering Implementation

### Plotly Polar Approach

1. **Figure Base**
   ```python
   fig = go.Figure()
   polar = {
       "radialaxis": {
           "range": [0, 100],
           "tickvals": [20, 40, 60, 80, 100],
           "gridcolor": "rgba(0,0,0,0.15)"
       },
       "angularaxis": {"visible": False}
   }
   ```

2. **For Each Metric**
   ```python
   # Create bar as filled wedge
   theta = [angle - 1.25, angle - 1.25, angle + 1.25, angle + 1.25]
   r = [0, percentile, percentile, 0]
   
   # Add trace
   fig.add_trace(go.Scatterpolar(
       theta=theta, r=r, fill='toself',
       fillcolor=color, line={"color": dark_color}
   ))
   
   # Add benchmarks
   fig.add_trace(go.Scatterpolar(
       theta=[angle-1.5, angle+1.5],
       r=[median, median],
       line={"dash": "dot"}
   ))
   
   # Add value pill
   fig.add_annotation(
       x=pill_x, y=pill_y,
       text=raw_value,
       bgcolor=dark_color
   )
   ```

3. **Axis Titles**
   ```python
   annotations.append({
       "x": title_x, "y": title_y,
       "text": axis_label,
       "font": {"color": axis_dark_color}
   })
   ```

## Edge Cases

### Missing Metric
- Draw faint placeholder bar to r ≈ 5 (grey fill)
- Pill shows "—"
- Tooltip: "Insufficient data"

### Zero Value
- Draw slim outline at r = 0
- Still hoverable with tooltip

### Pill Overlap
- Stagger radial offsets: +6 px, +12 px, +18 px
- Cascade outward if needed

### Out-of-Bounds Pills
- Clamp pill position within canvas bounds
- Position slightly inside bar tip if overflow

## Toggle & Modes

### Percentile Mode (Default)
- Bar length = percentile (0–100)
- Benchmarks shown as dotted rays
- Value pill shows raw metric value
- Tooltip shows percentile

### Absolute Mode (Optional)
- Bar length = raw value normalized to [0, 1] range
- Uses `performance_minmax.json` for scaling
- Benchmarks hidden or scaled similarly
- Value pill shows raw metric value

## Performance Characteristics

- **Render time**: <200 ms (cached artifacts)
- **Smooth interaction**: Hover tooltips, zoom/pan (optional)
- **Responsive**: Fixed 600×600 canvas (no resizing)
- **Memory**: Minimal (vector graphics)

## Testing & Validation

✅ Chart renders 5 sectors with 2–4 bars each
✅ Bars scale to percentile values
✅ Dotted benchmark rays visible at median and p80
✅ Value pills display raw values at bar tips
✅ Axis titles outside rim, color-coded
✅ Minutes badge shows for <600' players
✅ Tooltips show all data correctly
✅ Clean, professional aesthetic matches design

## Next Steps

- Performance comparison overlay (multiple players)
- Export chart as image (PNG/SVG)
- Animate bar transitions on data update
- Interactive legend/filter by metric
- Drill-down to detailed statistics
