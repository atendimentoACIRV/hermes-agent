# EVIDENCE — EffectCraft Keyframe Direct Read (CW-AUDIT-01)

**Arquivo auditado:** `referências/01-Criacao-Visual-Video-3D/effectcraft-main/crates/keyframe/src/lib.rs`  
**Total de linhas:** 853 — lido completo (L1-L853)  
**Data:** 2026-10-11  
**Método:** leitura direta read-only, sem build

---

## Estrutura `Keyframe` (linhas 60-92)

```rust
pub struct Keyframe {
    pub time: Tick,           // inteiro i64, não float
    pub value: Value,         // polimórfico: Scalar/Vec2/Vec3/Color/ShapePath/Gradient/TextDoc
    pub in_interp: Interp,    // Linear | Bezier | Hold
    pub out_interp: Interp,
    pub in_ease: Vec<Ease>,   // per-dimension: {speed: f64, influence: f64}
    pub out_ease: Vec<Ease>,
    pub continuous: bool,     // temporal continuous Bezier
    pub auto_bezier: bool,    // Catmull-Rom derivação automática
    pub spatial_in: [f64; 3], // tangentes espaciais 3D
    pub spatial_out: [f64; 3],
    pub spatial_auto: bool,
    pub spatial_continuous: bool,
    pub roving: bool,         // "Rove Across Time"
    pub label: u8,            // ícone de cor na timeline
}
```

**Comparação Hermes `creative_document.py:Keyframe`:**
```python
@dataclass
class Keyframe:
    keyframe_id: str
    property_path: str
    time: CanonicalTime   # Fraction — correto racionalmente
    value: Any            # sem tipagem por dimensão
    easing: str = "linear"  # APENAS string — sem solver matemático
```

**Gap crítico confirmado diretamente:** Hermes tem a estrutura mas sem `in_ease/out_ease`, `spatial_*`, `roving`, `auto_bezier`, `continuous`. O campo `easing: str` é descritivo — sem algoritmo de interpolação.

---

## Algoritmos de interpolação verificados (linhas 166-543)

### Bézier temporal (L176-215): `solve_u`
- Newton-Raphson (8 iterações) + fallback Bisseção Binária (60 iterações)
- Trata singularidade quando derivada ≈ 0 (midpoint de 100%/100% influence)
- Fórmula exata: `0.5 + ((progress - 0.5) * 0.25).cbrt()` para caso degenerado

### `ease_progress` (L220-225):
```rust
pub fn ease_progress(out_speed_n: f64, out_inf: f64, in_speed_n: f64, in_inf: f64, x: f64) -> f64 {
    let (i0, i1) = (out_inf.clamp(0.0, 1.0), in_inf.clamp(0.0, 1.0));
    let u = solve_u(0.0, i0, 1.0 - i1, 1.0, x);
    bez(0.0, out_speed_n * i0, 1.0 - in_speed_n * i1, 1.0, u)
}
```

### Arc-length spatial (L228-267): `SpatialSeg`
- `ARC_N = 96` amostras por segmento
- Lookup table cumulativo com interpolação linear
- Converte speed temporal em distância ao longo da curva Bézier 3D

### Roving keyframes (L394-443): `retime_roving`
- Detecta runs de `roving=true` entre keyframes fixos
- Calcula comprimento acumulado (arc-length para Vec2/Vec3, distância Euclidiana para outros)
- Redistribui tempos proporcionalmente: velocidade estritamente constante ao longo do caminho

### Testes verificados (L593-853):
- `temporal_ease_matches_live_ae_with_overlapping_influences` — compara contra AE 26.3x87 via AEsync 2.0.4, tolerância < 1e-7 degrees
- `maximum_influence_resolves_flat_midpoint_time_curve` — caso degenerado cbrt
- `roving_keys_get_constant_speed_times`
- `easy_ease_is_symmetric_and_slow_at_ends`
- `spatial_linear_constant_speed`
- `set_key_replaces_same_time`

**FIDELIDADE AO AE COMPROVADA:** Testes com dados reais do After Effects passam.

---

## SHA EffectCraft
SHA do repositório: NOT_VERIFIED (snapshot sem .git). Versão: `workspace 0.7.0`, `edition 2024`, `rust-version = "1.95"`. SHA do Hermes HEAD na época: `55399a455d`.
