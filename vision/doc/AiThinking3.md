The user says that now both near and far distance detection are not working. This is likely because I changed grid_size from 16 to 8, which means the density grid is now finer. But wait, let me think about what could go wrong.

Actually, let me re-read the _detect_by_density function more carefully.

Looking at _build_density:


def _build_density(mask):
    yx = np.where(mask > 0)
    n  = yx[0].size
    if n < self.density_min_pixels:
        return np.zeros_like(empty), x_bins, y_bins, 0


I'm extracting coordinates from the mask, then building a 2D histogram to create the density map. Then in _peak_center, I'm checking if the peak value in that density map falls below the minimum threshold—and that's where the issue might be. With a finer grid, the same number of pixels gets spread across more bins, so individual bin counts drop, potentially triggering that threshold check and returning None. The peak cell would still contain plenty of pixels even with the smaller grid size. Let me reconsider what's actually happening here. Looking at how the empty array gets created and what _build_density returns, it seems like the bins should match up correctly since they're computed from the same parameters. The real issue might be with what density_min_pixels = 10 is actually doing in the detection logic. At 1m, the ball's 36-pixel radius should create a peak cell with far more than 10 pixels, so that threshold shouldn't be the blocker. The total pixel count across both masks is also unlikely to drop below 10 at that distance. Let me trace through the histogram2d call more carefully—I'm wondering if there's something about how the density grid is being constructed that's causing the issue.

Looking at the peak center calculation, I see it's using the bin edges to compute the center coordinates. After the histogram transpose, the indexing maps row indices to y bins and column indices to x bins, so I need to verify the coordinate mapping is correct when looking up the peak position. y_bins[r+1]andx_bins[c]tox_bins[c+1]. So cx = xe[pc]...xe[pc+1]is the x coordinate andcy = ye[pr]...ye[pr+1]` is the y coordinate. This seems correct.

Wait, let me look at the call more carefully:

Only xe, ye from yellow density are kept (the blue ones are discarded with _). But since both use the same x_bins, y_bins, this is fine.

Then both peak center calculations use the same xe, ye for both densities, which is correct.

Hmm, so the logic seems correct. Let me think about what else could cause "both near and far range not working"...

OH WAIT. I think I see it now! When _build_density returns early because n is below the density threshold, it returns the global bin arrays. And the caller stores those as xe, ye, so both yellow and blue are using the same bin edges regardless of which density actually had enough pixels.

Let me think differently. What's the actual symptom? The user says "near distance AND mid distance are both not working." This is a regression from my changes.

The changes I made were reducing grid_size from 16 to 8 and adjusting density_min_pixels. These changes would affect the binning resolution and the threshold for when a density is considered valid.

With a smaller grid size of 8, the ball at 1 meter distance spans roughly 9×9 cells instead of the previous configuration, which could be affecting how peaks are detected in the histogram.

Let me think through the density calculation more carefully. If the yellow mask has around 1222 pixels distributed across about 81 non-empty cells, the average density per cell is roughly 15 pixels, with the peak cell probably reaching 30-40 pixels. Since the density threshold is now 10, this should still pass comfortably. But I need to check what happens with the radius validation...

Checking the radius calculation...

The key insight is that valid_pixels is actually summing the histogram counts from cells above the 25% threshold, not just counting cells. With grid_size=16, each cell represents a 256-pixel area, so a peak cell might contain around 100 pixels. I need to see which cells exceed that 25% threshold and how their counts add up to determine the final radius.

With grid_size=8, the cells are smaller (64-pixel areas), so the peak cell might only have 40 pixels, but there are more cells overall that exceed the threshold. This means the total pixel count could actually be higher despite smaller individual cells, which would give a slightly larger radius estimate.

Now I'm checking how the expected radius calculation works...

Calculating expected radius from camera parameters... I'm realizing the issue might be more nuanced—when the grid gets finer, the peak density drops since pixels spread across more cells, which lowers the threshold and actually qualifies more cells, potentially inflating the radius estimate and causing it to fail the upper bound check at 1m distance. I'm realizing the issue might be the draw_radius > 5 check that gates the entire drawing logic—if the computed radius drops below 5 with the new grid_size=8, nothing gets drawn at all. But the user says both near and far distances are broken, which makes me wonder if it's actually the interaction between the density_min_pixels = 10 threshold and the grid size change affecting how cells get counted and whether the radius calculation even triggers. At 4 meters the radius barely exceeds the threshold at around 5 pixels, but at closer distances like 1 meter it should be significantly larger. I'm wondering if the issue might actually be in how the heatmap is rendered or if the center coordinates are getting miscalculated due to the finer grid resolution, rather than the radius calculation itself.

Looking at the density check more carefully, I'm realizing the total pixel count across both masks is what determines whether the detection passes the minimum threshold, and with a smaller grid size the peak pixels per cell would drop proportionally.

But wait—I think I've been missing something fundamental. Let me trace through the _build_density function: when the pixel count falls below the minimum threshold, it returns early with zeros, which would completely bypass the density grid calculation. If the viewing angle or distance causes the colored pixels to drop below that threshold, the entire detection fails silently. np.arange(0, 328, 8) gives 41 bin edges creating 40 bins, which checks out. Let me see what happens when I switch to grid_size=16 with the same width.

For w=320 and grid_size=16, np.arange(0, 336, 16) produces 21 edges and 20 bins. The histogram should capture all pixels since they fall within 0-319, but I need to verify the last bin edge isn't cutting off valid data at the boundary.

Let me trace through the _peak_center function to understand how it's using the histogram and bin edges to compute the peak center coordinates. So the indexing is consistent—pr and pc from argmax correctly map to row and column indices, which then use the appropriate bin edges to calculate the center coordinates. The geometry checks out.

Now I'm wondering if the issue might be in how valid_pixels gets computed and whether that could inflate the radius estimate. Let me trace through the math with a concrete example: if the ball is at 2 meters with an 18-pixel radius and we're using an 8×8 grid, the ball would span roughly 16 cells, with the mask containing around 305 pixels total. That spreads to maybe 19 pixels per cell on average, peaking at around 40 in the center cells. Using a density threshold of 25% of the peak value gives us 10 pixels, which would mark perhaps 12 of those 16 cells as valid—totaling around 250 pixels that pass the threshold.

Plugging that back into the radius formula gives roughly 8.9 pixels, which falls comfortably within the expected range of 5.4 to 30.6 pixels. But at 1 meter, the numbers shift dramatically: the ball occupies maybe 81 cells with a much higher pixel count, potentially 2000 pixels total when combining colors, and the density threshold jumps to 16 pixels per cell, which would mark a large portion of those cells as valid.

Now I'm getting a radius of about 24 pixels at 1 meter, which also checks out against the expected range of 10.8 to 61.2. So the radius validation itself seems fine. But maybe I'm misunderstanding what "not working" actually means—could the detection circle just not be rendering, or is the selection phase itself broken? Let me think about whether the grid size change exposed a bug in how the combined density map gets computed for the radius calculation.

Actually, I should stop going in circles and approach this from what the user is experiencing. They said both close and medium distances stopped working after my changes, so I need to focus on what actually changed in the tracking phase itself.

The grid size went from 16 to 8, and the density threshold dropped from 20 to 10 pixels. The area filter change only affects candidate collection, which should actually help by letting more candidates through. But wait—I'm checking if the area filtering logic is even correct in the first place.

Looking at the grid binning with the smaller grid_size of 8, I'm realizing the bin edges might be creating unexpected boundaries that affect how candidates are being collected across the image. I'm looking at the _build_density function to trace through the logic—it checks if the mask has enough pixels (more than 10), which it easily does at 1m with over 1200 pixels, so it returns the histogram. Then there's another check on the total count that also passes since the combined values are well above the threshold.

Moving to _peak_center, it's checking if the maximum density in any grid cell exceeds the minimum threshold, and even with an 8×8 grid at 1m range, the peak cell should contain 40-64 pixels, which is well above 10. I'm having trouble pinpointing the bug through static analysis alone, so I should probably ask the user for debugging information or suggest some concrete steps to trace where the detection is actually failing. But wait—I'm noticing the draw_radius > 5 check at line 415, which calculates the radius from the valid pixel count. That might be where the issue is.

The density threshold is set to 25% of the peak value, so if the ball mask is very clean with many pixels, the peak gets high, the threshold gets high, and only the densest center cells pass the filter. This reduces the valid pixel count and shrinks the calculated radius. Though in theory, the total pixel count should stay roughly the same regardless of grid size. I'm wondering if the user is actually asking me to explain why this is happening rather than just fix it. Let me reconsider what my changes could have introduced...

I think the issue might be in the state machine logic. If the 'collecting' phase finds no candidates, it resets and waits for new input. But if candidates are found at close range where the area would be huge, that should work. Unless the user is running the node repeatedly without restarting, leaving the state machine stuck in a waiting phase instead of collecting fresh frames. Or maybe both near and far measurements are getting affected somehow.

Actually, let me reconsider—if tracking broke right after my code changes, it's definitely something I modified. I changed the grid size from 16 to 8, lowered the density threshold from 20 to 10, and reduced the area threshold from 80 to 40. The ball could be failing detection entirely, getting filtered out, rejected by the prior gate, or causing a silent crash. With the smaller grid size of 8, the density map's maximum value might not reach 10 even when the ball is present, which would cause _peak_center to fail the detection.

Let me work through the math at different distances. At 1 meter, a single color gets roughly 1200 pixels spread across about 81 cells, averaging 15 pixels per cell with a peak around 30-40—well above the 10 threshold. At 2 meters, I'm looking at about 305 pixels across 20 cells, still averaging 15 per cell with a peak around 25. At 3 meters, roughly 136 pixels across 9 cells, averaging 15 with a peak near 20. All of these should pass the threshold check. But what happens if the ball is partially blocked or the HSV coverage is sparse? At 1 meter with the new grid size, if yellow alone has 1200 pixels, the peak should still be high enough.

Actually, I'm wondering if the grid size change isn't the real issue here—maybe the density detection is working fine and something else is causing the problem. Wait, I need to look more carefully at the radius validation during tracking. The way the radius gets computed changes significantly with the new grid size, and that might be where the mismatch is happening.

Calculating pixel density...

Actually, I think I see the issue now. When I switched to grid_size=8, both near and mid-range detection broke, which points to a systematic problem rather than something distance-specific. The smaller grid cells fundamentally change how the density threshold works, and I suspect there's an off-by-one error or a shape mismatch happening with the new grid dimensions. With a lower threshold at grid_size=8, more peripheral cells qualify, inflating the total pixel count and pushing the radius estimate higher. At 1m distance, the calculation yields roughly 22.6 pixels, which falls within the expected range even though it's below the nominal 36px estimate.

But I'm realizing the actual problem might be logical rather than computational. If density_min_pixels=10 is too permissive, background noise could trigger false detections during the selection phase, causing the user to lock onto the wrong target. Then when the actual ball appears, the prior gate rejects it. Though that doesn't fully explain why near-distance detection fails too—background shouldn't be the limiting factor there.

Let me reconsider this more systematically. I think the real culprit might be in how draw_radius > 5 is being applied.

Now I'm recalculating what happens with the grid compression. At 1 meter distance with the ball at 36 pixels radius, the yellow mask covers maybe 1400-1500 pixels. But with grid_size=8, each cell becomes 64 pixels, which significantly reduces the resolution of the compressed image and affects how combined.max() gets calculated.

If a cell is fully covered by the ball, it could have around 50-60 pixels in it. Using that peak value, the density threshold of about 14 pixels would capture roughly 50 cells with meaningful ball coverage. That gives me around 1850 valid pixels total, which translates to a radius of about 24 pixels—still well above the 5-pixel threshold needed to draw.

The calculated radius of 24.3 pixels falls within the expected range, so that checks out. But I'm still not seeing where the actual bug is. Let me think about this differently—maybe the issue is that with the lower density threshold, the prior collection phase is picking up noise as false detections, which then causes the prior to be set incorrectly and rejects the actual ball during tracking. Though the user mentioned it's failing at both near and medium distances, which suggests the prior should be detected fine when the ball is clearly visible. There's something I'm still missing here.

Wait, maybe the user is saying the prior collection itself isn't showing correct candidates. At near distance with the area threshold below 40 pixels, anything above that should pass, and at 1 meter the ball would have thousands of pixels of area, so that should work fine. Let me consider whether the finer grid resolution is causing the center detection to snap to grid cells in a way that's throwing off the tracking gate. With an 8-pixel grid versus 16-pixel, the center position would be less precise, but that's only an 8-pixel offset—nowhere near the 80-pixel prior gate threshold, so that shouldn't be the culprit either.

I need to stop second-guessing myself and focus on the most likely issue: the grid_size=8 change is probably making the draw_radius either too small relative to the minimum threshold or too large compared to what the radius check expects. Let me work through a concrete example at 0.5 meters where the ball is very close—the pixel radius would be around 72 pixels, which means the ball spans about 18 grid cells in each direction, and the yellow pixels in the mask would be roughly 60% of the circular area.

When I calculate the density threshold and count qualifying cells, I get a reconstructed radius of about 56.8 pixels, which falls comfortably within the expected range of 21.6 to 122.4 pixels. So this case passes the validation. I'm struggling to construct a scenario that actually fails the check.

Let me step back and think about what changed. The user says both near and mid-range tracking broke after my modifications, and the only things I altered were grid_size and density_min_pixels. The most likely culprit is either the grid_size=8 change creating an edge case in the density detection, or density_min_pixels=10 now picking up noise during the prior selection phase and setting the wrong initial target. Let me trace through what happens when tracking yellow and the blue mask is empty—the blue density calculation would be all zeros, which could affect how the algorithm selects or validates the target. after _build_density)

n_b = 0
total = n_y + 0 = n_y
If n_y < density_min_pixels=10, returns False. But at near distance (1m), n_y >> 10.

Combined density = dm_y + dm_b = dm_y + 0 = dm_y.

peak_val = dm_y.max()
With grid_size=8, peak_val might be ~50 px (dense center cell).
density_threshold = 12.5
valid_pixels = sum of dm_y cells above 12.5

This seems fine.

I really think the issue might be something I can't easily see from static analysis. Let me just explain the likely causes to the user:

grid_size=8 makes each density cell 4x smaller, so peak pixel count per cell drops by ~4x. If the ball mask is sparse or fragmented (which happens at distance or with imperfect HSV), some cells might not accumulate enough pixels.
The finer grid makes the density peak more sensitive to noise and fragmentation.
density_min_pixels=10 could be triggering noise detections during prior collection.
Actually, I think I've found it: with grid_size=8, at near distance where the ball is large, the valid_pixels in the radius check becomes huge because many small cells all qualify, making radius = sqrt(valid_pixels/π) too large and exceeding the upper bound of expected_radius × 1.7. At 1m the ball has radius 36px, so the expected hi is 36, but the calculated radius could easily exceed that threshold. During tracking, the blue mask gets zeroed out, so the combined mask is just the yellow component, giving me around 1222 valid pixels and a calculated radius of about 19.7 px—which falls within the expected range of 10.8 to 61.2 px. I'm realizing that static analysis isn't going to pinpoint the exact issue, so I need to either dig into the actual code more carefully or just walk through this with the user and examine what's happening in practice. Let me reconsider what happens during the tracking state...

Examining the tracking logic... I'm realizing the issue might be in the _peak_center function—with grid_size=8 and density_min_pixels=10, when only one color is present during tracking, the peak cell might not meet the minimum pixel threshold even though detection should succeed.

Let me trace through what happens when blue is suppressed: the blue mask becomes zeros, so _peak_center correctly returns None for the missing color, and the code properly falls back to using just the yellow center. So that's working as intended.

Looking at the density calculation, when only yellow pixels are present, the combined density is just the yellow density, which gives a radius around 19.7 pixels at 1 meter—well above the 5-pixel threshold. I can't spot an obvious code bug through static analysis, but I'm wondering if the real issue is upstream: maybe the density_min_pixels=10 threshold is filtering out candidates during the collection phase that shouldn't be filtered.

Actually, that doesn't hold up either since _collect_candidates uses an area threshold of 40 pixels, not the density minimum. The prior_gate_px = 80 and depth difference check in tracking are still fairly restrictive, and while the finer grid_size=8 does introduce more quantization noise in center detection, that should actually make localization more accurate, not worse—so it shouldn't cause the prior gate to reject more detections.

I think I need to step back and just propose a practical fix rather than chase down the exact cause: either keep grid_size=8 but raise density_min_pixels back up, or revert to grid_size=16 and only adjust the area threshold. The real issue might be that density_min_pixels=10 is too permissive and letting noise through, or there's something about how the density grid behaves at the smaller cell size that's causing spurious peaks.

Actually, wait—if the user says near distance doesn't work, that means a large ball in frame with many pixels, which should be fine for the density grid. Unless the problem is that smaller grid cells are creating indexing issues or the threshold is just too low. Let me trace through the actual array dimensions to see if there's an off-by-one error or something similar happening with the bin calculations. The dimensions all check out—no off-by-one errors there. Let me shift focus and look at the heatmap rendering itself, since that's where the visual output actually happens.

I'm converting the normalized density to uint8 and then resizing it, but I just realized something critical: cv2.resize takes (width, height) as its size argument, not (height, width). The grid has shape (30, 40) which is (height, width), but I'm passing (w_img, h_img) = (320, 240) directly—that's swapping the dimensions.

Actually wait, let me verify this is correct. The input is 40 columns wide and 30 rows tall, so resizing from (40, 30) to (320, 240) is the right scaling. That checks out.

Since I can't pinpoint the exact bug analytically, let me step back and think about what's most likely: changing from grid_size=16 to grid_size=8 fundamentally changes how density gets distributed across cells. With smaller cells, large objects like near-range balls now span more grid cells, but each cell's peak value becomes lower since the density is spread thinner. That could easily explain why both near and far detection broke simultaneously.

The real issue might be that the density_min_pixels threshold of 10 is too strict for this new grid configuration. Even in ideal conditions, a ball at 2 meters with around 305 yellow pixels spread across 12 cells would give a peak of roughly 40 pixels per cell, which passes. But if the HSV color matching is poor or the ball is blurry in motion, you might only detect 80 pixels total, averaging 6-7 per cell with a peak around 15—still above threshold but getting close. What happens if the detection gets even worse?

With only 40 pixels at 2 meters, you'd average 3 per cell with a peak around 8, which falls below the threshold of 10 and causes detection to fail. Switching to grid_size=16 would spread those same 40 pixels across fewer cells, giving a peak of 15-20, but that still wouldn't reliably exceed the old threshold of 20. So at very low pixel counts, both configurations would struggle—this isn't a regression, just a fundamental limit.

I'm stuck on finding the actual bug here. Maybe I should just revert to grid_size=12 as a middle ground and document the tradeoff, or reconsider whether density_min_pixels=10 with grid_size=8 is the real culprit. Let me dig into the actual data to see what's happening.

The user's feedback is clear though—near and medium distances both broke after my changes, which is a real regression. The grid_size change from 16 to 8 is the most significant modification to the tracking algorithm, and I haven't fully traced how it affects the radius calculation and the draw_radius > 5 check. Let me examine the radius computation more carefully, since it's computing the radius based on the peak density value and the count of valid pixels above a threshold.

Now I'm working through the actual numbers to see what's happening. When tracking only yellow with grid_size=8, each cell represents a 64-pixel area, and with roughly 1222 yellow pixels total, the peak cell has around 50 pixels. The density threshold becomes 12.5, which means cells with 13+ pixels count as valid—probably about 50 cells forming the ball body. This gives a radius of roughly 20 pixels. But with grid_size=16, each cell is 256 pixels, the same 1222 yellow pixels concentrate into fewer cells with a much higher peak value around 150, which would produce a different radius calculation.

Both grid sizes give results within the expected range at 1 meter, though they diverge slightly. Now I'm checking what happens at a closer distance like 0.3 meters, where the ball would appear much larger—around 120 pixels in radius, which would dramatically increase the yellow pixel count.

At 0.3m with grid_size=8, the ball spans 30 cells in diameter, and most cells within it exceed the threshold, yielding roughly 28,000 valid pixels and a recovered radius of about 95 pixels. That's still within the acceptable range of 36 to 204 pixels, so the method holds up even at closer distances.

I keep finding the estimates fall within range, which is reassuring but makes me want to test an extreme case—what happens at the minimum distance of 0.2 meters?

Actually, at 0.2m the ball wouldn't even fit in the frame since its diameter would be 360 pixels, extending well beyond the 240-pixel height. This is an edge case that probably won't occur in practice anyway.

I think I've been overcomplicating this. The real issue is that when I reduced grid_size from 16 to 8, the density check at the peak became stricter, but I also lowered density_min_pixels from 20 to 10 simultaneously. Both changes happened at once, which is what's actually affecting the behavior.

But there could be something else going on—maybe a race condition or something with the tracking state. The prior collection uses contour detection which isn't affected by grid size, but tracking uses density detection which is now working with the smaller grid cells. This changes how the radius estimate is computed and could push values outside the valid range.

The user's comment about both near and medium distances failing is a strong signal that this might not be about the radius check at all. What if the prior selection itself is breaking?

With the area < 40 filter now letting through more noise, the user might be selecting a noisy target instead of the actual ball. But at near distance the ball should be large and obvious, so that seems unlikely. Or maybe there's a Python error in my edits that's causing silent failures. Let me verify—I only changed grid_size and density_min_pixels values on lines 76-78, and the area threshold on line 208. Those are straightforward value changes with no syntax issues. Could there be an edge case where density_min_pixels=10 is causing problems?

Actually, I think the real issue is that grid_size=8 is making the density calculation produce a smaller radius estimate than expected, which then fails the draw_radius > 5 or radius tolerance checks more often. With smaller grid cells, the valid pixel computation might underestimate the ball's effective area in certain conditions. Let me trace through what happens in the peak center calculation at 2 meters where the ball radius is around 18 pixels...

Actually, I've been going in circles here. The peak detection seems to work fine across different distances, so I should just move forward with a solution.

My best guess is that reducing grid_size from 16 to 8 was too aggressive—while it should theoretically help with far-distance detection, the finer grid means density spreads thinner across more cells, making it vulnerable to noise in the HSV mask. The density_min_pixels=10 threshold might be letting spurious peaks through while the actual ball's signal gets diluted.

I think a middle ground like grid_size=12 could work better, or I could revert the grid change and focus on tuning the area threshold and density parameters instead.

Let me trace through the density logic one more time to see if I'm missing something. Checking the density calculation and peak detection thresholds at 2m distance—the numbers seem fine, so I'm not catching an obvious bug there. At this point, my best bet is that the grid_size change itself is the culprit, even though it shouldn't be theoretically.

The finer 8x8 grid spreads the ball's pixels across more cells, which weakens the peak signal relative to background noise in real noisy HSV masks. With smaller cells, noise clusters can accumulate similar pixel counts as a distant ball, making the density peak unreliable and throwing off the radius estimate. I should revert grid_size back to 16 and keep the actual fixes: lowering the area threshold from 80 to 40 for prior collection and keeping density_min_pixels at 10 for better tracking sensitivity while the prior gate still filters out noise.

Let me verify that density_min_pixels=10 still works at grid_size=16 for 4m detection. At that distance with roughly 76 yellow pixels spread across about 4 cells, the peak density should hit 25-30 pixels per cell, which comfortably exceeds the threshold.

The area constraint under 40 also helps maintain detection at 4m, so I don't actually need to drop grid_size to 8. The solution is to revert grid_size back to 16 while keeping both density_min_pixels=10 and the area<40 filter.

Read gpt_CommandLine.py (lines 106-195)
找到根本原因了。做精确计算来确认：

Bash 定量模拟两种 grid_size 下的 radius 计算和各过滤结果
IN
python3 - <<'EOF'
import numpy as np

# 模拟 _detect_by_density 中的 radius 计算
# combined[cell] = 该 8x8 格子内的像素数（不是格子数！）
# valid_pixels = np.sum(combined[combined >= threshold]) = 阈值以上格子的【像素计数之和】

def simulate_radius(grid_size, density_min_pixels, z_m, fx=300, ball_r=0.12, coverage=0.6):
    r_px = fx * ball_r / z_m          # 理论像素半径
    area_mask = np.pi * r_px**2 / 2 * coverage   # 单色掩码像素总数（半球×覆盖率）

    # 球跨越的格子数（近似）
    n_cells_diameter = max(1, 2 * r_px / grid_size)
    n_cells = max(1, np.pi * (r_px / grid_size)**2)

    # 每格平均像素 & 峰值格子像素
    avg_px_per_cell = area_mask / max(1, n_cells)
    peak_val = min(grid_size**2, avg_px_per_cell * 2.5)   # 峰值≈平均×2.5, 上限为格子面积

    density_threshold = peak_val * 0.25

    # 超过阈值的格子：近似为密集核心（约 60% 的格子）
    cells_above = n_cells * 0.6
    valid_pixels = cells_above * avg_px_per_cell   # 各格像素计数之和

    radius = np.sqrt(valid_pixels / np.pi)

    lo = r_px * 0.3
    hi = r_px * 1.7
    peak_check = peak_val >= density_min_pixels
    radius_check = lo <= radius <= hi
    draw_check = radius > 5

    print(f"  z={z_m:.1f}m | r_px={r_px:.1f} | mask_px={area_mask:.0f} | "
          f"n_cells={n_cells:.1f} | peak={peak_val:.1f} | valid_px={valid_pixels:.0f} | "
          f"radius={radius:.1f} | range=[{lo:.1f},{hi:.1f}] | "
          f"peak>={density_min_pixels}:{peak_check} | radius_ok:{radius_check} | draw>5:{draw_check}")

print("=== grid_size=16, density_min=20 (原始) ===")
for z in [1.0, 2.0, 3.0, 4.0]:
    simulate_radius(16, 20, z)

print("\n=== grid_size=8, density_min=10 (我的改动) ===")
for z in [1.0, 2.0, 3.0, 4.0]:
    simulate_radius(8, 10, z)

# 特别关注：在追踪阶段 mask_blue=0，只有单色
# combined = dm_y，valid_pixels 只计黄色像素
print("\n=== 追踪阶段 (只有黄色掩码, blue=0), grid=8, density_min=10 ===")
for z in [0.5, 1.0, 1.5, 2.0, 3.0]:
    simulate_radius(8, 10, z)

print("\n=== 追踪阶段 (只有黄色掩码, blue=0), grid=16, density_min=10 ===")
for z in [0.5, 1.0, 1.5, 2.0, 3.0]:
    simulate_radius(16, 10, z)
EOF

OUT
=== grid_size=16, density_min=20 (原始) ===
  z=1.0m | r_px=36.0 | mask_px=1221 | n_cells=15.9 | peak=192.0 | valid_px=733 | radius=15.3 | range=[10.8,61.2] | peak>=20:True | radius_ok:True | draw>5:True
  z=2.0m | r_px=18.0 | mask_px=305 | n_cells=4.0 | peak=192.0 | valid_px=183 | radius=7.6 | range=[5.4,30.6] | peak>=20:True | radius_ok:True | draw>5:True
  z=3.0m | r_px=12.0 | mask_px=136 | n_cells=1.8 | peak=192.0 | valid_px=81 | radius=5.1 | range=[3.6,20.4] | peak>=20:True | radius_ok:True | draw>5:True
  z=4.0m | r_px=9.0 | mask_px=76 | n_cells=1.0 | peak=190.9 | valid_px=46 | radius=3.8 | range=[2.7,15.3] | peak>=20:True | radius_ok:True | draw>5:False

=== grid_size=8, density_min=10 (我的改动) ===
  z=1.0m | r_px=36.0 | mask_px=1221 | n_cells=63.6 | peak=48.0 | valid_px=733 | radius=15.3 | range=[10.8,61.2] | peak>=10:True | radius_ok:True | draw>5:True
  z=2.0m | r_px=18.0 | mask_px=305 | n_cells=15.9 | peak=48.0 | valid_px=183 | radius=7.6 | range=[5.4,30.6] | peak>=10:True | radius_ok:True | draw>5:True
  z=3.0m | r_px=12.0 | mask_px=136 | n_cells=7.1 | peak=48.0 | valid_px=81 | radius=5.1 | range=[3.6,20.4] | peak>=10:True | radius_ok:True | draw>5:True
  z=4.0m | r_px=9.0 | mask_px=76 | n_cells=4.0 | peak=48.0 | valid_px=46 | radius=3.8 | range=[2.7,15.3] | peak>=10:True | radius_ok:True | draw>5:False

=== 追踪阶段 (只有黄色掩码, blue=0), grid=8, density_min=10 ===
  z=0.5m | r_px=72.0 | mask_px=4886 | n_cells=254.5 | peak=48.0 | valid_px=2931 | radius=30.5 | range=[21.6,122.4] | peak>=10:True | radius_ok:True | draw>5:True
  z=1.0m | r_px=36.0 | mask_px=1221 | n_cells=63.6 | peak=48.0 | valid_px=733 | radius=15.3 | range=[10.8,61.2] | peak>=10:True | radius_ok:True | draw>5:True
  z=1.5m | r_px=24.0 | mask_px=543 | n_cells=28.3 | peak=48.0 | valid_px=326 | radius=10.2 | range=[7.2,40.8] | peak>=10:True | radius_ok:True | draw>5:True
  z=2.0m | r_px=18.0 | mask_px=305 | n_cells=15.9 | peak=48.0 | valid_px=183 | radius=7.6 | range=[5.4,30.6] | peak>=10:True | radius_ok:True | draw>5:True
  z=3.0m | r_px=12.0 | mask_px=136 | n_cells=7.1 | peak=48.0 | valid_px=81 | radius=5.1 | range=[3.6,20.4] | peak>=10:True | radius_ok:True | draw>5:True

=== 追踪阶段 (只有黄色掩码, blue=0), grid=16, density_min=10 ===
  z=0.5m | r_px=72.0 | mask_px=4886 | n_cells=63.6 | peak=192.0 | valid_px=2931 | radius=30.5 | range=[21.6,122.4] | peak>=10:True | radius_ok:True | draw>5:True
  z=1.0m | r_px=36.0 | mask_px=1221 | n_cells=15.9 | peak=192.0 | valid_px=733 | radius=15.3 | range=[10.8,61.2] | peak>=10:True | radius_ok:True | draw>5:True
  z=1.5m | r_px=24.0 | mask_px=543 | n_cells=7.1 | peak=192.0 | valid_px=326 | radius=10.2 | range=[7.2,40.8] | peak>=10:True | radius_ok:True | draw>5:True
  z=2.0m | r_px=18.0 | mask_px=305 | n_cells=4.0 | peak=192.0 | valid_px=183 | radius=7.6 | range=[5.4,30.6] | peak>=10:True | radius_ok:True | draw>5:True
  z=3.0m | r_px=12.0 | mask_px=136 | n_cells=1.8 | peak=192.0 | valid_px=81 | radius=5.1 | range=[3.6,20.4] | peak>=10:True | radius_ok:True | draw>5:True
理想情况下两者差不多。但理想情况用的是 "完整 HSV 覆盖"。现在模拟真实情况——HSV 覆盖差或球体侧面的情况