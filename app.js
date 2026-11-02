(() => {
  'use strict';
  const steps=window.GUIDE_STEPS;
  if(!Array.isArray(steps)||!steps.length)return;
  const $=id=>document.getElementById(id);
  const KEY='omar-zid.nxt-university.v1';
  const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const today=()=>{const d=new Date();return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-')};
  function fresh(){return {version:1,day:today(),startTime:'09:00',checks:{},readiness:{},done:{},notes:{},answers:{},updatedAt:null};}
  function validate(value){
    if(!value||value.version!==1||typeof value!=='object')throw Error('This is not a progress file from this guide.');
    const clean=fresh();
    if(/^\d{4}-\d{2}-\d{2}$/.test(value.day||''))clean.day=value.day;
    if(/^([01]\d|2[0-3]):[0-5]\d$/.test(value.startTime||''))clean.startTime=value.startTime;
    const ids=steps.flatMap(s=>s.checks.map(c=>c.id));
    for(const id of ids)clean.checks[id]=value.checks?.[id]===true;
    for(const item of steps.flatMap(s=>s.readinessItems||[]))clean.readiness[item.id]=value.readiness?.[item.id]===true;
    for(const step of steps){
      clean.notes[step.id]=typeof value.notes?.[step.id]==='string'?value.notes[step.id].slice(0,30000):'';
      for(let i=0;i<step.explainPrompts.length;i++){const id=step.id+':'+i;clean.answers[id]=typeof value.answers?.[id]==='string'?value.answers[id].slice(0,20000):'';}
      if(value.done?.[step.id]&&step.checks.every(c=>clean.checks[c.id]))clean.done[step.id]=String(value.done[step.id]).slice(0,50);
    }
    clean.updatedAt=typeof value.updatedAt==='string'?value.updatedAt:null;
    return clean;
  }
  let state=fresh(),storageOK=true;
  try{const saved=localStorage.getItem(KEY);if(saved)state=validate(JSON.parse(saved));}catch{storageOK=false;}
  let current=Math.max(0,steps.findIndex(s=>s.id===location.hash.slice(1)));
  if(location.protocol==='file:')document.querySelectorAll('a[href^="downloads/"]').forEach(link=>{const note=document.createElement('p');note.className='subtle';note.textContent='You are using the offline copy. Keep this whole folder together.';link.replaceWith(note)});
  let toastTimer;
  const toast=message=>{$('toast').textContent=message;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,5500)};
  function save(){
    state.updatedAt=new Date().toISOString();
    try{localStorage.setItem(KEY,JSON.stringify(state));storageOK=true;}catch{storageOK=false;}
    $('save-status').textContent=storageOK?'Saved in this browser · download a copy before leaving.':'This browser cannot save notes. Download your notes to keep them.';
  }
  function clock(minutes){const next=((minutes%1440)+1440)%1440;return String(Math.floor(next/60)).padStart(2,'0')+':'+String(next%60).padStart(2,'0')}
  function timings(){const [h,m]=state.startTime.split(':').map(Number);let cursor=h*60+m;return steps.map(s=>{const from=cursor;cursor+=s.minutes;const value={from:clock(from),to:clock(cursor),nextDay:cursor>=1440};if(s.breakAfter){value.breakFrom=clock(cursor);cursor+=s.breakAfter.minutes;value.breakTo=clock(cursor);value.breakNextDay=cursor>=1440}return value})}
  function updateProgress(){
    const count=steps.filter(s=>!!state.done[s.id]).length;
    $('step-count').textContent=count+' of '+steps.length+' steps done';$('percent').textContent=Math.round(count/steps.length*100)+'%';$('progress').value=count;
    const schedule=timings();
    $('steps-nav').innerHTML=steps.map((s,i)=>`<button class="step-nav${i===current?' active':''}${state.done[s.id]?' done':''}" type="button" data-step="${i}"${i===current?' aria-current="step"':''}><span class="number" aria-hidden="true">${state.done[s.id]?'✓':i+1}</span><span><span class="label">${esc(s.title.replace(/^\d+\.\s*/,''))}</span><span class="duration">${schedule[i].from}–${schedule[i].to}${schedule[i].nextDay?' (next day)':''} · ${s.minutes} min</span></span></button>`).join('');
    const total=steps.reduce((n,s)=>n+s.minutes+(s.breakAfter?.minutes||0),0);
    const end=Number(state.startTime.slice(0,2))*60+Number(state.startTime.slice(3))+total;
    $('day-duration').textContent='6 hours of work + 70 minutes of breaks · finishes about '+clock(end)+(end>=1440?' (next day)':'');
    $('steps-nav').querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>render(Number(button.dataset.step),true)));
    $('time-block').textContent=schedule[current].from+'–'+schedule[current].to+(schedule[current].nextDay?' (next day)':'')+' · '+steps[current].minutes+' min suggested';
    updateReadiness();
  }
  function updateReadiness(){
    const last=steps[steps.length-1],items=last.readinessItems||[];
    const marked=items.filter(c=>state.readiness[c.id]).length;
    const stepsDone=steps.filter(s=>!!state.done[s.id]).length;
    const ready=marked===items.length&&stepsDone===steps.length;
    $('readiness-result').textContent=ready?'Your checklist is complete for showing the computer demonstration.':marked+' of '+items.length+' readiness checks marked · '+stepsDone+' of '+steps.length+' study steps completed.';
  }
  function checkMarkup(check,kind){const checked=(kind==='readiness'?state.readiness:state.checks)[check.id]===true;return `<div class="check-row"><input type="checkbox" id="${kind}-${check.id}" data-check="${check.id}" data-kind="${kind}"${checked?' checked':''}><label for="${kind}-${check.id}">${esc(check.label)}<span class="expected"><strong>Look for:</strong> ${esc(check.expected)}</span></label></div>`}
  function render(index,focus=false){
    current=Math.max(0,Math.min(steps.length-1,index));const s=steps[current];
    $('study-date').value=state.day;$('start-time').value=state.startTime;
    $('step-position').textContent='STEP '+(current+1)+' OF '+steps.length;
    $('step-title').textContent=s.title.replace(/^\d+\.\s*/,'');$('step-goal').textContent=s.goal;
    $('actions-list').innerHTML=s.actions.map(a=>'<li>'+esc(a)+'</li>').join('');
    $('step-links').innerHTML=s.links.map(l=>`<a href="${esc(l.href)}" target="_blank" rel="noopener">${esc(l.label)} <span aria-hidden="true">↗</span></a>`).join('');
    $('step-checks').innerHTML=s.checks.map(c=>checkMarkup(c,'check')).join('');
    $('explain-fields').innerHTML=s.explainPrompts.map((prompt,i)=>{const key=s.id+':'+i;return `<label class="answer-field"><span>${esc(prompt)}</span><textarea rows="2" data-answer="${esc(key)}" placeholder="My explanation…">${esc(state.answers[key]||'')}</textarea></label>`}).join('');
    $('explain-example').hidden=!s.exampleExplanation;$('explain-example').open=false;$('example-text').textContent=s.exampleExplanation||'';
    $('note-prompts').innerHTML=s.notePrompts.map(p=>'<li>'+esc(p)+'</li>').join('');
    $('step-notes').value=state.notes[s.id]||'';
    $('readiness').hidden=!s.readinessItems;
    $('readiness-checks').innerHTML=(s.readinessItems||[]).map(c=>checkMarkup(c,'readiness')).join('');
    $('readiness-note').textContent=s.statusNote||'';
    const time=timings()[current];$('break-note').hidden=!s.breakAfter;
    $('break-note').innerHTML=s.breakAfter?`<strong>${time.breakFrom}–${time.breakTo} · ${s.breakAfter.minutes}-minute break</strong>${esc(s.breakAfter.label)}. Save your notes, then continue with the next step.`:'';
    $('previous').disabled=current===0;$('finish-hint').textContent='';
    $('finish-step').textContent=current===steps.length-1?'Finish my day ✓':'Finish this step →';
    $('save-status').textContent=storageOK?'Your notes stay in this browser. Download a copy to keep them.':'This browser cannot save notes. Download your notes to keep them.';
    document.querySelectorAll('[data-check]').forEach(input=>input.addEventListener('change',()=>{
      const store=input.dataset.kind==='readiness'?state.readiness:state.checks;
      store[input.dataset.check]=input.checked;
      if(!input.checked&&input.dataset.kind==='check')delete state.done[s.id];
      save();updateProgress();
    }));
    document.querySelectorAll('[data-answer]').forEach(input=>input.addEventListener('input',()=>{state.answers[input.dataset.answer]=input.value;save()}));
    history.replaceState(null,'','#'+s.id);updateProgress();
    if(focus){$('step-title').focus({preventScroll:true});window.scrollTo(0,0);document.querySelector('.step-nav.active')?.scrollIntoView({block:'nearest',inline:'nearest'})}
  }
  $('step-notes').addEventListener('input',event=>{state.notes[steps[current].id]=event.target.value;save()});
  $('previous').addEventListener('click',()=>render(current-1,true));
  $('finish-step').addEventListener('click',()=>{
    const s=steps[current],missing=s.checks.filter(c=>!state.checks[c.id]);
    if(missing.length){$('finish-hint').textContent='Check the '+missing.length+' item'+(missing.length===1?'':'s')+' above first.';document.getElementById('check-'+missing[0].id).focus();return}
    state.done[s.id]=new Date().toISOString();save();updateProgress();
    if(current<steps.length-1){const pause=s.breakAfter?`Take your ${s.breakAfter.minutes}-minute break before starting this step.`:'Step saved. Continue when you are ready.';render(current+1,true);toast(pause)}
    else{toast('Day saved. Check the readiness list and download your notes before leaving.');$('readiness').scrollIntoView({block:'start'})}
  });
  $('study-date').addEventListener('change',event=>{if(event.target.value)state.day=event.target.value;save()});
  $('start-time').addEventListener('change',event=>{if(/^([01]\d|2[0-3]):[0-5]\d$/.test(event.target.value)){state.startTime=event.target.value;save();updateProgress();const s=steps[current],t=timings()[current];if(s.breakAfter)$('break-note').innerHTML=`<strong>${t.breakFrom}–${t.breakTo} · ${s.breakAfter.minutes}-minute break</strong>${esc(s.breakAfter.label)}. Save your notes, then continue with the next step.`}});
  function download(name,content,type){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),5000)}
  function readableNotes(){
    const schedule=timings(),lines=['OMAR ZID - ROBOTICS STUDY NOTES','Study date: '+state.day,'Start: '+state.startTime,'Saved: '+new Date().toISOString(),'','These are my study notes and self-confirmed checks. Robot results in the supplied reports are simulated.',''];
    for(let n=0;n<steps.length;n++){const s=steps[n];lines.push(s.title.toUpperCase(),schedule[n].from+'-'+schedule[n].to+' | '+(state.done[s.id]?'STEP COMPLETED':'STEP NOT COMPLETED'),s.goal,'','Checks:');for(const c of s.checks)lines.push('['+(state.checks[c.id]?'x':' ')+'] '+c.label,'Expected: '+c.expected);lines.push('','My explanations:');s.explainPrompts.forEach((p,i)=>lines.push(p,state.answers[s.id+':'+i]||'(Not recorded)'));lines.push('','My observations, problems and next actions:',state.notes[s.id]||'(Not recorded)','');if(s.readinessItems){lines.push('READINESS CHECKLIST');for(const c of s.readinessItems)lines.push('['+(state.readiness[c.id]?'x':' ')+'] '+c.label);lines.push('',s.statusNote,'')}}
    return lines.join('\r\n');
  }
  function exportNotes(){save();download('Omar_Zid_robotics_notes_'+state.day+'.txt',readableNotes(),'text/plain;charset=utf-8');toast('Notes downloaded. Open the file to check it before leaving.');}
  ['export-top','export-step','export-bottom'].forEach(id=>$(id).addEventListener('click',exportNotes));
  $('backup').addEventListener('click',()=>{save();download('Omar_Zid_robotics_progress_'+state.day+'.json',JSON.stringify(state,null,2),'application/json');toast('Progress file downloaded. Load it on the next computer to continue.');});
  $('restore').addEventListener('change',async event=>{
    const file=event.target.files?.[0];if(!file)return;
    try{if(file.size>3000000)throw Error('This file is too large. Choose a progress file from this guide.');const imported=validate(JSON.parse(await file.text()));state=imported;save();render(current);toast('Your saved progress and notes are loaded.');}catch(error){toast('Could not load this file. '+(error.message||'Choose a progress JSON file.'));}finally{event.target.value=''}
  });
  $('clear').addEventListener('click',()=>$('clear-dialog').showModal());
  $('clear-dialog').addEventListener('close',()=>{if($('clear-dialog').returnValue==='clear'){try{localStorage.removeItem(KEY)}catch{}state=fresh();render(0,true);toast('The notes on this browser were cleared. Exported files were not changed.')}});
  $('health-check').addEventListener('click',async()=>{
    const button=$('health-check'),output=$('health-result');output.hidden=false;
    if(!/^https?:$/.test(location.protocol)){output.textContent='You are using the downloaded copy. Open the demo, PDF and four project links below to check the files. The online link check is available on the public website.';return}
    const files=['kit/Start_Here.html','kit/Omar_Zid_Complete_Robotics.pdf','downloads/Omar_Zid_University_Kit.zip',...new Set(steps.flatMap(s=>s.links.map(l=>l.href.split('#')[0])))];
    const unique=[...new Set(files)];button.disabled=true;output.textContent='Checking the reports, demonstration and download…';
    const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);
    try{const results=await Promise.all(unique.map(async url=>{try{const response=await fetch(url,{method:'HEAD',cache:'no-store',signal:controller.signal});return {url,ok:response.ok}}catch{return {url,ok:false}}}));const failed=results.filter(r=>!r.ok);output.textContent=failed.length?'Some files did not open: '+failed.map(r=>r.url).join(', ')+'. Check your connection, or use the downloaded kit.':`All ${unique.length} file links opened on this computer. Next, play the four projects and record what you see.`;}finally{clearTimeout(timeout);button.disabled=false}
  });
  window.addEventListener('hashchange',()=>{const i=steps.findIndex(s=>s.id===location.hash.slice(1));if(i>=0&&i!==current)render(i,true)});
  render(current);
})();
