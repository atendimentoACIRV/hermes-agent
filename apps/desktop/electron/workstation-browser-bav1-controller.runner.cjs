'use strict'
/* BAV-03 test-only: reuse Hermes loopback controller, no second browser owner. */
const assert=require('node:assert/strict')
const fs=require('node:fs'),os=require('node:os'),path=require('node:path')
const http=require('node:http'),{spawn}=require('node:child_process')
const electron=require('electron')
const procedure=JSON.parse(fs.readFileSync(path.join(__dirname,'workstation-browser-bav1-procedure.fixture.json'),'utf8'))
assert.equal(procedure.version,1)
assert.equal(procedure.lifecycle,'discovered')
assert.equal(procedure.steps.length,4)
const root=fs.mkdtempSync(path.join(os.tmpdir(),'hermes-bav-procedure-'))
const delay=ms=>new Promise(r=>setTimeout(r,ms))
let server,child,childStderr=''
async function run(){
 let effects=0
 server=http.createServer((req,res)=>{
  if(req.url==='/form'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<!doctype html><title>BAV procedure fixture</title><label for="note">Note</label><input id="note" data-testid="note-input"><button id="save" data-testid="save-button" onclick="fetch(\'/effect?note=\'+encodeURIComponent(document.querySelector(\'#note\').value)).then(r=>r.text()).then(t=>document.querySelector(\'#status\').textContent=t)">Save</button><p id="status">Pending</p>');return}
  if(req.url.startsWith('/effect?note=')){effects++;res.end('Saved: '+new URL(req.url,'http://localhost').searchParams.get('note'));return}
  res.statusCode=404;res.end('Not found')
 })
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve))
 const site='http://127.0.0.1:'+server.address().port+'/form'
 child=spawn(electron,[path.join(__dirname,'workstation-browser-bav1-cdp.child.cjs'),'--no-sandbox'],{cwd:path.resolve(__dirname,'..'),stdio:['ignore','pipe','pipe','ipc'],windowsHide:true,env:{...process.env,BAV_TEMP_ROOT:root,BAV_MODE:'controller',BAV_CDP_PORT:'0',BAV_FIXTURE_URL:site}})
 let stdout='',stderr=''
 child.stdout.on('data',x=>stdout+=x)
 child.stderr.on('data',x=>{stderr+=x;childStderr+=x})
 for(let i=0;i<160&&!stdout.includes('BAV_READY');i++){if(child.exitCode!==null)throw new Error('Electron exit '+stderr);await delay(150)}
 assert.match(stdout,/BAV_READY/,'isolated native Hermes task must be ready')
 const pathControl=path.join(root,'controller.json')
 assert.ok(fs.existsSync(pathControl),'native authenticated controller must be running')
 const ctrl=JSON.parse(fs.readFileSync(pathControl,'utf8'))
 assert.ok(ctrl.url.startsWith('http://127.0.0.1:'))
 let callId=0
 async function invoke(action,args={}){
  const result=await fetch(ctrl.url+'/v1/action',{method:'POST',headers:{'Authorization':'Bearer '+ctrl.token,'Content-Type':'application/json'},body:JSON.stringify({action,arguments:args,task_id:'bav-cdp-test',session_id:'offline-session',run_id:'bav-run',operation_id:'bav-op-'+(++callId)})})
  const body=await result.json()
  assert.equal(result.status,200,action+': '+JSON.stringify({error:body.error,error_code:body.error_code}))
  assert.equal(body.success,true,action+' controller rejected')
  return body.result
 }
 // Test-only JSON-lines bridge: Python canonical ProceduralMemory/runner asks the
 // existing authenticated controller to execute, never a parallel BrowserRuntime.
 async function runPersistentWorker(mode,note){
  // The controller rejects invented run IDs; the fixture owns bav-run.
  const repoRoot=path.resolve(__dirname,'../../..')
  const storage=path.join(root,'procedures.json')
  const py=spawn('python',['-u',path.join(__dirname,'workstation-browser-bav1-memory.worker.py'),
   mode,note,site,storage,path.join(__dirname,'workstation-browser-bav1-procedure.fixture.json')],{
    cwd:repoRoot,windowsHide:true,stdio:['pipe','pipe','pipe'],
    env:{...process.env,PYTHONPATH:[repoRoot,'C:\\Github\\hermes-agent\\.venv\\Lib\\site-packages'].join(path.delimiter)}
  })
  let data='',err='',done=null,queue=Promise.resolve()
  py.stderr.on('data',x=>err+=x.toString())
  py.stdout.on('data',chunk=>{
   data+=chunk.toString()
   while(data.includes('\n')){
    const index=data.indexOf('\n')
    const line=data.slice(0,index); data=data.slice(index+1)
    if(!line.trim())continue
    queue=queue.then(async()=>{
     const message=JSON.parse(line)
     if(message.done){done=message;return}
     if(!message.rpc)throw new Error('unexpected worker output')
     const result=message.rpc==='test_effect_count'?effects:await invoke(message.rpc,message.args)
     py.stdin.write(JSON.stringify({ok:true,result})+'\n')
    }).catch(e=>{err+='\nbridge error '+String(e);try{py.kill()}catch{}})
   }
  })
  const code=await new Promise(resolve=>py.on('exit',resolve))
  await queue
  assert.equal(code,0,mode+' '+note+' worker failed '+err.slice(-3000))
  assert.ok(done&&done.verified,'worker must provide independent verified effect '+err)
  return done
 }

 // Parameterized deterministic procedure: known URL, semantic discovery, operation, independent read.
 async function runProcedure(note,reacquire=false){
  assert.ok(typeof note==='string'&&note.length>0&&note.length<=64,'typed note input contract')
  const nav=await invoke('browser_navigate',{url:site})
  assert.ok(nav.receipt)
  const snap=await invoke('browser_snapshot')
  const inputs=snap.elements.filter(x=>x.tag==='input')
  assert.equal(inputs.length,1,'unique input in controlled fixture')
  const input=inputs[0]
  const typed=await invoke('browser_type',{ref:reacquire?'@e999':input.ref,text:note,clear:true,semantic_anchor:procedure.steps[1].fallback_anchors[0]})
  assert.ok(typed.receipt)
  const next=await invoke('browser_snapshot')
  const save=next.elements.find(x=>x.tag==='button'&&/Save/.test(x.label||''))
  assert.ok(save,'semantic Save button')
  const click=await invoke('browser_click',{ref:reacquire?'@e998':save.ref,semantic_anchor:procedure.steps[2].fallback_anchors[0]})
  assert.ok(click.receipt)
  // Independently read the observable semantic state; owner receipt alone does not prove remote effect.
  const state=await invoke('browser_snapshot',{full:true})
  assert.ok(String(state.snapshot||'').includes(procedure.steps[3].expectation.replace('{note}',note)),'expected server readback: '+JSON.stringify({snapshot:String(state.snapshot||'').slice(-180),effects}))
 }
 if(process.env.BAV_PERSISTENCE_TEST==='1'){
  const seed=await runPersistentWorker('seed','Alpha')
  const replay1=await runPersistentWorker('replay','Beta')
  const replay2=await runPersistentWorker('replay','Gamma')
  assert.equal(seed.procedure_id,replay1.procedure_id)
  assert.equal(seed.procedure_id,replay2.procedure_id)
  assert.equal(replay1.completed_steps,4)
  assert.equal(replay2.completed_steps,4)
  assert.equal(effects,3,'all test-only effects independently confirmed')
  console.log('BAV05_PERSISTENT_RUN_MATCHING_PASS '+JSON.stringify({
   executions:3,effects,memoryReloads:2,modelCalls:0,controllerCalls:callId,
   procedureId:seed.procedure_id,existingBrowserOwner:true}))
 }else{
  await runProcedure('Alpha',false)
  await runProcedure('Beta',true)
  assert.equal(effects,2,'exactly one test-only mutation per input')
  console.log('BAV03_CONTROLLER_PROCEDURE_PASS '+JSON.stringify({executions:2,effects,calls:callId,modelCalls:0,existingBrowserOwner:true}))
 }
}
run().catch(err=>{console.error('BAV03_CONTROLLER_PROCEDURE_FAIL',String(err.stack||err),'CHILD_DEBUG:',childStderr.slice(-2000));process.exitCode=1}).finally(async()=>{
 try{child?.send({type:'close'})}catch{}
 if(child){await Promise.race([new Promise(r=>child.once('exit',r)),delay(1700)]);if(child.exitCode===null)child.kill()}
 try{server?.close()}catch{}
 try{fs.rmSync(root,{recursive:true,force:true,maxRetries:8,retryDelay:250})}catch{}
})
