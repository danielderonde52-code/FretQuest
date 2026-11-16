"""FretQuest rooktest. Gebruik:  python3 dev/test.py   (vereist: pip install playwright, en een Chromium)
Laadt index.html in een headless browser en controleert theorie, oefeningen, uitleg, telefoonopmaak en rondleiding.
Eindigt met 'ALLES GOED' of een lijst fouten (exitcode 1)."""
import asyncio, os, sys
from playwright.async_api import async_playwright
URL = 'file://' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'index.html')
fails = []
def check(name, ok, info=''):
    print(('ok   ' if ok else 'FOUT ') + name + (' ' + str(info) if info and not ok else ''))
    if not ok: fails.append(name)

THEORY = """()=>{const h=__hk,bad=[];let n=0;
  const LC={all:1,pos:5,nps:7,set:4,str:6};
  for(const fid of Object.keys(h.F))for(let root=0;root<12;root++)for(const t of Object.keys(LC)){
    if(t==='nps'&&h.F[fid].iv.length!==7)continue;
    for(let i=0;i<LC[t];i++){let L;try{L=h.getLens(fid,root,{t,i});}catch(e){bad.push('exception '+fid+root+t+i+': '+e.message);continue;}
      n++;if(!L.notes.length&&t!=='set')bad.push('leeg '+fid+' '+root+' '+t+i);
      for(const x of L.notes){const iv=((h.OPEN[x.s]+x.f-root)%12+12)%12;
        if(iv!==x.iv||!h.F[fid].iv.includes(iv))bad.push('verkeerde noot '+fid+root+t+i);if(x.f<0)bad.push('fret<0 '+fid+root+t+i);}}}
  return{n,bad:bad.slice(0,8)};}"""
DRILLS = """()=>{const h=__hk,bad=[];let n=0;
  const mats=['pow','chr','maj','min','dim','aug','maj7','dom7','m7','m7b5','pmin','pmaj','blues','ion','dor','phr','lyd','mix','aeo','loc','hmin','phd'];
  for(const d of Object.keys(h.DR)){if(h.DR[d].jam)continue;
    for(const fid of (h.DR[d].free?['maj']:mats))for(const t of (h.DR[d].nolens||h.DR[d].free?['all']:h.DR[d].fixlens?['pos']:['all','pos','set','str','nps'])){
      if(t==='set'&&h.F[fid].iv.length!==3)continue;if(t==='nps'&&h.F[fid].iv.length!==7)continue;
      Object.assign(h.run,{drill:d,fid,lens:{t,i:0},rk:true,rp:true,hint:true,ear:h.DR[d].ear?{root:3,last:null}:null,key:d});
      for(let k=0;k<6;k++){let q;try{q=h.DR[d].make();}catch(e){bad.push(d+' '+fid+' '+t+': '+e.message);break;}n++;
        if(q.type==='choice'&&q.choices.filter(c=>c.ok).length!==1)bad.push(d+' '+fid+' niet precies een goed antwoord');
        if(q.type==='tap'&&!q.targets.length)bad.push(d+' '+fid+' '+t+' geen doelen');
        if(q.type==='play'&&!q.seq.length)bad.push(d+' '+fid+' '+t+' lege reeks');}}}
  h.run.ear=null;return{n,bad:bad.slice(0,8)};}"""
LESSONS = """()=>{const h=__hk,bad=[];let n=0;
  if(h.LESSONS.length!==h.STAGES.length)bad.push('aantal lessen != aantal stappen');
  h.LESSONS.forEach((L,i)=>L.forEach((x,j)=>{let bs;try{bs=x.b();}catch(e){bad.push('les '+i+'.'+j+': '+e.message);return;}
    bs.forEach(b=>{n++;for(const d of b.dots)if(d.f<0||d.f>22||d.s<0||d.s>5)bad.push('stip buiten hals '+i+'.'+j);});}));
  for(const st of h.STAGES)for(const p of st.dr){if(!h.DR[p[0]])bad.push('onbekende oefening '+p[0]);if(p[1]&&!h.F[p[1]])bad.push('onbekend materiaal '+p[1]);if(!h.HOW[p[0]])bad.push('geen denkstap '+p[0]);}
  return{n,bad:bad.slice(0,8)};}"""
ANSWER = """async()=>{const r=__hk.run,q=r.q;await new Promise(z=>setTimeout(z,470));
  if(q.type==='choice')document.querySelectorAll('#prChoices .choice')[q.choices.findIndex(c=>c.ok)].click();
  else if(q.type==='tap')for(const t of q.targets)document.querySelector(`#prBoard .tap[data-s='${t.s}'][data-f='${t.f}']`).dispatchEvent(new MouseEvent('click',{bubbles:true}));
  else{r.muteUntil=0;for(const t of q.seq.slice())__hk.heard(t.midi,t.s,t.f);}
  await new Promise(z=>setTimeout(z,40));
  const fit=e=>{const b=e.getBoundingClientRect();return e.hidden||b.width===0||(b.left>=-1&&b.top>=-1&&b.right<=innerWidth+1&&b.bottom<=innerHeight+1);};
  const ok=['prNext','prStop','prChoices','prBoard','prBig'].every(id=>fit(document.getElementById(id)));
  document.getElementById('prNext').click();return ok;}"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        # 1. inhoud
        pg = await b.new_page(viewport={'width': 1200, 'height': 800}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(400)
        for name, js in [('theorie: elke noot in elke lens klopt', THEORY), ('oefeningen: elke vraag is geldig', DRILLS), ('uitleg en leerpad', LESSONS)]:
            r = await pg.evaluate(js); check(f'{name} ({r["n"]} gevallen)', not r['bad'], r['bad'])
        await pg.close()
        # 2. rondleiding past op elk formaat en start maar één keer
        for w, h in [(800, 360), (740, 300), (390, 780), (320, 560), (1100, 800)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}); pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(URL); await pg.wait_for_timeout(300); bad = []
            if not await pg.is_visible('#tourCard'): bad.append('start niet')
            else:
                while await pg.is_visible('#tourCard'):
                    await pg.wait_for_timeout(300)
                    ok = await pg.evaluate("""()=>{const c=tourCard.getBoundingClientRect(),h=tourHole.getBoundingClientRect();let ok=c.left>=0&&c.right<=innerWidth&&c.top>=0&&c.bottom<=innerHeight&&(tourHole.className==='none'||h.bottom<=c.top);
                      tourCard.querySelectorAll('h3,p,button').forEach(e=>{if(e.hidden)return;const q=e.getBoundingClientRect();if(q.left<c.left-.5||q.right>c.right+.5||q.bottom>c.bottom+.5)ok=false;});return ok;}""")
                    if not ok: bad.append(await pg.inner_text('#tourH'))
                    await pg.click('#tourNext')
                await pg.reload(); await pg.wait_for_timeout(300)
                if await pg.is_visible('#tourCard'): bad.append('start opnieuw na afronden')
            check(f'rondleiding {w}x{h}', not bad, bad); await ctx.close()
        # 3. een ronde van elke oefening op een liggende telefoon: alles blijft in beeld, ronde eindigt met een score
        ctx = await b.new_context(viewport={'width': 800, 'height': 360}); pg = await ctx.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL); await pg.wait_for_timeout(300); await pg.click('#tourSkip')
        drills = await pg.evaluate("()=>Object.keys(__hk.DR).filter(d=>!__hk.DR[d].jam)")
        for d in drills:
            await pg.evaluate(f"()=>{{const h=__hk;h.ui.drill='{d}';h.cfg.fid=h.DR['{d}'].ear?'pmin':'aeo';h.cfg.lens={{t:'pos',i:0}};h.ui.auto=false;h.ui.reps={{'{d}':5}};document.getElementById('t-oef').click();}}")
            await pg.click('#prStart'); fit = True
            for _ in range(5): fit = (await pg.evaluate(ANSWER)) and fit
            score = await pg.inner_text('#dScore') if await pg.is_visible('#prDone') else '(niet afgerond)'
            check(f'ronde {d}: {score}', fit and score == '5 / 5', 'buiten beeld' if not fit else score)
        await ctx.close()
        check('geen JavaScript-fouten', not errs, errs[:3]); await b.close()
    print('\nALLES GOED' if not fails else f'\n{len(fails)} FOUT(EN): ' + '; '.join(fails)); sys.exit(1 if fails else 0)
asyncio.run(main())
