'use strict'
/* BAV-01 RED/GREEN: external Playwright attached to isolated Hermes WebContentsView. */
const assert=require('node:assert/strict')
const fs=require('node:fs'),os=require('node:os'),path=require('node:path')
const http=require('node:http'),net=require('node:net')
const {spawn}=require('node:child_process')
const electron=require('electron')
const {chromium}=require('playwright-core')
const root=fs.mkdtempSync(path.join(os.tmpdir(),'hermes-bav1-'))
const deadline=(promise,ms,label)=>Promise.race([promise,new Promise((_,reject)=>setTimeout(()=>reject(new Error(label+' timed out')),ms))])
async function availablePort(){const s=net.createServer();await new Promise(r=>s.listen(0,'127.0.0.1',r));const p=s.address().port;await new Promise(r=>s.close(r));return p}
let child,browser,server
async function main(){
  let effects=0
  server=http.createServer(async(req,res)=>{
    if(req.url==='/index'){res.setHeader('Content-Type','text/html; charset=utf-8');res.end('<!doctype html><title>BAV-01 isolated test</title><label for="note">Note</label><input id="note"><button onclick="fetch(\'/effect?note=\'+encodeURIComponent(document.querySelector(\'#note\').value)).then(r=>r.text()).then(t=>document.querySelector(\'#status\').textContent=t)">Save</button><p id="status">Pending</p>');return}
    if(req.url.startsWith('/effect?note=')){effects++;res.end('Saved: '+new URL(req.url,'http://127.0.0.1').searchParams.get('note'));return}
    res.statusCode=404;res.end('not found')
  })
  await new Promise(r=>server.listen(0,'127.0.0.1',r))
  const fixture='http://127.0.0.1:'+server.address().port+'/index'
  const port=await availablePort()
  const exe=electron
  child=spawn(exe,[path.join(__dirname,'workstation-browser-bav1-cdp.child.cjs'),'--no-sandbox'],{
    cwd:path.resolve(__dirname,'..'),
    env:{...process.env,BAV_TEMP_ROOT:root,BAV_CDP_PORT:String(port),BAV_FIXTURE_URL:fixture},
    stdio:['ignore','pipe','pipe','ipc'],windowsHide:true
  })
  let stdout='',stderr=''
  child.stdout.on('data',b=>stdout+=String(b))
  child.stderr.on('data',b=>stderr+=String(b))
  child.on('exit',(code)=>{if(!stdout.includes('BAV_READY'))console.error('BAV_CHILD_EXIT',code,stderr.slice(-1600))})
  await deadline(new Promise((resolve,reject)=>{const check=()=>{if(stdout.includes('BAV_READY'))return resolve();if(child.exitCode!==null)return reject(new Error('Electron exited: '+stderr));setTimeout(check,150)};check()}),25000,'electron native WebContentsView')
  const ready=JSON.parse(stdout.split('BAV_READY ')[1].split('\n')[0])
  assert.equal(typeof ready.debugger,'boolean','native debugger attachment must be observable')
  browser=await deadline(chromium.connectOverCDP('http://127.0.0.1:'+port,{timeout:12000}),16000,'Playwright CDP')
  const pages=browser.contexts().flatMap(c=>c.pages())
  const page=pages.find(p=>p.url()===fixture)
  assert.ok(page,'Playwright must discover existing Hermes-owned tab; got '+pages.map(x=>x.url()).join('; '))
  await page.getByRole('textbox',{name:'Note'}).fill('BAV-01')
  await page.getByRole('button',{name:'Save'}).click()
  await page.getByText('Saved: BAV-01',{exact:true}).waitFor({timeout:5000})
  assert.equal(effects,1)
  console.log('BAV01_CDP_SPIKE_PASS '+JSON.stringify({webContentsId:ready.webContentsId,existingTab:true,effects,debuggerInitiallyAttached:ready.debugger,playwrightLocator:true}))
}
main().catch(e=>{console.error('BAV01_CDP_SPIKE_FAIL',String(e.stack||e));process.exitCode=1}).finally(async()=>{
  try{await browser?.close()}catch{}
  try{child?.send({type:'close'})}catch{}
  if(child){await Promise.race([new Promise(r=>child.once('exit',r)),new Promise(r=>setTimeout(r,1800))]);if(child.exitCode===null)child.kill()}
  try{server?.close()}catch{}
  try{fs.rmSync(root,{recursive:true,force:true,maxRetries:8,retryDelay:250})}catch{}
})
