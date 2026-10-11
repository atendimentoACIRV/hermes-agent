# 04 — Craft Family Synergy (CW-AUDIT-01)

**Alvos:** `filmcraft-main` (ws `0.6.0`) + `photocraft-main` (ws `0.7.0`) + `effectcraft-main` (ws `0.7.0`) — snapshots sem `.git`, SHA NOT_VERIFIED · todas `MIT OR Apache-2.0` + NOTICE + ATTRIBUTION + clean-room (sem GPL/Adobe, codecs de spec, ffmpeg só oráculo)
**Pin cruzado FACT:** `effectcraft-main/Cargo.toml:72-93` `filmcraft-* git rev="2c5ba7a72619935f0481f99d59409e0d1844b234"` — só `media/export/interchange` podem depender. ADR `plan/adr/0001`.

## 4.1 FilmCraft — engine NLE (ADAPT_CONTRACT + ADAPT_ALGORITHM)

Arquitetura: `Cargo.toml:1-58` L0 `time,geom,color,bitstream` + codecs standalone (`isobmff,matroska,mxf,cfb,mpegts,ogg,h264,h264enc,hevc,vp9,av1,mpeg2v,prores,dnx,apv,aac,ac3,opus` só→`bitstream`) → L1 `frame,media,project,audio-dsp,text` → L2 `edit,codecs,interchange,captions,speech,tts` → L3 `render,gpu,export,golden,scopes` → L4 `engine{Session,registry,undo,jobs}` → L5 `ui-egui,automation,platform` (único `unsafe` FFI) → L6 apps + `cargo xtask layers`.

Documento (`project/src/lib.rs`): `Project{root:Bin,items:Map<ItemId→Media|Sequence|Subclip|AdjustmentLayer|Graphic>}` · `Sequence{settings,video_tracks/audio_tracks:Vec<Track>,submix,markers,mark_in/out,multicam,merged}` · `Track{locked,sync_lock default true,targeting,mute/solo,items sorted never-overlapping,transitions,volume/pan/effects/mixer}` · `TrackItem{id,item,start:Tick,duration:Tick,source_in:Tick,speed:f64,reverse,enabled,link:Option<u64>,group,effects,gain,multicam,time_interpolation}` · `Sequence::check()` invariantes (`lib.rs:965,1033`).

Tempo: `filmcraft_time::Tick(i64)` `TICKS_PER_SECOND=254_016_000_000` (= EffectCraft, compatível) + `FrameRate{num,den}` + timecode só display (`architecture.md:103-120`).

NLE (`edit/src/lib.rs` álgebra pura): `split_track_at:95,insert_track_gap:169,overwrite:251,insert:269,lift:334,extract:346,ripple_delete_items:434,close_gap:469,trim:705,ripple_trim_group:760,roll:863,slip:910,slide:923,slide_items:984,rate_stretch:1003` + `transcript ripple_delete_ranges` + `captions split/trim`. Engine: `sequence.addEdit,timeline.place/razor,clip.remix` + Trim Monitor + `J/K/L` + `Q/W` + `Ctrl+T` (`commands.rs:2460`, `README:84`).

Linked A/V: `link:Option<u64>` + `linked_selection default true` (`engine/src/lib.rs:252,469`); `timeline_hit/move` respeita; `linked:false` desliga; `commands.rs:324,418,1777`, `keyboard.rs:251`, `timeline.rs:1262 Link`.

Interchange (`interchange/src/`): `fcp7.rs` xmeml v4/v5 + `fcpxml.rs` 1.9-1.11 + `otio.rs` + `edl.rs` CMX3600 + `aaf/read|write.rs` sobre `cfb` + `omf/` + `comp.rs/common.rs(ImportBuilder link_id/place/overwrite)/essence.rs/ale.rs/wav.rs`. Import merge bins+media+sequences 1 undo + relink (`README:207-218`).

Melhor capacidade: Tick + `edit` puro testável + interchange mais completo OSS + 650+ commands `enabled()->Result` + mesmo dispatch UI/CLI/control/MCP + codecs Rust bit-exact.

## 4.2 PhotoCraft — engine raster (ADAPT_ALGORITHM + ADAPT_CONTRACT)

Arquitetura: `version 0.7.0` L0 `geom cms color raster|psd codecs tablet standalone` → L1 `doc` → L2 `ops paint algo text vector` → L3 `compose gpu format` → L4 `io plugins` → L5 `engine` → L6 `ui-egui automation` + `xtask layers|wasm|corpus|parity|perf|scorecard` (`AGENTS.md §2`, `doc/src/lib.rs:1-9`).

Documento (`doc/src/lib.rs:52-1315`): `LayerId/DocId` AtomicU64, `children[0]=bottom`, `LayerContent::Group/Adjustment/Fill/Pixel/Text/Shape/Smart` + `vector_mask/clipping/Locks/label`, `Group:290,SmartObject:469,VectorMask:vector.rs:188,Artboard:comps.rs:155,LayerComp,Slices,blend_if`. 16 adjustments (`adjust.rs:133`: BrightnessContrast/Levels+hist/Curves/Exposure/Vibrance/HueSat/ColorBalance/BlackWhite/PhotoFilter/ChannelMixer/ColorLookup/Invert/Posterize/Threshold/GradientMap/SelectiveColor + Shadows/Highlights/HDR) + `effects.rs` (Drop/Inner Shadow, Glow, Bevel, Satin, Stroke, Overlays, Patt) + 27 blends PS + 6 PDN.

PSD/PSB (`photocraft-psd` da spec Adobe): v1/v2 (`header.rs:22 is_psb`), RLE 2B vs 4B (`compression.rs:199`), `PSB_LONG_KEYS[21]` (`tagged.rs:20`), `>30000px→PSB` (`file.rs:271`), >2GiB testado, re-save 307/309 psd-tools + 169/170 ag-psd, parser byte-identical, composite oracle vs Photoshop (`README:213-219`). Formatos: TIFF layered, PDN3, OpenRaster, SVG→shape, PNG/JPEG/TIFF/WebP/GIF/BMP/TGA/ICO/QOI/PNM/EXR/HDR, `.pcraft` nativo, Affinity read-only, HEIC opt, AVIF write-only.

Cor (`cms` ICC v2/v4 puro Rust `ICC.1:2010`): `Profile(matrix/TRC/mft/clut/curv/para)+write v4`, Intents, Transform cached, tetrahedral, Bradford/D50, `srgb/linear_gray/coated-cmyk.icc`, GamutCheck + soft-proof `⌘Y` (`lib.rs,pipeline.rs,clut.rs,curve.rs,math.rs,builtin.rs,gamut.rs`). Docs RGB/Gray/CMYK/Lab 8/16/32f — todo tool toda depth.

Tiles (`raster/src/lib.rs:1,38-90`): `Surface = plano infinito tiles 256×256 esparsos CoW, missing→default, clonar=O(tiles), mutar copia tocados`; `Tile{Bpp}`, `BTreeMap<Coord,Arc<Tile>>`, `take_tiles/put_tiles`, Interrupt per-tile rayon. CPU oracle + wgpu testados entre si.

Brushes (`paint/{brush,lib,dynamics,render}.rs`): `BrushSettings{size,hardness,spacing,tip,dynamics,scattering,texture,dual,colorDynamics,transfer,pose,smoothing,wetEdges,build-up}` + Preset + Define-from-Selection, dabs determinísticos seed/hash, pressão/tilt/rotation, `tablet` unsafe só macos/X11. 55 tools (`README:182`).

Comandos: 500+ `engine/src/*_cmds.rs specs()`, `Session::execute`, `automation/{headless,server,rpc,bridge}.rs` rmcp, CLI `run/batch/convert/info/commands/mcp`, `--control` loopback + offscreen screenshot. Tools `command_list/run/batch/doc_inspect/render_preview/doc_save + ui_* bridge`.

Complemento sem 2º editor: `Adjustment` stack non-destructive + `cms::Transform` + `Surface` CoW + `BrushSettings` math + `Actions record/replay` macro JSON → pipeline imagem Hermes. `psd` só se ler PSD alheio.

## 4.3 Mapa de crates compartilhados — NÃO DUPLICAR

| FilmCraft (source of truth) | EffectCraft consome | Hermes deve usar |
|---|---|---|
| `filmcraft-time (Tick)` | `effectcraft-time` wrapper compat | **FilmCraft Tick** — nunca 3º clock |
| `filmcraft-color / -geom / -frame` | direto | idem |
| `filmcraft-media + codecs/*` | `filmcraft-media/codecs` + `effectcraft-media` adapter | só WRAP subprocess/FFI |
| `filmcraft-project (Sequence/Track/TrackItem)` | `filmcraft-project` + `effectcraft-project/model/track/segment` próprios (precomp layer) | NLE=FilmCraft model, MoGraph=EffectCraft model, mapear via `interchange` |
| `filmcraft-interchange` | direto | único conversor EDL/FCP7/FCPXML/OTIO |
| `filmcraft-h264enc/prores/aac/isobmff` | `export` | idem |

EffectCraft próprios (manter): `raster,path,keyframe,effects,expr,lottie,svg,pdf,psd,encoders,host,plugin(wasmi),script`.

**Regra:** recomendação que precise tempo/cor/frame/media/interchange → `filmcraft-*` pinado; EffectCraft só `effects/expr/track/segment/model`. Nunca dois clocks/CMS/EDL parsers.

| Projeto | Adoção | Motivo |
|---|---|---|
| filmcraft | ADAPT_CONTRACT + ADAPT_ALGORITHM | bus humano+IA + Tick + edit + interchange |
| photocraft | ADAPT_ALGORITHM + ADAPT_CONTRACT | doc/adjustment/cms/tiles/brush |
| effectcraft | ADAPT_CONTRACT (contexto) | MoGraph, reusa filmcraft pin |
