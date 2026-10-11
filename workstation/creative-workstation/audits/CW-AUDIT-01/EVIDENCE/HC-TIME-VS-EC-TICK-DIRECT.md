# EVIDENCE — Hermes creative_time.py vs EffectCraft Time Model (CW-AUDIT-01)

**Arquivos auditados:**  
- `workstation/creative_time.py` (227 linhas, completo — lido diretamente)  
- `effectcraft-main/crates/time/src/lib.rs` (via subagente `fbd8362a` + architecture.md)  
**Data:** 2026-10-11

---

## Hermes `CanonicalTime` (FACT — código verificado)

```python
@dataclass(frozen=True)
class CanonicalTime:
    """Exact rational time in seconds, preventing floating-point drift across cuts."""
    fraction: Fraction  # Python fractions.Fraction — racional exato

    @classmethod
    def from_seconds(cls, seconds: float | int | Fraction | str) -> CanonicalTime:
        if isinstance(seconds, float):
            return cls(Fraction(seconds).limit_denominator(1_000_000))
        return cls(Fraction(seconds))

    @classmethod
    def from_frames(cls, frame_index: int, fps: RationalFps) -> CanonicalTime:
        return cls(Fraction(frame_index) / fps.as_fraction())

    def to_frame(self, fps: RationalFps) -> int:
        exact_frame = self.fraction * fps.as_fraction()
        return int(math.floor(float(exact_frame) + 1e-9))  # epsilon para drift
```

**Pontos fortes:**
- Racional exato via `Fraction` — sem drift em frações NTSC (30000/1001)
- Rejeita NaN/Inf/negativo
- `TimeRange` half-open `[start, end)` — correto para semântica editorial
- `MediaTimeMap` bidirecional com `speed` e reverse
- SMPTE drop-frame completo (29.97 e 59.94 fps)

**Lacunas vs EffectCraft `Tick`:**

| Capacidade | Hermes | EffectCraft Tick |
|---|---|---|
| Armazenamento | `Fraction` (heap, GC) | `i64` (stack, zero-alloc) |
| Saturação aritmética | ausente (exceção em negativo) | `saturating_add/sub`, clamp `[MIN/4, MAX/4]` |
| `nonzero` (garantia compilador) | ausente | `NonzeroTick` para durações |
| `snap_nearest` (snap a frame) | ausente — gap para agentes que setam keyframes | implementado com `FrameRate::snap` |
| `timeBase` (layer vs comp) | ausente — `MediaTimeMap` só faz timeline→source | `timeBase: "layer"|"comp"` nos comandos |
| Display drop-frame vs sample-rate | `format_timecode` completo | separado de sample rate, com `TimeDisplay` enum |
| Float `source_duration/source_out` | usa `float()` internamente — deriva em L198-211 | inteiro puro, sem float em path crítico |

**Recomendação confirmada por código direto:**  
`CanonicalTime(Fraction)` é **suficiente e correto** para a maioria dos casos. NÃO substituir por `Tick` por preferência de performance sem prova de necessidade. **Adaptar seletivamente:**
1. Adicionar `saturating` em operações que possam overflow com valores extremos
2. Adicionar `snap_nearest(fps)` — necessário para `timeBase` correto
3. Eliminar `float()` em `source_duration`/`source_out` (L198-211) — usar Fraction pura
4. Documentar explicitamente `timeBase: layer|comp` como convenção de API

---

## Hermes `creative_timeline.py` — NLE Primitives (FACT)

```python
def split_clip_op(doc, composition_id, clip_id, split_time) -> tuple[Clip, Clip, list[...]]:
    """Split a clip (and its linked companion clips) at split_time."""
    # Respeita track.locked
    # Propagação simétrica para linked A/V clips
    # MediaTimeMap para cálculo correto de source_in no ponto de corte
```

**7 primitivas implementadas e testadas:** split, trim, ripple_delete, slip, slide, roll, set_clip_speed_op

**Lacunas identificadas:**
- `roll` não propaga para linked clips
- `set_speed(0)→freeze` não ajusta linked nem lida com overlaps/transições
- Sem audio mix

**Conclusão:** O NLE do Hermes é **superior ao EffectCraft** para edição editorial linear (track-based). EffectCraft é compositor de camadas (AE-style), não NLE de trilhas (Premiere-style). Esta é uma vantagem Hermes que deve ser preservada.
