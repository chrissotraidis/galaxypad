# Disc identity

Status: **exact input identified; G1 evidence complete**

## Import compatibility

The development reference below identifies one reproducible input, not every
valid WBFS conversion. The importer now verifies a single-disc WBFS header,
USA RMGE01 revision 0 in both disc and game-partition headers, the exact main
DOL, and the home-menu RSO and symbol data. Different container sizes/layouts
are accepted within a 5 GiB bound. ISO, split WBFS, other regions and revisions
remain unsupported. The executable checks do not certify every asset byte.

The private copy and extraction stay in staging until verification completes
and the runtime stops. Save/NAND paths are separate. At least 9 GiB free is
required, with additional capacity for larger containers. The developer command
`scripts/verify-disc.sh` intentionally still checks the exact reference container
for reproducible code generation; it is not the user-import compatibility test.
These source changes are not in the already-published Preview 2 binary.

## Immutable source image

| Field | Value |
|---|---|
| Local source | designated single image under ignored `ref/` |
| Container | WBFS |
| Byte length | 3,508,535,296 |
| SHA-1 | `925af5b6b84ad1ca279c3a5633fdb38821e071bd` |
| SHA-256 | `bd0d3d4bc1376a8614fd8f4fee5df86be6bc676e9d617944918fda79ed9e3589` |
| Permissions | `-rw-r--r--` at the identity gate |

The source was inspected in place and was not moved, renamed, truncated, or modified.

## Read-only WIT result

| Field | Value |
|---|---|
| Disc/boot/WBFS ID | `RMGE01` |
| Ticket/TMD ID | `RMGE` |
| Product | Super Mario Galaxy |
| Region | NTSC/USA |
| Image kind | Wii, encrypted and scrubbed WBFS |
| Virtual disc size | 4,699,979,776 bytes |
| Scrubbed payload size | 3,501,359,104 bytes |
| Partitions | one signed encrypted DATA partition; no update partition present |
| DATA partition range | `0x0f800000..0x1173c0000` |
| IOS | 33 (`00000001-00000021`) |
| Directories/files | 79 / 2,383 |

The extracted tree contains 2,386 total files including partition metadata and system files. `boot.bin` records disc number 0, revision 0, and Wii magic `0x5d1c9ea3`.

## Deterministic extraction and executables

Two clean extractions into distinct ignored directories produced identical sorted relative-path/file-SHA-256 manifests. Each manifest contains 2,386 files and has SHA-256 `da223690a51c93308b2746fad38966edf62bf313ea1ff32ce659997844893630`.

| Path | Size | SHA-1 | SHA-256 |
|---|---:|---|---|
| `sys/main.dol` | 6,283,264 | `9a71008ae1ee9010e267fa67d1f0b0d4f0e895dd` | `2c680585a8f58e1cc9c5521b579057f12b124ff0ef409e470a57606c50a93c09` |
| `files/ModuleData/HomeButtonMenuWrapperRSO.rso` | 194,816 | `20cdb6b3fcbba6ab486780be2e12675f93644598` | `13dd2229f88b5af0f18875b3db15f4d3a52ea583085606a50e4b760a2e68194e` |

`files/ModuleData/product.sel` is a 5,600-byte RSO symbol-selection metadata blob (SHA-256 `c37a0ff9bf9b86f8d46b0ac5c360f747add24178c2a81951ad4ecd06a65d6730`), not a standalone executable. No other `.dol`, `.rel`, `.rso`, or `.elf` file exists in the manifest.

This `RMGE01` `main.dol` does not match Petari's pinned `RMGK01` SHA-1. Petari names and behavior are semantic guidance only; no Petari address is accepted without revision-specific validation.

No partition key or decrypted game data belongs in committed evidence.
