# Native HOME-menu adapter plan

Status: **bounded plan; implementation and runtime proof pending**

The supported input contains one dynamic executable: `HomeButtonMenuWrapperRSO.rso`.
The mobile baseline must never link or execute it and must never generate its jump
table. GalaxyPad will intercept only the exact RMGE01 wrapper boundary and route it
to the native three-dot menu. The generic RSO loader, cache behavior, and executable
write checks remain intact.

## Seven-entry contract

| Guest operation | Native behavior |
|---|---|
| `HBMCreateRSO` | Register the one menu context; retain no pointers into the RSO or its assets. |
| `HBMInitRSO` | Begin a fresh menu session, clear stale selection, pause game input, and enter the native presentation state. |
| `HBMCalcRSO` | Advance the adapter state only; do not consume guest controller structures as native UI input. |
| `HBMDrawRSO` | No-op in guest rendering; the Apple overlay owns presentation. |
| `HBMGetSelectBtnNumRSO` | Return `NULL` until close, reset, or quit has been committed, then return exactly one matching selection. |
| `HBMSetAdjustFlagRSO` | Record 4:3/16:9 for diagnostics; native layout remains safe-area driven. |
| `HBMStartBlackOutRSO` | Enter a bounded closing state and complete without guest blackout drawing. |

## State and lifecycle contract

The adapter state is `inactive -> opening -> open -> closing -> inactive`.
Opening clears injected gameplay input, pauses or ducks audio through the runtime host,
and transfers controller ownership to native UI. Closing clears input again, restores
audio and controller ownership once, and returns one of close, reset, or quit.
Backgrounding while open retains `open`; foregrounding cannot inject held controls.
Shutdown from any state cancels presentation and releases the pause exactly once.

The host must log state transitions and the selected result, but not game data or
guest memory. A watchdog turns a stuck `opening` or `closing` transition into a
visible native error rather than silently resuming the guest.

## Exact-address binding

Petari's `RMGK01` wrapper is semantic guidance, not an address map for RMGE01. Before
implementation, a reproducible exact-DOL signature pass must bind the RMGE01 wrapper,
its seven pointer slots and call sites, and the `setupRsoHomeButtonMenu` call site.
The patch is accepted only when all signatures resolve once, the original words match
a pinned manifest, and a wrong DOL fails closed. The resulting addresses belong in an
RMGE01-only patch manifest with regression tests; no region-relative offsets are
permitted.

## Acceptance

- Open and close from live gameplay and a cutscene.
- Prove no read, link, prologue, or jump-generation attempt for either HOME module file.
- Prove neutral guest input and correct audio pause/resume while open.
- Prove close, reset, and quit selections, plus background/foreground while open.
- Prove clean shutdown from every adapter state with no stuck blackout or pause.
- Repeat on macOS and iPad Simulator before physical-device acceptance.
