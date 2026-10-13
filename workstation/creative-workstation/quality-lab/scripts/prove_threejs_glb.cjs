/* CQL-02: genuine GLB raster proof using installed Three.js + headless Chromium.
   Uses existing engine dependencies. Never produces synthetic success evidence. */
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { createRequire } = require('module');

async function main() {
  const [glbPath, evidenceDir] = process.argv.slice(2);
  if (!glbPath || !evidenceDir) throw new Error('usage: node prove_threejs_glb.cjs <input.glb> <evidence_dir>');
  const moduleDir = process.env.CQL_NODE_MODULES;
  if (!moduleDir || !fs.existsSync(moduleDir)) throw new Error('CQL_NODE_MODULES must point at preinstalled repository node_modules');
  const rootRequire = createRequire(path.join(path.dirname(moduleDir), 'package.json'));
  const { chromium } = rootRequire('playwright');
  const esbuild = rootRequire('esbuild');
  const source = [
    "import * as THREE from 'three';",
    "import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';",
    "window.cqlRender = async (b64, angle, energy) => {",
    " const bytes = Uint8Array.from(atob(b64), c=>c.charCodeAt(0));",
    " const loader = new GLTFLoader();",
    " const gltf = await new Promise((resolve, reject) => loader.parse(bytes.buffer, '', resolve, reject));",
    " const scene = new THREE.Scene(); scene.background = new THREE.Color(0x101018);",
    " const obj = gltf.scene; obj.position.set(-0.5,-0.5,0); obj.rotation.y = angle;",
    " scene.add(obj);",
    " const ambient = new THREE.AmbientLight(0xffffff, 0.3); scene.add(ambient);",
    " const key = new THREE.DirectionalLight(0xffffff, energy); key.position.set(1,2,4); scene.add(key);",
    " const camera = new THREE.PerspectiveCamera(50,1,0.01,100); camera.position.set(0,0,2.2); camera.lookAt(0,0,0);",
    " const renderer = new THREE.WebGLRenderer({antialias:false, preserveDrawingBuffer:true});",
    " renderer.setPixelRatio(1); renderer.setSize(256,256);",
    " renderer.render(scene,camera);",
    " const gl = renderer.getContext();",
    " const rgba = new Uint8Array(256*256*4); gl.readPixels(0,0,256,256,gl.RGBA,gl.UNSIGNED_BYTE,rgba);",
    " const bg = rgba.slice(0,4); let changed = 0;",
    " for(let i=0;i<rgba.length;i+=4) if(rgba[i]!==bg[0] || rgba[i+1]!==bg[1] || rgba[i+2]!==bg[2]) changed++;",
    " const png = renderer.domElement.toDataURL('image/png').split(',')[1];",
    " let meshes=0;obj.traverse(n=>{if(n.isMesh) meshes++;});",
    " const animationCount = gltf.animations.length;",
    " renderer.dispose();",
    " return {png,changed,meshes,animationCount, backgroundRGB:Array.from(bg.slice(0,3))};",
    "};"
  ].join('\n');
  const bundled = await esbuild.build({
    stdin: { contents: source, resolveDir: path.dirname(moduleDir), loader: 'js' },
    bundle: true, write: false, platform: 'browser', format: 'iife', nodePaths: [moduleDir],
  });
  const glb = fs.readFileSync(glbPath);
  const chrome = process.env.CQL_CHROME || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const browser = await chromium.launch({
    executablePath: chrome, headless: true,
    args: ['--use-gl=angle','--use-angle=swiftshader','--enable-webgl','--enable-unsafe-swiftshader','--no-sandbox']
  });
  try {
    const page = await browser.newPage({ viewport: { width: 300, height: 300 } });
    await page.setContent('<!doctype html><html><body><main id="scene">CQL</main></body></html>');
    await page.addScriptTag({content: bundled.outputFiles[0].text});
    const inputs = [[0.0, 1.0],[0.55,1.0],[0.55,0.25]];
    fs.mkdirSync(evidenceDir,{recursive:true});
    const shots = [];
    for(let i=0;i<inputs.length;i++){
      const [angle,energy] = inputs[i];
      const result = await page.evaluate(([b64,a,e])=>window.cqlRender(b64,a,e),[glb.toString('base64'),angle,energy]);
      if (result.meshes < 1 || result.changed < 100) throw new Error('GLB did not produce visible geometry pixels');
      const png = Buffer.from(result.png, 'base64');
      if (png.toString('hex',0,8)!=='89504e470d0a1a0a') throw new Error('Invalid PNG');
      const filename = 'threejs-glb-frame-'+i+'.png';
      fs.writeFileSync(path.join(evidenceDir,filename),png);
      shots.push({frame:i,angle,light:energy,png:filename,sha256:crypto.createHash('sha256').update(png).digest('hex'),...(({png,...x})=>x)(result)});
    }
    if(new Set(shots.map(s=>s.sha256)).size<3) throw new Error('Camera/object/light controls did not change rendered pixels');
    const replay = await page.evaluate(([b64,a,e])=>window.cqlRender(b64,a,e),[glb.toString('base64'),0,1]);
    const replaySha = crypto.createHash('sha256').update(Buffer.from(replay.png,'base64')).digest('hex');
    if (replaySha !== shots[0].sha256) throw new Error('Out-of-order repeat seek is not deterministic');
    const report = {
      status:'PASS_NATIVE', scope:'isolated Three.js GLTFLoader + Chromium/WebGL pixel proof (NOT composite/TaskRun/production)',
      inputGLB:path.resolve(glbPath),inputSha256:crypto.createHash('sha256').update(glb).digest('hex'),
      engine:'three.js GLTFLoader + Chromium WebGL', nativeFrames:shots,
    };
    fs.writeFileSync(path.join(evidenceDir,'threejs-glb-receipt.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report,null,2));
  } finally { await browser.close(); }
}
main().catch(err=>{ console.error('FAIL_NATIVE:',err.stack||err.message); process.exitCode=1; });
