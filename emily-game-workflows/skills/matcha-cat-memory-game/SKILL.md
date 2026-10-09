---
name: matcha-cat-memory-game
description: Play the Matcha Cat memory-matching game through macOS iPhone Mirroring by reading the revealed board, tracking card positions, and completing pairs with visual verification.
---

# Matcha Cat memory game

Use Computer Use with the native **iPhone Mirroring** app (`com.apple.ScreenContinuity`). This is a visual workflow: the mirrored phone UI may not appear in the accessibility tree, so obtain a fresh screenshot whenever the board changes and use screenshot-relative clicks when no usable AX target exists. Do not use a fixed replay of coordinates from a previous round.

Discard the entire identity-to-position map when a new round starts; every round is a fresh memory task. Separately, watch for in-round reflow: after matched cards are removed, the remaining cards may move to different slots, so positions can also need recalculation within the same round.

## Safe start

- Confirm the iPhone Mirroring window is visible and focused before interacting.
- Locate the intended Matcha Cat banner from the current screenshot and tap its `เล่นเกม` button.
- If the game offers paid play and free play, ask which mode to use unless the user has already specified one. Never spend a ticket or other in-game resource by assumption.
- After selecting a mode, wait for the game screen and tap `เริ่มเกม` only when the user has authorized starting the round.

## Solve a round

1. Wait for the `Ready` preview to finish loading. During this phase the game shows every card face; capture a screenshot while the whole board is visible.
2. Detect the current card grid from the screenshot. The demonstrated round used 4 columns by 5 rows, but treat the grid size and card centers as dynamic.
3. Enumerate card centers in row-major order and assign a visual identity to each card. Record all positions for each identity; do not infer a pair from a similar-looking cat unless the artwork is clearly the same.
4. Wait until the cards are face-down and the board is stable. Tap the two centers for one known pair.
5. In speed mode, first tap one or two known pairs in a compact Computer Use call. Use a verification screenshot to determine whether matched cards disappear in place or whether the remaining cards reflow into new positions.
6. If slots stay fixed, send the remaining known pair sequence in one compact call without per-pair screenshots or narration. If cards reflow, use short batches, re-detect the current card centers after each batch, and translate the remembered identities to the new layout before continuing. Never send stale coordinates after a reflow.
7. Confirm periodically that matched cards remain matched/disappear and that the score or board state advances. If a pair does not match, stop the fast sequence, leave the board state intact, update the visual map, and continue in verified mode.
8. Repeat until no unmatched cards remain. Avoid tapping during startup or transition animations, but do not wait longer than needed once the board is interactive.
9. Wait for the result overlay and verify that the round is completed and a score/result is visible. Report the observed result without claiming success from a score change alone.

## Speed mode

Prefer speed mode when the user says the score depends on completion time. Capture the complete `Ready` preview once and compute the pair map before tapping. Test the board's removal behavior with a tiny first batch: only use one full click sequence if slots remain fixed; otherwise use compact reflow-aware batches. Do not spend round time on narration or unnecessary AX polling.

If the `Ready` preview was missed and the cards are already face-down with no known map, do not attempt a full 4×5 discovery scan under a short timer. Stop before spending more time and ask the user to restart a free round (or explicitly authorize another mode); a slow blind scan is unlikely to beat the clock.

## Stopping conditions

Pause and ask the user if the board is cropped or unreadable, the artwork is ambiguous, the app presents a ticket/purchase prompt, a permission prompt appears, or the game state cannot be verified after a tap. If the user asks to stop, stop immediately.

## Learned behavior from the demonstration

The demonstrated Matcha Cat round first displayed a full 4×5 set of cat cards with a `Ready` countdown, then turned them face-down. Correct pairs increased the score by 100 and removed the matched cards. A completed round showed a `สรุปผล` result screen with a final score and reward.
