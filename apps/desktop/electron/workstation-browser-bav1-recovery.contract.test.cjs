'use strict'
const {test}=require('node:test')
const assert=require('node:assert/strict')
const {spawnSync}=require('node:child_process')
const path=require('node:path')

test('native WebContentsView restart fencing reconciles uncertain click without duplicate',()=>{
 const result=spawnSync(process.execPath,[path.join(__dirname,'workstation-browser-bav1-controller.runner.cjs')],{
  cwd:path.resolve(__dirname,'..'),
  env:{...process.env,BAV_RECOVERY_TEST:'1'},
  encoding:'utf8',timeout:125000,maxBuffer:1024*1024
 })
 assert.equal(result.status,0, 'fixture failed: '+result.stderr+'\n'+result.stdout)
 assert.match(result.stdout,/BAV04_BROWSER_CRASH_RECONCILED_PASS/)
 assert.match(result.stdout,/"crashCode":37/)
 assert.match(result.stdout,/"effects":2/)
 assert.match(result.stdout,/"modelCalls":0/)
})
