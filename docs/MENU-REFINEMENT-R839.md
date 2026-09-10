# R839 — native menu refinement

2026-09-09. Previous turn: progress (README and icon packaging). This pass follows
the product queue, not the parked CPU-thread comparison. Product Design audit
workflow used for the bounded existing menu surface; no new visual system.

## Scope and observations

Actual GalaxyPadGameOverlay in the isolated UIKit host, iPad Pro 11-inch M5,
iOS26.5, sole Simulator DE8E956F-6B29-4FF3-AF4A-77034CE8588A. No game core/data/save
loaded. Compared hierarchy and mechanisms with read-only SunPadGameOverlay
buildMenu and PRD9.5. This is not a gameplay, full-accessibility or iPhone audit.

1. Controls preview: existing lower clusters, one-letter action buttons and hidden
   advanced keys remain. Neutral field cannot establish overlap with game HUD or
   text. Touch geometry was not redesigned this pass.
2. Root menu before: FPS was a primary item separate from Display. Stop appeared
   actionable even with no runtime handler. Other host-dependent actions were
   correctly disabled in this preview; this is not evidence they fail in product.
3. Root menu after: seven top-level items instead of eight; FPS moved under Display
   as specified by PRD. Removed an empty copied experiment section (already
   invisible at runtime). Stop is disabled without a handler and refreshes when
   the handler is attached/cleared. Destructive attributes on Stop/data removal
   preserve existing disabled state and confirmation paths.
4. Display submenu: render/aspect groups preserved; FPS reachable. Unsupported
   aspect actions remain disabled; that delivery gap is not disguised as fixed.
5. Toggle: real UI click dismissed menu; reopening Display showed FPS selected
   both visually and in accessibility tree. Product FPS renderer was not loaded.

Private screenshots: generated/ui-r839/01-controls-before.png through
05-fps-selected.png. Simulator captures have native framebuffer orientation;
the live Simulator window was inspected in landscape. No screenshots published.

## Verification and limits

- Baseline `bash tests/run-mobile-ui.sh DE8E956F-6B29-4FF3-AF4A-77034CE8588A`
  passed, log generated/tests/mobile-ui.8xf9g2.
- First edited test build failed from local variable name collision; corrected.
- Same command then passed, log generated/tests/mobile-ui.zd646f. Added assertions
  for root hierarchy, nested FPS, destructive/disabled semantics, and real attached
  menu refresh after runtime callback changes. Existing input/layout tests pass.
- `--preview` exercised current compiled overlay; no product bundle replacement.
- Preview terminated and sole Simulator shut down. No game or save touched.

Next: controls/settings view and actual gameplay HUD/reachability on a private
product candidate, then compact iPhone layout. Preserve explicit A/B and Spin,
pointer ownership and editor reset; no broad mapping rewrite from this preview.
Full PRD remains open, including performance and physical-device acceptance.
