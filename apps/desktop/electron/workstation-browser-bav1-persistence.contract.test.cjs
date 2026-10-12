'use strict'
// BAV-05 experimental contract: persistent canonical ProceduralMemory replay, no product changes.
const {test}=require('node:test')
const assert=require('node:assert/strict')
const {spawnSync}=require('node:child_process')
const path=require('node:path')

test('promoted test-only procedure survives fresh Python workers and uses the Hermes browser owner',()=>{
 const result=spawnSync(process.execPath,[path.join(__dirname,'workstation-browser-bav1-controller.runner.cjs')],{
  cwd:path.resolve(__dirname,'..'),
  env:{...process.env,BAV_PERSISTENCE_TEST:'1'},
  encoding:'utf8',timeout:125000,maxBuffer:1024*1024
 })
 assert.equal(result.status,0, 'fixture failed: '+result.stderr+'\n'+result.stdout)
 assert.match(result.stdout,/BAV05_PERSISTENT_RUN_MATCHING_PASS/)
 assert.match(result.stdout,/"memoryReloads":2/)
 assert.match(result.stdout,/"modelCalls":0/)
 assert.match(result.stdout,/"effects":3/)
})
