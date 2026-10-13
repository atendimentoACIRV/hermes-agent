'use strict'
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { spawn } = require('node:child_process')
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'hermes-concurrent-admission-'))
function run(participant) {
  return new Promise((resolve,reject) => {
    const child=spawn(process.execPath,[path.join(__dirname, 'workstation-browser-admission-concurrency.child.cjs'), root, participant],{
      cwd:path.resolve(__dirname,'..'),windowsHide:true,env:{...process.env, HERMES_WORKSTATION_HOME:path.join(root,'isolated')}
    })
    let out='',err=''
    child.stdout.on('data',b=>out+=b.toString())
    child.stderr.on('data',b=>err+=b.toString())
    child.on('error',reject)
    child.on('exit',(code,signal)=>{
      if(err)process.stderr.write(err)
      if(code!==0)return reject(new Error('child '+participant+' exit '+code+' signal '+signal+' '+out))
      const found=out.match(/CRASH_03_RESULT (\{[^\r\n]+\})/)
      if(!found)return reject(new Error('no child result '+participant+' '+out))
      resolve(JSON.parse(found[1]))
    })
  })
}
async function main(){
  try{
    const a=run('A'),b=run('B')
    const start=Date.now()
    while(!fs.existsSync(path.join(root,'ready-A'))&&!fs.existsSync(path.join(root,'ready-B'))){
      assert.ok(Date.now()-start<12000,'no writer reached admission')
      await new Promise(resolve=>setTimeout(resolve,25))
    }
    // Let the other process race for the same operation ID, then release.
    await new Promise(resolve=>setTimeout(resolve,350))
    fs.writeFileSync(path.join(root,'go'),'proceed')
    const results=await Promise.all([a,b])
    const admitted=results.filter(x=>x.result==='admitted')
    assert.equal(admitted.length,1,'CRASH-03: no two independent processes may BOTH admit the same operation')
    assert.equal(results.filter(x=>x.result!=='admitted').length,1)
    const persisted=JSON.parse(fs.readFileSync(path.join(root,'browser-session.json'),'utf8'))
    assert.ok(persisted.operationAdmissions['op-concurrent'])
    process.stdout.write('CRASH_03_CONCURRENT_PASS '+JSON.stringify(results)+'\n')
  } finally {
    fs.rmSync(root,{recursive:true,force:true,maxRetries:10,retryDelay:100})
  }
}
main().catch(e=>{process.stderr.write('CRASH_03_CONCURRENT_FAIL '+String(e.stack||e)+'\n');process.exitCode=1})
