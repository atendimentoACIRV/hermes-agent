"""Native EffectCraft 2-layer proof: pinned HF RGBA sequence and GLB WebGL PNGs."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image


def sha(file: Path) -> str:
    return hashlib.sha256(file.read_bytes()).hexdigest()


def cli_run(cli: Path, *args: object) -> str:
    result = subprocess.run([str(cli), *(str(a) for a in args)],
                            text=True, capture_output=True, timeout=55, check=False)
    if result.returncode:
        raise RuntimeError(f"EffectCraft exit {result.returncode}: {args!r}\n{result.stdout[-600:]}\n{result.stderr[-600:]}")
    return result.stdout


def prove(cli: Path, hf: Path, three: Path, out: Path) -> dict:
    if not cli.is_file():
        raise FileNotFoundError(f"EffectCraft CLI unavailable: {cli}")
    if out.exists() and any(out.iterdir()):
        raise ValueError("output directory must be empty; preserve existing receipts")
    out.mkdir(parents=True, exist_ok=True)
    sequences: dict[str, Path] = {}
    for label, source in (("hf", hf), ("three", three)):
        files = sorted(source.glob("*.png"))
        if not files:
            raise ValueError(f"missing PNG frames for {label}")
        target = out / "assets" / label
        target.mkdir(parents=True)
        for i, file in enumerate(files):
            shutil.copy2(file, target / f"clip_{i:04d}.png")
        sequences[label] = target

    base, hf_project, hybrid = (out / n for n in
                                ("00-base.ecproj", "01-hf.ecproj", "02-hf-three.ecproj"))
    comp = {"name": "CQL3DHybrid", "width": 640, "height": 360,
            "frameRate": 30, "duration": 2}
    cli_run(cli, "--empty", "--save-as", base, "exec", "comp.new",
            "--params", json.dumps(comp), "--json")
    previous = base
    for name, dest in (("hf", hf_project), ("three", hybrid)):
        payload = {"paths":[str(sequences[name]/"clip_0000.png")],
                   "sequence":True,"frameRate":30,"addToComp":True}
        cli_run(cli, "--project", previous, "--save-as", dest, "exec",
                "file.import", "--params", json.dumps(payload,separators=(",",":")), "--json")
        previous = dest

    reopened = json.loads(cli_run(cli, "--project", hybrid, "info", "--json"))
    layers = max((int(c.get("layers",0)) for c in reopened["project"]["items"]
                  if c.get("type")=="Composition"), default=0)
    if layers < 2:
        raise ValueError(f"native reopened project has {layers} layers, expected 2")

    pixels = {}
    for name, project, seek in (("hf-only",hf_project,"0"),
                                ("both-at-zero",hybrid,"0"),
                                ("both-at-next",hybrid,"0.066667")):
        destination = out / (name+".png")
        cli_run(cli,"--project",project,"render-frame","--time",seek,"--out",destination)
        with Image.open(destination) as im:
            im.load()
            if im.size != (640,360):
                raise ValueError(f"rendered size mismatch: {im.size}")
            pixels[name] = im.convert("RGBA").tobytes()
    if pixels["hf-only"] == pixels["both-at-zero"]:
        raise ValueError("Three.js footage did not affect native composite pixels")
    if pixels["both-at-zero"] == pixels["both-at-next"]:
        raise ValueError("native seek did not produce different pixels")
    # Existing EffectCraft commands, not a replacement effects engine.
    titled, effected, blurred = (out / name for name in
                                 ("03-hybrid-title.ecproj", "04-hybrid-effect.ecproj",
                                  "05-hybrid-blur20.ecproj"))
    heading = {"text":"CQL / HERMES", "size":42,"fill":"#ffffff"}
    cli_run(cli,"--project",hybrid,"--save-as",titled,"exec","layer.newText",
            "--params",json.dumps(heading,separators=(",",":")),"--json")
    title_info = json.loads(cli_run(cli,"--project",titled,"info","--json"))
    active_layers = title_info["activeComp"]["layers"]
    if not any(layer["type"]=="Text" for layer in active_layers):
        raise ValueError("native typography layer missing")
    footage = next((layer for layer in active_layers if layer["type"]=="Footage"),None)
    if footage is None:
        raise ValueError("native footage layer missing")
    spec = {"layer":footage["id"],"effect":"Gaussian Blur"}
    cli_run(cli,"--project",titled,"--save-as",effected,"exec","effect.apply",
            "--params",json.dumps(spec,separators=(",",":")),"--json")
    cli_run(cli,"--project",effected,"--save-as",blurred,"set","-",footage["id"],
            "effects/#1/blurriness","20","--json")
    props = json.loads(cli_run(cli,"--project",blurred,"props","-",footage["id"],"--flat","--json"))
    if not any(prop["path"]=="effects/#1/blurriness" and prop["value"]==20
               for prop in props["properties"]):
        raise ValueError("Gaussian Blur parameter not saved")
    decorated = []
    for n, project in enumerate((hybrid,titled,blurred)):
        png = out / f"decorated-{n}.png"
        cli_run(cli,"--project",project,"render-frame","--time","0.033333","--out",png)
        with Image.open(png) as pic:
            pic.load()
            decorated.append(hashlib.sha256(pic.convert("RGBA").tobytes()).hexdigest())
    if len(set(decorated)) != 3:
        raise ValueError("typography or blur did not alter native decoded pixels")
    receipt = {
        "status":"PASS_NATIVE",
        "scope":"isolated real EffectCraft CLI, editable project reopen, two-layer pixel output; NOT Hermes TaskRun/Electron",
        "cli_sha256":sha(cli),
        "ecproj":str(hybrid.resolve()),"ecproj_sha256":sha(hybrid),
        "native_layers":layers,
        "hf_input_frames":len(list(sequences["hf"].glob("*.png"))),
        "three_input_frames":len(list(sequences["three"].glob("*.png"))),
        "render_hashes":{name:sha(out/(name+".png")) for name in pixels},
        "native_reopened":True, "second_layer_changed_pixels":True,
        "seek_changed_pixels":True,
        "native_blur20_ecproj":str(blurred.resolve()), "native_blur20_sha256":sha(blurred),
        "native_text_added":True,"gaussian_blur20_verified":True,
        "decorated_rgb_sha256":decorated
    }
    (out/"hybrid-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return receipt


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--cli",type=Path,required=True)
    parser.add_argument("--hyperframes",type=Path,required=True)
    parser.add_argument("--threejs",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    opts=parser.parse_args()
    try:
        print(json.dumps(prove(opts.cli,opts.hyperframes,opts.threejs,opts.out),indent=2))
    except Exception as exc:
        print(json.dumps({"status":"FAIL","reason":str(exc)},indent=2),file=sys.stderr)
        sys.exit(1)
