"use strict";
/* CQL-03: external black-box Chromium component probe, NOT authenticated Electron E2E. */
const fs=require("node:fs"), path=require("node:path"), crypto=require("node:crypto");
const {execFileSync}=require("node:child_process"), {createRequire}=require("node:module");
const head=process.env.CQL_TARGET_HEAD,root=process.env.CQL_PR81_CHECKOUT;
const modules=process.env.CQL_NODE_MODULES,dir=process.env.CQL_UI_REPORT_DIR;
if(!root||!head||!modules||!dir||!/^[0-9a-f]{40}$/.test(head))throw Error("CQL_PR81_CHECKOUT/CQL_TARGET_HEAD/CQL_NODE_MODULES/CQL_UI_REPORT_DIR required");
const actual=execFileSync("git",["-C",root,"rev-parse","HEAD"],{encoding:"utf8"}).trim();
if(actual!==head)throw Error("Refusing to test changed candidate HEAD: "+actual);
const candidate=path.join(root,"apps/desktop/src/app/creative-workspace");
const loader=createRequire(path.join(path.dirname(modules),"package.json"));
const esbuild=loader("esbuild"),{chromium}=loader("playwright");
const names=["CreativeWorkspaceContext.tsx","CreativeTimeline.tsx","CreativeInspector.tsx","CreativePreview.tsx","CreativeGraphEditor.tsx","CreativeToolbar.tsx"];
const srcHash=Object.fromEntries(names.map(n=>[n,crypto.createHash("sha256").update(fs.readFileSync(path.join(candidate,n))).digest("hex")]));
const importLine=(exports,file)=>"import { "+exports+" } from "+JSON.stringify(path.join(candidate,file).replaceAll("\\","/"))+";";
const entry=[
  "import React from 'react';import {createRoot} from 'react-dom/client';",
  importLine("CreativeWorkspaceProvider,useCreativeWorkspace","CreativeWorkspaceContext.tsx"),
  importLine("CreativeTimeline","CreativeTimeline.tsx"),
  importLine("CreativeInspector","CreativeInspector.tsx"),
  importLine("CreativePreview","CreativePreview.tsx"),
  importLine("CreativeGraphEditor","CreativeGraphEditor.tsx"),
  importLine("CreativeToolbar","CreativeToolbar.tsx"),
  "const h=React.createElement;",
  "function Consumer(){const c=useCreativeWorkspace();",
  "window.__CQL={accept:x=>c.acceptCanonicalHead(x),selectLayer:x=>c.selectLayer(x),",
  "state:()=>({rev:c.canonicalRevision?.revisionId??null,playhead:c.playheadTime,playing:c.isPlaying,",
  "tracks:[...c.selection.selectedTrackIds],clips:[...c.selection.selectedClipIds],layers:[...c.selection.selectedLayerIds]})};",
  "return h('main',null,h(CreativeToolbar),h(CreativeTimeline),h(CreativeInspector),h(CreativePreview),window.__INCLUDE_GRAPH?h(CreativeGraphEditor):null);}",
  "createRoot(document.getElementById('root')).render(h(CreativeWorkspaceProvider,null,h(Consumer)));"
].join("\n");
const rep="a".repeat(32),rev="d".repeat(32),tid="c".repeat(32),lid="9".repeat(32);
const fixture={project_id:rep,revision_id:rev,etag:'"'+ "1".repeat(16)+"-"+ "1".repeat(16)+'"',
source:{schema_version:1,project_id:rep,name:"CQL Canonical Snapshot",assets:{},metadata:{},
compositions:[{composition_id:"b".repeat(32),name:"Main",width:640,height:360,duration:"10",fps:{num:30000,den:1001},
tracks:[{track_id:tid,name:"Video A",kind:"video",z_index:0,locked:false,muted:false,solo:false,clips:[
{clip_id:"e".repeat(32),track_id:tid,asset_id:"f".repeat(32),name:"Visual Clip",
timeline_range:{start:"0",end:"5"},source_in:"0",speed:1,reverse:false,freeze:false,linked_clip_ids:[]}]}],
layers:[{layer_id:lid,name:"CQL Title",kind:"vector_svg",declared_parameters:{text:"CQL"},opaque_code:null,
transform:{x:20,y:45,opacity:1},keyframes:[
{keyframe_id:"8".repeat(32),property_path:"transform.x",time:"0",value:20,easing:"linear"},
{keyframe_id:"7".repeat(32),property_path:"transform.x",time:"1",value:220,easing:"ease-in"}]}]}]}};
const obs=[];
const record=(id,expect,observed,pass,scope)=>obs.push({id,expect,observed,status:pass?"PASS_UNIT":"FAIL",scope:scope||"Chromium React component, synthetic canonical projection (not Electron E2E)"});
(async()=>{
const bundle=await esbuild.build({stdin:{contents:entry,resolveDir:path.dirname(modules),loader:"js"},
bundle:true,write:false,platform:"browser",format:"iife",jsx:"automatic",nodePaths:[modules],logLevel:"silent",
plugins:[{name:"cql-one-react-instance",setup(build){build.onResolve({filter:/^react(?:\/jsx-runtime|\/jsx-dev-runtime)?$|^react-dom(?:\/client)?$/},args=>({path:loader.resolve(args.path)}));}}]});
const browser=await chromium.launch({headless:true,executablePath:process.env.CQL_CHROME||"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",args:["--no-sandbox"]});
try{
fs.mkdirSync(dir,{recursive:true});
const open=async(graph)=>{
 const page=await browser.newPage({viewport:{width:1280,height:880}});
 const errors=[];page.on("pageerror",e=>errors.push(e.message));page.on("console",m=>{if(m.type()==="error")errors.push(m.text())});
 await page.setContent("<!doctype html><html><body><div id='root'></div></body></html>");
 if(graph)await page.evaluate(()=>{window.__INCLUDE_GRAPH=true});
 await page.addScriptTag({content:bundle.outputFiles[0].text});
 try { await page.waitForFunction(()=>Boolean(window.__CQL),null,{timeout:7000}); } catch (e) {console.error("BOOT_ERRORS",errors,"ROOT",await page.locator("#root").innerHTML());throw e;}
 return {page,errors};
};
let {page,errors}=await open(false);
const empty=await page.locator(".creative-timeline").count();
record("UX-EMPTY","No timeline before source HEAD",empty,empty===0);
await page.evaluate(f=>window.__CQL.accept(f),fixture);
await page.locator(".creative-timeline-clip").waitFor();
const initial=await page.evaluate(()=>window.__CQL.state());
record("UX-HEAD","Only accepted revision enters view",initial.rev,initial.rev===rev);
await page.locator(".creative-timeline-track").first().click();
const track=await page.locator(".creative-inspector").innerText();
record("UX-TRACK","Inspector displays selected track",track.includes("Track: Video A"),track.includes("Track: Video A"));
await page.locator(".creative-timeline-clip").first().click();
const clip=await page.locator(".creative-inspector").innerText();
record("UX-CLIP","Inspector displays selected clip",clip.includes("Clip: Visual Clip"),clip.includes("Clip: Visual Clip"));
await page.locator(".creative-timeline-time-ruler").click({position:{x:153,y:10}});
const seek=await page.evaluate(()=>window.__CQL.state());
const preview=await page.locator(".creative-preview-time").innerText();
record("UX-SEEK","Ruler click updates preview and leaves source revision intact",{seek:seek.playhead,preview,rev:seek.rev},Math.abs(seek.playhead-1.53)<.03&&preview.startsWith("1.53")&&seek.rev===rev);
await page.locator('button[title^="Step Forward"]').click();
const stepped=await page.evaluate(()=>window.__CQL.state());
const delta=stepped.playhead-seek.playhead;
record("UX-RATIONAL-FPS","One frame step at canonical 30000/1001fps equals 1001/30000s",delta,Math.abs(delta-1001/30000)<1e-7);
await page.getByRole("button",{name:"Play",exact:true}).click();
const afterPlay=await page.evaluate(()=>window.__CQL.state());
record("UX-PREVIEW-PLAY","Preview Play updates playback state",afterPlay.playing,afterPlay.playing);
const speed=page.locator(".creative-inspector input[type=number]").first();
await speed.fill("1.5");
const afterSpeed=await page.evaluate(()=>window.__CQL.state());
record("UX-INSPECTOR-SPEED","Inspector property edit produces acknowledged canonical revision",afterSpeed.rev,afterSpeed.rev!==rev);
const samples=[];
for(let i=0;i<12;i++){
 const x=22+i*16,expectedTime=x/100,start=process.hrtime.bigint();
 await page.locator(".creative-timeline-time-ruler").click({position:{x,y:10}});
 await page.waitForFunction(t=>Math.abs(parseFloat(document.querySelector(".creative-preview-time")?.textContent||"NaN")-t)<.012,expectedTime,{timeout:2000});
 samples.push(Number(process.hrtime.bigint()-start)/1e6);
}
const sorted=[...samples].sort((a,b)=>a-b);
const seekBenchmark={scope:"Chromium React local ruler click -> visible Preview text only (NOT pixel render or Electron product latency)",
 count:samples.length,ms:samples.map(v=>Math.round(v*100)/100),
 p50_ms:(sorted[5]+sorted[6])/2,p95_nearest_rank_ms:sorted[Math.ceil(samples.length*.95)-1]};
await page.screenshot({path:path.join(dir,"creative-chromium-component.png"),fullPage:true});
await page.close();
let graph=await open(true);
await graph.page.evaluate(f=>window.__CQL.accept(f),fixture);
await graph.page.locator(".creative-graph-editor").first().waitFor();
await graph.page.evaluate(id=>window.__CQL.selectLayer(id),lid);
await graph.page.waitForTimeout(250);
const show=await graph.page.locator(".creative-graph-editor:not(.empty)").count();
record("UX-GRAPH-HOOKS","Selected keyed layer renders graph without React hook-order error",{show,errors:graph.errors.slice(0,3)},show>0&&graph.errors.length===0);
await graph.page.close();
const result={mission:"CQL-001",targetPR:81,head:actual,scope:"Chromium component probe; synthetic schema-valid head; no native Electron/TaskRun authority",candidateSourceSha256:srcHash,
pass:obs.filter(x=>x.status==="PASS_UNIT").length,fail:obs.filter(x=>x.status==="FAIL").length,seekBenchmark,errors,graphErrors:graph.errors,observations:obs};
fs.writeFileSync(path.join(dir,"CQL_CHROMIUM_UI_OBSERVATIONS.json"),JSON.stringify(result,null,2)+"\n");
console.log(JSON.stringify({head:actual,pass:result.pass,fail:result.fail,observations:obs,graphErrors:graph.errors.slice(0,2)},null,2));
if(!obs.some(o=>o.id==="UX-CLIP"&&o.status==="PASS_UNIT"))process.exitCode=2;
}finally{await browser.close()}
})().catch(e=>{console.error("CQL-UI-PROBE-ERROR",e.stack||e);process.exitCode=1});
