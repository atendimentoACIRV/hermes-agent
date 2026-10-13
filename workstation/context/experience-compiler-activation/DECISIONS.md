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

12. **EC-03 legacy cache fail-closed**: only return a cached DurableRunAdoptionOwner if _bound_task_run exactly matches current canonical (task_id, run_id). An owner lacking identity must be reconstructed; no permissive grandfathering.
13. **EC-07 URI-only telemetry projection**: emit_event converts known workstation.contracts.EvidenceRef objects to URI; summaries/verifier metadata must never be serialized into telemetry. No change to canonical evidence or verification authority.

14. Native Browser navigation changes external state: run-local adoption requires explicit CALL(browser.navigate,host), HTTPS host and optional path match, independently admitted readback and effect authority; never classify it as read-only. SET-only existing budgets need separately reviewed migration if Browser direct adoption is desired.
15. A cached owner matching at factory time may become stale later; production dispatch and readback must re-check canonical task/run at every call boundary.
16. Snapshot/lease revocation is a TOCTOU risk. Runtime re-reads live canonical authority, lease, uncertain effects and budgets at durable item admission and before each step. No claim of perfect atomicity across native Browser side effects without H-082.
17. VERIFIED_SUCCESS in progressive corpus requires E2+ persisted proof, explicit owner trust and verifier fingerprint, matching task/run/operation and canonical proof linking underlying evidence. A fabricated text, mismatched run or failed readback never certifies an operation.
18. Vendor Laya 0.3.23 locked-source provenance and local System-1 tests are distinct from live checkpoint, DIRECT, exact-head CI and release certification.

19. Named-site deterministic command may explicitly budget CALL(browser.navigate,trello.com) only for that host; existing SET goals alone do not authorize network navigation. Formal effect lattice still demands external reversible authority and independent readback.
20. An owner-verified post-state does not prove a causal change without a separate independent pre-state witness. A context-supplied semantic_state_before is only a claim. Delta may be computed only when workstation.operational_prestate_readback.v1 resolves with read_before_write=true, canonical task/run/operation, approved observer and exact state predicates. Otherwise store verified poststate with empty delta to prevent speculative compilation.
21. OperationalKernel may attach only known formal contract family/target/effect/scope; no unverified execution arguments may enter automatic replay from tool text or arbitrary Laya output. Missing prestate producer and parameter attestation keep productive EC-04 reuse HOLD.

22. Production filesystem semantics MUST observe the same _resolve_path(path, base_dir) used by fs_ primitives, for filesystem and composite, rather than process CWD.
23. The existing OperationalKernel is the ONLY producer for scoped fs_write prestate in a durable TaskRun. Proof generation requires canonical running WorkPlan / pending-or-running WorkItem task/run/operation identity, current primitive_admission, owner scope, and resolved resource; admission + canonical status must be rechecked after read and before dispatch.
24. Independently persisted POST-readback proof is restricted to fs_hash/hash_file/fs_stat/stat metadata or digests. Never persist raw fs_read contents as reusable proof. Verification result and raw ack alone are insufficient. Resource of prestate and poststate must agree.
25. Intermediate VERIFIED_SUCCESS corpus capture now demonstrated with real fs_hash and an unfinished two-item WorkPlan. Mining/validated offer/VERIFIED_REUSE and Laya DIRECT are separate missing gates. No performance or cost claim without evidence.
