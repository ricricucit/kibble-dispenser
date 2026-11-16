# Electronics module

From hardware 6.4 the electronics of the Kibble Dispenser Outdoor live in a detachable, sealed module with its own version line (see [VERSIONS.md](../../VERSIONS.md)). The source of truth for its version is [`VERSION`](VERSION); releases are tagged `case-v<version>`.

- [`case-1.0/`](case-1.0/README.md): case 1.0 (version 1.0.0), fits hardware 6.4. **Status: designed, not printed or tested.**

The holder side of the interface (the opening in the shell and the cap, the two posts, the lock screws, the connector J1 and the harness) is fixed from hardware 6.4 on. A new case may change everything inside, as long as its outside fits that interface:

- MAJOR: the case no longer fits the holder interface (it would need a new chassis);
- MINOR: a compatible change of the case (another board slot, another panel layout, a different speaker ring);
- PATCH: a fix that does not change the fit.

The inside of the case is generic. The electronics on the board and their wiring are a separate project that is still evolving: see [docs/PROTOTYPE_BENCH.md](../../docs/PROTOTYPE_BENCH.md) for the bench prototype and the decisions so far.

The CAD scripts that make the module are part of the chassis chain (`hardware/v6.4/cad/build_v64.py`), and its print files are in the 6.4 print package (`hardware/v6.4/plates/`, projects `Kibble_Module_case_1.0_*.bambu.3mf`, plates MOD-1, MOD-2 and MOD-TPU-1), so chassis and module are always checked together.
