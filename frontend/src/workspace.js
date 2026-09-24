const $=id=>document.getElementById(id);
const API='http://127.0.0.1:8000', key='neural.chat.v3';
let history=[],busy=false,paused=matchMedia('(prefers-reduced-motion: reduce)').matches,state='idle',health=null;
try{history=JSON.parse(localStorage.getItem(key)||'[]').filter(m=>['user','bot','error'].includes(m.role)&&typeof m.text==='string').slice(-100)}catch{}
function save(){try{localStorage.setItem(key,JSON.stringify(history))}catch{}}
function render(){ $('messages').replaceChildren();
 if(!history.length){const w=document.createElement('div');w.className='welcome';w.innerHTML='<div class="symbol">✳</div><h3>Uma pergunta abre caminhos.</h3><p>Escreva uma ideia, explore um assunto ou peça ajuda para organizar seu próximo passo.</p><div class="suggestions"></div>';for(const text of ['Explique como funciona uma rede neural.','Ajude-me a organizar meu dia.']){const b=document.createElement('button');b.textContent=text;b.onclick=()=>{$('prompt').value=text;$('prompt').focus()};w.querySelector('.suggestions').append(b)}$('messages').append(w)}
 for(const m of history){const a=document.createElement('article');a.className='message '+m.role;const label=document.createElement('b'),p=document.createElement('p');label.textContent=m.role==='user'?'VOCÊ':m.role==='bot'?'QWEN LOCAL':'ERRO';p.textContent=m.text;a.append(label,p);if(m.role==='bot'){const b=document.createElement('button');b.className='copy';b.textContent='Copiar resposta';b.onclick=async()=>{try{await navigator.clipboard.writeText(m.text);b.textContent='Copiado'}catch{b.textContent='Selecione o texto para copiar'}};a.append(b)}$('messages').append(a)}
 $('count').textContent=history.length;$('messages').scrollTop=$('messages').scrollHeight;
}
function phase(next){if(next==='thinking')executionTopic=selectedTopic;if(next==='success'||next==='error')releaseSignal(next);state=next;document.body.dataset.state=next;$('phase').textContent=({idle:'EM REPOUSO',thinking:'PROCESSANDO NO QWEN',success:'RESPOSTA RECEBIDA',error:'FALHA NA RESPOSTA'})[next]}
async function send(e){e.preventDefault();const text=$('prompt').value.trim();if(!text||busy)return;busy=true;$('send').disabled=true;$('clear').disabled=true;$('thinking').hidden=false;$('prompt').value='';history.push({role:'user',text});render();save();phase('thinking');const start=performance.now();try{const r=await fetch(API+'/orchestrate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({request:selectedTopic ? 'Tema selecionado: '+selectedTopic.name+'\nPergunta: '+text : text,execution_mode:'local'}),signal:AbortSignal.timeout(190000)});const data=await r.json();if(!r.ok)throw Error(typeof data.detail==='string'?data.detail:'Falha na API ('+r.status+')');const answer=data.answer||data.final_response;if(typeof answer!=='string'||!answer.trim())throw Error('A API retornou uma resposta vazia.');history.push({role:'bot',text:answer});$('latency').textContent=((performance.now()-start)/1000).toFixed(1)+' s';phase('success');$('detail').textContent='Resposta recebida do modelo local. Você pode ler e copiar o texto na conversa.'}catch(err){history.push({role:'error',text:err.name==='TimeoutError'?'O tempo de espera terminou. A API pode continuar processando.':err.message||'Falha ao conectar à API local.'});phase('error')}finally{busy=false;$('send').disabled=false;$('clear').disabled=false;$('thinking').hidden=true;save();render();$('prompt').focus()}}
$('form').onsubmit=send;$('prompt').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();$('form').requestSubmit()}};
$('clear').onclick=()=>{if(busy)return;history=[];save();render();phase('idle');$('prompt').focus()};
async function check(){try{const r=await fetch(API+'/health',{signal:AbortSignal.timeout(10000)});if(!r.ok)throw Error();health=await r.json();$('connection').textContent=health.ollama==='ok'?'● Ollama conectado':'○ Ollama indisponível';$('model').textContent=health.local_model?.name||'Não informado';$('agents').replaceChildren();for(const [name,status] of Object.entries(health.agents||{})){const row=document.createElement('div');row.className='agent-row';const a=document.createElement('span'),b=document.createElement('span');a.textContent=name;b.textContent=status;row.append(a,b);$('agents').append(row)}}catch{$('connection').textContent='○ API desconectada';$('model').textContent='Indisponível';$('agents').textContent='Não foi possível consultar os agentes.'}}
$('refresh').onclick=check;check();setInterval(()=>{if(!document.hidden)check()},30000);
for(const b of document.querySelectorAll('[data-node]'))b.onclick=()=>{const n=b.dataset.node;$('detail-title').textContent=({qwen:'QWEN / NÚCLEO LOCAL',input:'ENTRADA / SUA PERGUNTA',output:'SAÍDA / RESPOSTA DO MODELO',history:'HISTÓRICO / NESTE NAVEGADOR'})[n];$('detail').textContent=({qwen:'O núcleo envia sua pergunta ao Ollama e aguarda a resposta. Nenhum agente externo é acionado.',input:'Digite sua pergunta no campo da conversa e pressione Enter para enviar.',output:history.filter(m=>m.role==='bot').at(-1)?.text||'A próxima resposta será apresentada na conversa.',history:history.length+' mensagens armazenadas neste navegador. Nova conversa limpa este histórico.'})[n];if(n==='input')$('prompt').focus();if(n==='output'||n==='history')$('messages').scrollTop=$('messages').scrollHeight};
$('motion').onclick=()=>{paused=!paused;motionLabel()};function motionLabel(){$('motion').textContent=paused?'Retomar animação':'Pausar animação';$('motion').setAttribute('aria-pressed',String(paused))}motionLabel();
const canvas=$('network'),ctx=canvas.getContext('2d');let w=0,h=0,time=0,last=0;
const nodes=Array.from({length:80},(_,i)=>{const a=i*2.39996,r=Math.sqrt((i+1)/80);return{x:.5+Math.cos(a)*r*.40,y:.46+Math.sin(a)*r*.39,z:i%5}});
new ResizeObserver(()=>{w=canvas.clientWidth;h=canvas.clientHeight;const d=Math.min(devicePixelRatio||1,1.5);canvas.width=w*d;canvas.height=h*d;ctx?.setTransform(d,0,0,d,0,0)}).observe(canvas);
function frame(now){requestAnimationFrame(frame);if(!ctx||document.hidden||now-last<33)return;const dt=Math.min(now-last,50);last=now;if(!paused)time+=dt;ctx.clearRect(0,0,w,h);const active=state==='thinking',rgb=state==='error'?'243,156,170':active?'237,209,151':'129,224,203';const pts=nodes.map((n,i)=>({x:n.x*w+Math.sin(time*.0003+i)*8,y:n.y*h+Math.cos(time*.0004+i)*8}));
pts.forEach((p,i)=>{for(let j=i+1;j<pts.length;j++){const q=pts[j],d=Math.hypot(p.x-q.x,p.y-q.y);if(d>70)continue;ctx.strokeStyle='rgba('+rgb+','+(1-d/85)*.24+')';ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.quadraticCurveTo((p.x+q.x)/2+8,(p.y+q.y)/2-8,q.x,q.y);ctx.stroke()}ctx.fillStyle='rgba('+rgb+',.65)';ctx.beginPath();ctx.arc(p.x,p.y,1.3+nodes[i].z*.35,0,Math.PI*2);ctx.fill()});
drawSynapses(rgb,dt);}


const topics=[
 ['Medicina','MED',.5,.10],
 ['Obstetrícia e Ginecologia','GO',.77,.18],
 ['Pediatria','PED',.86,.40],
 ['Impressão 3D','3D',.83,.64],
 ['Mestrado em Saúde e Tecnologia','MSC',.65,.82],
 ['IA','IA',.35,.82],
 ['Desenvolvimento de dispositivos e aplicativos','DEV',.17,.64],
 ['HardWork Medicina','HW',.14,.40],
 ['INEP, Revalida e Enamed','INEP',.23,.18]
].map(([name,code,x,y])=>({name,code,x,y}));
let selectedTopic=null;
document.querySelectorAll('.node:not(.core)').forEach(n=>n.remove());
const topicBadge=document.createElement('p');topicBadge.className='topic-badge';topicBadge.textContent='Conversa geral · selecione um tema na rede';
$('form').prepend(topicBadge);
function selectTopic(topic){
 selectedTopic=topic;
 fireTopic(topic);
 for(const b of document.querySelectorAll('.topic-node'))b.setAttribute('aria-pressed',String(b.dataset.topic===topic?.name));
 topicBadge.textContent=topic?'Tema: '+topic.name:'Conversa geral · selecione um tema na rede';
 $('detail-title').textContent=topic?topic.name.toUpperCase():'QWEN / NÚCLEO LOCAL';
 $('detail').textContent=topic?'As próximas perguntas serão enviadas ao Qwen com o contexto de '+topic.name+'. Este nó organiza a conversa; não adiciona uma base de documentos ou um modelo especializado.':'Todos os temas se conectam ao Qwen local. Selecione uma área para orientar sua próxima pergunta.';
 $('prompt').placeholder=topic?'Pergunte sobre '+topic.name+'…':'O que você quer explorar?';
}
for(const topic of topics){const b=document.createElement('button');b.className='node topic-node';b.dataset.topic=topic.name;b.style.left=topic.x*100+'%';b.style.top=topic.y*100+'%';b.setAttribute('aria-pressed','false');b.setAttribute('aria-label',topic.name);b.textContent=topic.code;const label=document.createElement('span');label.textContent=topic.name;b.append(label);b.onclick=()=>selectTopic(topic);document.querySelector('.nodes').append(b)}
document.querySelector('.core').onclick=()=>selectTopic(null);


let executionTopic=null,hoverTopic=null,signals=[],rings=[],nextSignal=0,sequence=0;
const corePoint={x:.5,y:.45};
function emit(from,to,color='129,224,203',delay=0){
 if(paused||signals.length>=45)return;
 signals.push({from,to,color,start:time+delay,duration:1000+Math.hypot(from.x-to.x,from.y-to.y)*900});
}
function fireTopic(topic){
 const p=topic||corePoint;rings.push({p,start:time,color:'164,241,220'});
 if(topic){emit(topic,corePoint);const i=topics.indexOf(topic);emit(topic,topics[(i+1)%topics.length],'137,182,246',180);emit(topic,topics[(i+8)%topics.length],'137,182,246',320)}
 else topics.forEach((t,i)=>emit(corePoint,t,'164,241,220',i*70));
}
function releaseSignal(result){
 const color=result==='error'?'243,156,170':'145,242,179';
 (executionTopic?[executionTopic]:topics).forEach((t,i)=>emit(corePoint,t,color,i*60));
}
for(const t of topics){
 const b=[...document.querySelectorAll('.topic-node')].find(el=>el.dataset.topic===t.name);
 b.addEventListener('pointerenter',()=>{hoverTopic=t;emit(t,corePoint,'164,215,255')});
 b.addEventListener('pointerleave',()=>{hoverTopic=null});
 b.addEventListener('focus',()=>{hoverTopic=t});
 b.addEventListener('blur',()=>{hoverTopic=null});
}
function curve(a,b){
 const ax=a.x*w,ay=a.y*h,bx=b.x*w,by=b.y*h;
 const bend=.12;
 return {ax,ay,bx,by,cx:(ax+bx)/2-(by-ay)*bend,cy:(ay+by)/2+(bx-ax)*bend};
}
function at(c,t){return{x:(1-t)*(1-t)*c.ax+2*(1-t)*t*c.cx+t*t*c.bx,y:(1-t)*(1-t)*c.ay+2*(1-t)*t*c.cy+t*t*c.by}}
function drawSynapses(rgb){
 if(!paused&&time>=nextSignal){
  const source=state==='thinking'?(executionTopic||topics[sequence%9]):topics[sequence%9];
  emit(source,state==='thinking'?corePoint:topics[(sequence+1)%9],state==='thinking'?'237,209,151':'129,224,203');
  if(state!=='thinking'&&sequence%2===0)emit(corePoint,source);
  sequence++;nextSignal=time+(state==='thinking'?420:1100);
 }
 const edges=topics.flatMap((t,i)=>[[t,corePoint],[t,topics[(i+1)%topics.length]]]);
 for(const [a,b] of edges){
  const lit=a===hoverTopic||b===hoverTopic||a===selectedTopic;
  const c=curve(a,b);ctx.lineWidth=lit?1.5:.8;ctx.strokeStyle='rgba('+rgb+','+(lit?.6:.18)+')';
  ctx.beginPath();ctx.moveTo(c.ax,c.ay);ctx.quadraticCurveTo(c.cx,c.cy,c.bx,c.by);ctx.stroke();
 }
 signals=signals.filter(s=>{
  const f=(time-s.start)/s.duration;if(f<0)return true;
  if(f>=1){rings.push({p:s.to,start:time,color:s.color});return false}
  const c=curve(s.from,s.to);
  for(let k=10;k>=0;k--){const q=at(c,Math.max(0,f-k*.012));ctx.fillStyle='rgba('+s.color+','+(.85*(1-k/11))+')';ctx.beginPath();ctx.arc(q.x,q.y,k===0?3.4:1.7,0,Math.PI*2);ctx.fill()}
  const q=at(c,f);ctx.shadowBlur=16;ctx.shadowColor='rgb('+s.color+')';ctx.fillStyle='#efffff';ctx.beginPath();ctx.arc(q.x,q.y,1.7,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;return true;
 });
 rings=rings.filter(r=>{
  const f=(time-r.start)/950;if(f>=1)return false;
  ctx.strokeStyle='rgba('+r.color+','+(.65*(1-f))+')';ctx.lineWidth=1.6;ctx.beginPath();ctx.arc(r.p.x*w,r.p.y*h,(r.p===corePoint?39:24)+f*25,0,Math.PI*2);ctx.stroke();return true;
 }).slice(-36);
 ctx.lineWidth=1;
}

render();phase('idle');requestAnimationFrame(frame);
