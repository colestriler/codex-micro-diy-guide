(() => {
'use strict';
const $ = id => document.getElementById(id);
let viewerFinished=false;
window.addEventListener('message',event=>{if(event.source===window.parent&&event.origin===window.location.origin&&event.data?.type==='micro:ping')window.parent.postMessage({type:viewerFinished?'micro:ready':'micro:error'},window.location.origin);});
function tagged(object,partKey){object.traverse(m=>{if(m.isMesh)m.userData.partKey=partKey;});return object;}
const stages = [
 ['A map of every layer','The printed case, raised plate assembly and caps are separated here so you can see the stack. This is the custom wired design. The fit coupons are test pieces and do not go inside the finished device.',[['Printed component types','9'],['Mechanical switches','13'],['RGBW light boards','14']]],
 ['Prepare the shell','Install four M3 heat-set inserts into the corner posts and two from underneath for the round foot. Print and test the insert coupon first. Let the inserts cool before installing electronics.',[['01 · Clear PETG shell','1'],['M3 heat-set inserts','6']]],
 ['Seat the electronics','Mount the KB2040 between the rear guide rails, with USB facing the cable opening. Fit eight RGBW boards facing outward in the wall pockets. Insulate and secure the small support circuit in the front bay.',[['KB2040 controller','1'],['Perimeter RGBW boards','8'],['Support circuit / perfboard','1']]],
 ['Clip in the switches','Work on the plate separately from the case. Insert all 13 switches from the top. The wide microphone cap sits over TWO switches, so both of those positions must be populated.',[['02 · Switch plate','1'],['Normal MX switches','13']]],
 ['Fit the other controls','Mount the encoder from below and fasten its washer and nut above the plate. Seat the joystick in its printed cradle. Insert the touch cap from below with copper foil against its thin inner skin; add the three indicators.',[['04 · Joystick cradle + joystick','1'],['05 · Touch cap + copper disk','1'],['Encoder + nut / washer','1'],['3 mm indicator LEDs','3']]],
 ['Add the light cups','Put one RGBW board into each black baffle, with the LED facing upward. The animation moves each pre-seated pair into place. Attach the cups beneath the six agent switches; insulate pads and keep switch pins clear.',[['07 · Black light baffles','6'],['Agent RGBW boards','6']]],
 ['Wire and test while open','Wire the matrix, controls and light chain using the guide’s connection map. The colored curves show service slack only—not individual electrical connections. Bench-test every input and light with the plate still accessible.',[['Diodes and matrix wiring','13'],['Control + LED connections','See guide'],['Insulation and service slack','Required']]],
 ['Lower the plate assembly','Lower the completed plate, switches, light cups and controls together. Guide the wires into the free space. Keep them away from the posts and the LED cups; stop if the plate meets resistance.',[['Completed plate subassembly','1'],['Top ledge + corner supports','4']]],
 ['Fasten the plate','Use four M3 × 8 mm screws through the plate into the corner inserts. Tighten gently and evenly. The screws in this view are simplified shapes, not printable parts.',[['M3 × 8 top screws','4']]],
 ['Fit the caps and dial','Fit six translucent agent caps, five white single caps, and the white two-stem microphone cap. Press the dial onto its D shaft while leaving room to rotate and click. Add the printed legends after testing the fit.',[['08 · Single keycaps','11'],['09 · Two-stem wide cap','1'],['06 · Encoder knob','1']]],
 ['Attach the round foot','Tape optional steel washers into the foot pockets before fitting it. Secure the foot from underneath with two low-profile M3 × 8 screws, then add adhesive rubber. Use the Underside view to inspect those seats.',[['03 · Round foot','1'],['Optional steel washers','4'],['Low-profile M3 × 8 screws','2'],['Adhesive rubber pads','4 shown']]],
 ['Ready for the bench','Connect a USB data cable and run the guide’s acceptance checks. The colors shown here illustrate six task states; they are not a live connection. The included custom firmware still needs further work for native Codex behavior.',[['Clear caps reveal agent lights','6'],['Perimeter light windows','8'],['USB data connection','1']]],
];
const viewer=$('viewer'), labels=$('labels');
let renderer;
try { renderer=new THREE.WebGLRenderer({antialias:true,alpha:true}); }
catch(e){$('fallback').hidden=false;window.parent.postMessage({type:'micro:error'},window.location.origin);return;}
renderer.setPixelRatio(Math.min(window.devicePixelRatio,2));
renderer.setClearColor(0xf7f8f3,1);renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
viewer.prepend(renderer.domElement);renderer.domElement.setAttribute('role','img');renderer.domElement.setAttribute('aria-label','Rotatable CAD assembly of the DIY Micro. Key legends: agent 01 to 06; Fast, Approve, Decline, New Chat, Voice, and Send. Use the stage controls for a text description of every assembly step.');
const scene=new THREE.Scene(),camera=new THREE.OrthographicCamera(-150,150,150,-150,.1,2000);
camera.up.set(0,0,1);
scene.add(new THREE.AmbientLight(0xffffff,.9));
const key=new THREE.DirectionalLight(0xfffaf0,2);key.position.set(100,-130,220);scene.add(key);
const fill=new THREE.DirectionalLight(0xe8f3ff,.8);fill.position.set(-100,90,70);scene.add(fill);
const bottom=new THREE.DirectionalLight(0xffffff,1.0);bottom.position.set(40,-50,-130);scene.add(bottom);
const root=new THREE.Group(),topPack=new THREE.Group();scene.add(root);root.add(topPack);
const entries=[],byId=new Map(),allMeshes=[],materials=[];
const decode=(s,Type)=>{const raw=atob(s),a=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)a[i]=raw.charCodeAt(i);return new Type(a.buffer);};
const geo={};for(const [id,data] of Object.entries(CAD)){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(decode(data.vertices,Float32Array),3));g.setIndex(new THREE.BufferAttribute(decode(data.indices,Uint32Array),1));g.computeVertexNormals();g.computeBoundingBox();geo[id]=g;}
function mat(color,extra={}){const m=new THREE.MeshStandardMaterial({color,roughness:.65,metalness:0,...extra});materials.push(m);return m;}
function mesh(g,color,extra={}){return new THREE.Mesh(g,mat(color,extra));}
function box(w,d,h,x=0,y=0,z=0,color='#d2ded2'){const m=mesh(new THREE.BoxGeometry(w,d,h),color);m.position.set(x,y,z+h/2);return m;}
function cylinder(d,h,x=0,y=0,z=0,color='#b7c0b3',segments=32){const g=new THREE.CylinderGeometry(d/2,d/2,h,segments);g.rotateX(Math.PI/2);const m=mesh(g,color);m.position.set(x,y,z+h/2);return m;}
function ring(outer,inner,h,x,y,z,color){const s=new THREE.Shape();s.absarc(0,0,outer/2,0,Math.PI*2,false);const hole=new THREE.Path();hole.absarc(0,0,inner/2,0,Math.PI*2,true);s.holes.push(hole);const g=new THREE.ExtrudeGeometry(s,{depth:h,bevelEnabled:false,curveSegments:16});const m=mesh(g,color,{metalness:.65,roughness:.35});m.position.set(x,y,z);return m;}
function entry(id,name,obj,kind='printed',top=false,move=()=>[0,0,0]){(top?topPack:root).add(obj);obj.userData.id=id;obj.traverse(m=>{if(m.isMesh&&!m.userData.isLegend){m.userData.id=id;allMeshes.push(m);m.userData.baseColor=m.material.color.clone();}});const e={id,name,obj,kind,move,base:obj.position.clone()};entries.push(e);byId.set(id,e);return obj;}
function cad(id,number,name,color,top=false,move=()=>[0,0,0],pos=[0,0,0]){const m=mesh(geo[number],color);const g=new THREE.Group();g.position.set(...pos);g.add(m);const e=new THREE.LineSegments(new THREE.EdgesGeometry(geo[number],28),new THREE.LineBasicMaterial({color:0x526451,transparent:true,opacity:.18}));g.add(e);const outer=new THREE.Group();outer.add(g);return entry(id,name,outer,'printed',top,move);}
const smooth=x=>{x=Math.max(0,Math.min(1,x));return x*x*(3-2*x);};
const done=(t,n)=>smooth(t-(n-1));
const lift=(n,z)=>(t)=>[0,0,z*(1-done(t,n))];
const C=[-28.575,-9.525,9.525,28.575],R=[28.575,9.525,-9.525,-28.575];
const agents=[[C[1],R[0]],[C[2],R[0]],...C.map(x=>[x,R[1]])];
const shell=cad('case','01','01 · Clear PETG case','#d1ddd4');
cad('plate','02','02 · Switch plate','#f1f0e5',true);
const foot=cad('foot','03','03 · Round foot','#e4e6dc',false,lift(10,-45));
cad('cradle','04','04 · Joystick cradle','#2d3930',true,lift(4,46));
cad('touch','05','05 · Touch cap + copper electrode','#202b25',true,lift(4,-30));
const copper=cylinder(13,.15,C[0],R[3],24.1,'#b57448');tagged(copper,'copper');byId.get('touch').obj.add(copper);
cad('knob','06','06 · Encoder knob','#f4f1df',true,lift(9,85));
// All six cups use the same exported printable part; electronics are reference shapes.
const lightEmitters=[];
function ledBoard(){const g=new THREE.Group();g.add(box(9.1,9.1,1,0,0,0,'#2c6852'));g.add(box(5,5,1.3,0,0,1,'#eeeecc'));const die=box(3.8,3.8,.8,0,0,2.3,'#c4d9b7');die.material.emissive.set('#71b684');die.material.emissiveIntensity=.25;g.add(die);lightEmitters.push(die);tagged(g,'rgbw-led');return g;}
agents.forEach(([x,y],i)=>{
 const g=new THREE.Group();const b=mesh(geo['07'],'#26322b');g.add(b);const led=ledBoard();led.position.set(0,0,11.7);g.add(led);g.position.set(x,y,0);const wrap=new THREE.Group();wrap.add(g);
 entry('cup'+i,'07 · Agent light cup '+(i+1)+' + RGBW board',wrap,'printed + purchased',true,lift(5,-39));
});
// Thirteen real switch positions, including both switches under the wide cap.
for(let r=0;r<4;r++)for(let c=0;c<4;c++){
 if((r===0&&(c===0||c===3))||(r===3&&c===0))continue;
 const x=C[c],y=R[r],g=new THREE.Group();g.add(box(14,14,8.3,x,y,16.7,'#718878'));g.add(box(16,16,.5,x,y,24.5,'#adbaad'));g.add(box(12,12,4,x,y,25,'#b9c7b7'));g.add(box(4,1.2,4,x,y,29,'#8ba17d'));g.add(box(1.2,4,4,x,y,29,'#8ba17d'));
 entry('switch'+r+c,'MX switch · row '+(r+1)+', column '+(c+1)+(r===3&&c!==3?' · wide key':''),g,'purchased reference',true,lift(3,43));
 if(r===3&&(c===1||c===2))continue;
 const isAgent=agents.some(p=>p[0]===x&&p[1]===y);
 cad('cap'+r+c,'08',isAgent?'08 · Translucent agent keycap':'08 · White command keycap',isAgent?'#b6cbbc':'#f4f1e4',true,lift(9,92),[x,y,30.5]);
}
cad('wide','09','09 · Wide keycap · two MX sockets','#f4f1e4',true,lift(9,92),[0,R[3],30.5]);
// Decals follow each cap's shallow dish and move with the cap during assembly.
const decalRay=new THREE.Raycaster(),decalDirection=new THREE.Vector3(0,0,-1),capSurfaces={single:new THREE.Mesh(geo['08']),wide:new THREE.Mesh(geo['09'])};
for(const legend of KEY_LABELS){
 const canvas=document.createElement('canvas');canvas.width=legend.width===20?512:320;canvas.height=256;
 const ctx=canvas.getContext('2d');ctx.fillStyle='#202820';ctx.textAlign='center';ctx.textBaseline='middle';
 if(legend.icon){ctx.save();ctx.translate(canvas.width/2,76);ctx.scale(12,12);ctx.strokeStyle='#202820';ctx.lineWidth=.5;ctx.lineCap='round';ctx.lineJoin='round';ctx.stroke(new Path2D(legend.icon));ctx.restore();ctx.font='500 44px Arial';ctx.fillText(legend.label,canvas.width/2,174);}
 else{ctx.font='500 74px Arial';ctx.fillText(legend.label,canvas.width/2,128);}
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=renderer.capabilities.getMaxAnisotropy();
 const surface=new THREE.PlaneGeometry(legend.width,10,16,12),positions=surface.attributes.position;
 for(let i=0;i<positions.count;i++){decalRay.set(new THREE.Vector3(positions.getX(i),positions.getY(i),12),decalDirection);const hit=decalRay.intersectObject(legend.entry==='wide'?capSurfaces.wide:capSurfaces.single)[0];positions.setZ(i,(hit?hit.point.z:6)+.08);}
 surface.computeVertexNormals();
 const decal=new THREE.Mesh(surface,new THREE.MeshBasicMaterial({map:texture,transparent:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-1}));decal.userData.isLegend=true;decal.position.set(legend.x,legend.y,30.5);byId.get(legend.entry).obj.add(decal);
}
const encoder=new THREE.Group();encoder.add(box(12,12,11.5,C[0],R[0],10.5,'#59665e'));encoder.add(cylinder(7,6,C[0],R[0],22,'#a3aba2'));encoder.add(cylinder(6,9,C[0],R[0],28,'#b9bfb4'));
entry('encoder','Rotary encoder · panel mount and push switch',encoder,'purchased reference',true,lift(4,-29));
const nut=new THREE.Group();nut.add(ring(10.5,7,1.5,C[0],R[0],25.5,'#a1a89a'));nut.add(ring(11,7,.5,C[0],R[0],25,'#bec4b8'));
entry('nut','Encoder nut and washer',nut,'purchased reference',true,lift(4,58));
const joy=new THREE.Group();joy.add(box(19,19,5,30,30,25.6,'#6d796e'));joy.add(cylinder(14,4,30,30,30.6,'#222e27'));
entry('joystick','PSP slide joystick · simplified reference',joy,'purchased reference',true,lift(4,66));
const indicators=new THREE.Group();[-24.5,-29,-33.5].forEach(y=>{indicators.add(cylinder(3,3,-41,y,24,'#aac36b'));indicators.add(cylinder(.5,5,-41,y,19,'#aeb5a6'));});
entry('indicators','Three layer indicator LEDs',indicators,'purchased reference',true,lift(4,-29));
// Board, port and small support circuit occupy the guide's stated envelopes.
const board=new THREE.Group();board.add(box(17.8,35,1.6,0,31,4,'#225b42'));board.add(box(7,7,2.8,0,30,5.6,'#242e28'));board.add(box(9,7,3.3,0,45,5.6,'#a2aa9e'));
for(let y=17;y<44;y+=2.54)for(const x of [-7.8,7.8])board.add(cylinder(1.2,.2,x,y,5.6,'#c4a261',12));
entry('controller','KB2040 controller · USB toward rear',board,'purchased reference',false,t=>{const q=1-done(t,2);return[72*q,0,48*q+20*Math.sin(q*Math.PI)];});
const support=new THREE.Group();support.add(tagged(box(25,20,1.6,0,-35,4,'#897950'),'perfboard'));support.add(tagged(box(7,19,3,0,-35,5.6,'#283129'),'level-shifter'));support.add(tagged(cylinder(5,5,8,-30,5.6,'#556555'),'passives'));
entry('support','Support circuit · level shifter + passives',support,'purchased reference',false,t=>[75*(1-done(t,2)),-20*(1-done(t,2)),25*(1-done(t,2))]);
let pi=0;for(const sign of [-1,1])for(const t of [-22,22])for(const axis of ['x','y']){
 const led=ledBoard();if(axis==='x'){led.rotation.y=sign*Math.PI/2;led.position.set(sign*50.8,t,9);}else{led.rotation.x=-sign*Math.PI/2;led.position.set(t,sign*50.8,9);}const g=new THREE.Group();g.add(led);const index=pi++;
 entry('perimeter'+index,'Perimeter RGBW board '+(index+1)+' · faces outward',g,'purchased reference',false,p=>{const q=1-done(p,2);return[axis==='x'?sign*23*q:0,axis==='y'?sign*23*q:0,34*q];});
}
// Heat-set inserts, screws, optional washers and adhesive feet.
let ni=0;for(const x of [-43,43])for(const y of [-43,43]){
 const i=ni++;entry('insert'+i,'M3 heat-set insert · top corner',ring(4.2,3,4,x,y,17.7,'#b6944f'),'purchased reference',false,lift(1,35));
 const g=new THREE.Group();g.add(cylinder(3,8,x,y,17,'#737b70'));g.add(ring(5.5,2.4,2.5,x,y,25,'#38443a'));entry('screw'+i,'M3 × 8 mm plate screw',g,'purchased reference',true,lift(8,118));
}
for(const x of [-25,25]){entry('bottominsert'+x,'M3 heat-set insert · underside',ring(4.2,3,4,x,0,0,'#b6944f'),'purchased reference',false,lift(1,-35));const g=new THREE.Group();g.add(cylinder(3,8,x,0,-3.2,'#818778'));g.add(cylinder(6,1.6,x,0,-4.8,'#626e60'));entry('footscrew'+x,'Low-profile M3 × 8 mm foot screw',g,'purchased reference',false,t=>[0,0,-45*(1-done(t,10))-13*(1-done(t,10))]);}
for(const x of [-20,20])for(const y of [-20,20]){const w=ring(24,8.4,2,x,y,-2.2,'#9caa99');foot.add(tagged(w,'washer'));}
for(const [x,y] of [[0,34],[0,-34],[34,0],[-34,0]]){const r=cylinder(9,1.2,x,y,-6.2,'#26352b');foot.add(tagged(r,'rubber'));}
const cable=new THREE.Group();cable.add(box(8,8,2.8,0,51,6,'#a6afa1'));cable.add(box(10,12,6,0,61,4.5,'#e4e6d8'));const cg=new THREE.CylinderGeometry(2,2,28,20);const cm=mesh(cg,'#d9dfd0');cm.position.set(0,81,7.5);cable.add(cm);entry('usb','USB data cable · simplified reference',cable,'purchased reference',false,t=>[0,38*(1-done(t,11)),0]);
// Two illustrative service loops; exact connections live in the wiring diagram.
allMeshes.length=0;for(const e of entries){if(!MODEL_PARTS[e.id])throw new Error('Missing catalog mapping: '+e.id);e.obj.traverse(m=>{if(m.isMesh&&!m.userData.isLegend){m.userData.partKey=m.userData.partKey||MODEL_PARTS[e.id];m.userData.id=e.id;m.userData.baseColor=m.material.color.clone();allMeshes.push(m);}});}
const loom=new THREE.Group();root.add(loom);let oldWireOffset=-1;
function wirePaths(offset){if(Math.abs(offset-oldWireOffset)<.3)return;oldWireOffset=offset;while(loom.children.length){const c=loom.children.pop();c.geometry.dispose();c.material.dispose();}for(const [i,color] of ['#ad7c43','#567b8a'].entries()){const pts=[[i*4,20,6],[23+i*4,14,8],[30+i*4,-7,12+offset*.5],[20+i*4,9,18+offset]].map(v=>new THREE.Vector3(...v));const curve=new THREE.CatmullRomCurve3(pts);const m=new THREE.Mesh(new THREE.TubeGeometry(curve,28,.55,6,false),new THREE.MeshStandardMaterial({color,roughness:.8}));loom.add(m);}}
let progress=11,displayStage=-1,playing=false,animation=null,holdUntil=0,lastTime=0;
let theta=.78,elevation=.48,zoom=1,span=95,target=new THREE.Vector3(0,15,18),selectedId=null;
let annotationNodes=[];
const stageFocus=[['wide','cup2','case','foot'],['insert0','bottominsert-25'],['controller','perimeter1','support'],['switch31','plate'],['joystick','encoder','touch'],['cup2'],[],['plate'],['screw0'],['wide','knob'],['foot','footscrew-25'],['usb']];
const shortNames={wide:'Wide cap · 2 stems',cup0:'RGBW board + cup',cup2:'Black light baffle',case:'Printed shell',foot:'Round foot',insert0:'M3 heat-set insert','bottominsert-25':'Insert from below',controller:'KB2040 · USB rear',perimeter1:'Perimeter light',support:'Support circuit',switch31:'Two switches for wide cap',plate:'Switch plate',joystick:'Slide joystick',encoder:'Encoder from below',touch:'Touch electrode',screw0:'M3 × 8 screw',knob:'D-shaft knob','footscrew-25':'Low-profile screw',usb:'USB data cable'};
function stageText(n){if(n===displayStage)return;displayStage=n;const s=stages[n];$('step-counter').textContent=(n===0?'OVERVIEW':'STAGE')+' · '+String(n).padStart(2,'0')+' / 11';$('step-title').textContent=s[0];$('step-desc').textContent=s[1];$('part-list').replaceChildren(...s[2].map(([label,count])=>{const li=document.createElement('li');li.textContent=label;const b=document.createElement('span');b.textContent=count;li.append(b);return li;}));$('step-jump').value=n;$('view-state').textContent=n===0?'Exploded overview':n===11?'Assembled prototype':'Assembly stage '+String(n).padStart(2,'0');labels.replaceChildren();annotationNodes=stageFocus[n].map(id=>{const el=document.createElement('div');el.className='annotation';el.textContent=shortNames[id]||byId.get(id).name;labels.append(el);return{id,el};});$('prev').disabled=n===0&&!animation;$('next').disabled=n===11&&!animation;}
stages.forEach((s,i)=>{const o=document.createElement('option');o.value=i;o.textContent=String(i).padStart(2,'0')+' · '+s[0];$('step-jump').append(o);});
function paintParts(t){topPack.position.z=70*(1-done(t,7));for(const e of entries){const d=e.move(t);e.obj.position.set(e.base.x+d[0],e.base.y+d[1],e.base.z+d[2]);}cable.visible=t>10;loom.visible=t>=5.98;wirePaths(topPack.position.z);const colorStates=['#e8eedf','#649dff','#76d794','#ffc264','#ec7479','#bac9b8'];agents.forEach(([x,y],i)=>{const id='cap'+(i<2?'0'+(i+1):'1'+(i-2));const obj=byId.get(id).obj;obj.traverse(m=>{if(m.isMesh&&!m.userData.isLegend){m.material.color.copy(m.userData.baseColor);if(t>10.6)m.material.color.lerp(new THREE.Color(colorStates[i]),.8);m.material.emissive.set(t>10.6?colorStates[i]:'#000000');m.material.emissiveIntensity=t>10.6?(i===5?.02:.22):0;}});});lightEmitters.forEach(m=>m.material.emissiveIntensity=t>10.6?.65:.15);[shell,foot].forEach(part=>part.traverse(m=>{if(m.isMesh&&!m.userData.isLegend){m.material.transparent=$('xray').checked;m.material.opacity=$('xray').checked?.2:1;m.material.depthWrite=!$('xray').checked;}}));if(selectedId){byId.get(selectedId).obj.traverse(m=>{if(m.isMesh&&!m.userData.isLegend){m.material.emissive.set('#93bb63');m.material.emissiveIntensity=.26;}});}}
function stop(){playing=false;holdUntil=0;$('play').textContent=progress>=10.99?'Replay assembly':'Play assembly';}
function go(n){stop();n=Math.max(0,Math.min(11,n));const duration=matchMedia('(prefers-reduced-motion: reduce)').matches?0:1100;animation={from:progress,to:n,start:performance.now(),duration};stageText(n);}
$('play').addEventListener('click',()=>{if(playing){stop();animation=null;return;}playing=true;$('play').textContent='Pause';if(progress>=10.99){progress=0;animation=null;stageText(0);}holdUntil=performance.now()+300;});
$('prev').addEventListener('click',()=>go(Math.max(0,Math.ceil(progress-.05)-1)));
$('next').addEventListener('click',()=>go(Math.min(11,Math.floor(progress+.05)+1)));
$('step-jump').addEventListener('change',e=>go(Number(e.target.value)));
$('progress').addEventListener('input',e=>{stop();animation=null;progress=Number(e.target.value);stageText(Math.round(progress));});
$('explode').addEventListener('click',()=>go(0));
$('assembled').addEventListener('click',()=>go(11));
window.addEventListener('message',event=>{if(event.origin!==window.location.origin||event.source!==window.parent||event.data?.type!=='micro:highlight')return;const found=allMeshes.find(m=>m.userData.partKey===event.data.partId);clearSelection();if(found)selectedId=found.userData.id;});
$('xray').addEventListener('change',()=>paintParts(progress));
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-view]').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));theta=.78;elevation=b.dataset.view==='top'?1.565:b.dataset.view==='bottom'?-.48:.48;zoom=1;}));
// Pointer orbit and pinch zoom. Click selection uses the visible mesh raycast.
const pointers=new Map();let moved=0,pinch=0;
renderer.domElement.addEventListener('pointerdown',e=>{pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});moved=0;renderer.domElement.setPointerCapture(e.pointerId);if(pointers.size===2){const a=[...pointers.values()];pinch=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);}});
renderer.domElement.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId))return;const old=pointers.get(e.pointerId),dx=e.clientX-old.x,dy=e.clientY-old.y;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});moved+=Math.abs(dx)+Math.abs(dy);if(pointers.size===2){const a=[...pointers.values()],d=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);zoom=Math.max(.55,Math.min(3,zoom*d/Math.max(1,pinch)));pinch=d;}else{theta-=dx*.006;elevation=Math.max(-1.5,Math.min(1.565,elevation+dy*.005));}document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed','false'));});
const raycaster=new THREE.Raycaster();
function clearSelection(){if(selectedId)byId.get(selectedId).obj.traverse(m=>{if(m.isMesh&&!m.userData.isLegend){m.material.emissive.set('#000000');m.material.emissiveIntensity=0;}});selectedId=null;}
renderer.domElement.addEventListener('pointerup',e=>{if(moved<5&&pointers.size===1){const r=renderer.domElement.getBoundingClientRect();raycaster.setFromCamera(new THREE.Vector2((e.clientX-r.left)/r.width*2-1,-(e.clientY-r.top)/r.height*2+1),camera);const hits=raycaster.intersectObjects(allMeshes).filter(h=>{if($('xray').checked&&['case','foot'].includes(h.object.userData.partKey))return false;let o=h.object;while(o){if(!o.visible)return false;o=o.parent;}return true;});clearSelection();if(hits.length){selectedId=hits[0].object.userData.id;const p=byId.get(selectedId);$('selected').textContent=p.name+' · '+p.kind;window.parent.postMessage({type:'micro:select',partId:hits[0].object.userData.partKey},window.location.origin);}else $('selected').textContent='Select any visible part to identify it.';}pointers.delete(e.pointerId);});
renderer.domElement.addEventListener('pointercancel',e=>pointers.delete(e.pointerId));
renderer.domElement.addEventListener('wheel',e=>{e.preventDefault();zoom=Math.max(.55,Math.min(3,zoom*Math.exp(-e.deltaY*.001)));},{passive:false});
let width=1,height=1;new ResizeObserver(()=>{width=viewer.clientWidth;height=viewer.clientHeight;renderer.setSize(width,height,false);}).observe(viewer);
const bounds=new THREE.Box3(),temp=new THREE.Box3(),v=new THREE.Vector3();
function frameCamera(){bounds.makeEmpty();for(const e of entries)if(e.obj.visible)bounds.union(temp.setFromObject(e.obj));const center=bounds.getCenter(new THREE.Vector3());target.lerp(center,.12);const direction=new THREE.Vector3(Math.sin(theta)*Math.cos(elevation),-Math.cos(theta)*Math.cos(elevation),Math.sin(elevation));camera.position.copy(target).addScaledVector(direction,500);camera.lookAt(target);camera.updateMatrixWorld();const right=new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,0),up=new THREE.Vector3().setFromMatrixColumn(camera.matrixWorld,1);let maxX=0,maxY=0;for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){v.set(x,y,z).sub(center);maxX=Math.max(maxX,Math.abs(v.dot(right)));maxY=Math.max(maxY,Math.abs(v.dot(up)));}const aspect=width/height,wanted=Math.max(45,maxY*1.23,maxX/aspect*1.22);span+=(wanted-span)*.12;camera.left=-span*aspect/zoom;camera.right=span*aspect/zoom;camera.top=span/zoom;camera.bottom=-span/zoom;camera.updateProjectionMatrix();}
function positionLabels(){for(const {id,el} of annotationNodes){const e=byId.get(id);temp.setFromObject(e.obj).getCenter(v);v.project(camera);const x=(v.x*.5+.5)*width,y=(-v.y*.5+.5)*height;el.hidden=x<0||x>width||y<80||y>height-40||zoom>1.6;const labelWidth=el.offsetWidth||120;el.style.left=Math.min(width-labelWidth-18,Math.max(4,x))+'px';el.style.top=y+'px';}}
let lastVisual='',settleFrames=45;
function tick(now){const dt=now-lastTime;lastTime=now;
 if(playing&&!animation&&now>=holdUntil){if(progress>=10.99)stop();else{const next=Math.min(11,Math.floor(progress+.03)+1);animation={from:progress,to:next,start:now,duration:1400/Number($('speed').value)};stageText(next);}}
 if(animation){const f=animation.duration===0?1:Math.min(1,(now-animation.start)/animation.duration);progress=animation.from+(animation.to-animation.from)*smooth(f);if(f>=1){progress=animation.to;animation=null;holdUntil=now+2700/Number($('speed').value);$('prev').disabled=progress===0;$('next').disabled=progress===11;if(!playing)$('play').textContent=progress>=10.99?'Replay assembly':'Play assembly';}}
 $('progress').value=progress;const visual=[progress,theta,elevation,zoom,width,height,$('xray').checked,selectedId].join('|');if(visual!==lastVisual){lastVisual=visual;settleFrames=40;}if(settleFrames>0){paintParts(progress);root.updateMatrixWorld(true);frameCamera();positionLabels();renderer.render(scene,camera);settleFrames--;}requestAnimationFrame(tick);
}
stageText(11);paintParts(11);viewerFinished=true;requestAnimationFrame(tick);window.parent.postMessage({type:'micro:ready'},window.location.origin);
})();
