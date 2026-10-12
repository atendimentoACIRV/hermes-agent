# Architectural rulings — Hermes Experience Compiler activation
1. Continue PR #82 in its isolated branch/worktree; do not touch dirty root checkout or merge to main.
2. Keep H-079 baseline exact-head and H-081/H-082 as separate non-green promotion gates. Prior operational-speed PASS_WITH_AUTHORIZATION is not a green check; user authorizes this feature development, but no deployment.
3. H-080B expected fast path must be semantically compatible: text 'Abre o Trello.' vs formal host example.test appears mismatched. Never make router accept a different host only to satisfy a test.
4. Filesystem canary supports only write_file for now; read_file, fs_read, fs_write are rejected until individually implemented with independent verifier. Ignoring a step can never yield success.
5. Candidate-specific sandbox replay and filesystem readback replace unrelated probe writes; positive evidence records digests, ID, version and verifier fingerprint, not raw content. Negative divergence is tied to candidate target.
6. Preserve OperationalKernel, ExperiencePromotionPolicy, Effect Authority, native Browser ownership, TaskRun scope; SHADOW cannot dispatch.
7. EC-13 conditional HOLD; no competing n8n/Activepieces executor or undocumented licensing.
8. This is a partial incremental security remediation, NOT end-to-end qualification.

9. **EC-01 intent IR alignment**: use allowlisted native Browser destination as goal AND(EQ(host,..),EQ(page_family,..),EQ(recovery_state,live)), with exact corresponding SET effect footprint. Do not add generic url predicate to verified browser state or bypass router; keep authority and verified owner as sole dispatch gate.
10. **No undeclared input injection**: fixed named-site alias is already bound by semantic goal and URL in compiled static step; send no speculative url argument to zero-input learned schema. Parameterized future website flows require a separate schema-aware binding design and independent tests, not silently allowed extra inputs.
11. **Effect budget caution**: global effect_contained(SET) subsumes by path without comparing value. The exact requested target remains a separate goal coverage obligation. Any change to effect_contained is a security-policy migration, not part of EC-01.
