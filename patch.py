import re, sys

SRC = '/home/claude/work/index.orig.html'
DST = '/home/claude/work/index.html'
h = open(SRC, encoding='utf-8').read()


def rep(old, new, count=1):
    global h
    n = h.count(old)
    assert n == count, f'ditemukan {n}x (harus {count}x): {old[:90]!r}'
    h = h.replace(old, new)



# ---------------------------------------------------------------- 0. BUG: elemen .rv.l/.r/.z tetap bergeser setelah muncul
# aturan ".rv.l{translate:-64px 0}" ditulis sesudah ".rv.on{translate:none}" dengan spesifisitas sama, jadi menang terus.
rep(".js:not(.rm) .rv.z{scale:.9;translate:0 28px}",
    ".js:not(.rm) .rv.z{scale:.9;translate:0 28px}\n"
    ".js:not(.rm) .rv.l.on,.js:not(.rm) .rv.r.on,.js:not(.rm) .rv.z.on{translate:none;scale:none}")


# BUG desktop: kartu fakta di hero tergeser keluar layar. Pemusatan memakai "translate:-50% 0", lalu ditimpa oleh animasi
# ".hr{translate:none}" sehingga kartu mulai dari tengah layar dan terpotong di kanan. Dipusatkan tanpa translate.
rep(".hero-facts{position:absolute;left:50%;bottom:clamp(18px,4vh,44px);translate:-50% 0;width:var(--w);",
    ".hero-facts{position:absolute;left:0;right:0;margin-inline:auto;bottom:clamp(18px,4vh,44px);width:var(--w);")

# ---------------------------------------------------------------- 1. path gambar
rep("--a-plant:url('img/Area Workshop/MSB_Plant.JPEG'),url('img/Area Workshop/MSB_Plant.jpeg');",
    "--a-plant:url('img/Area Workshop/MSB_Plant.jpeg');")
rep("--foto-layanan-5:url('img/Inspection/UT.png');",
    "--foto-layanan-5:url('img/Inspection/UT/UT Inspection (17).jpeg');")
rep("--foto-qc:url('img/Inspection/UT.png');",
    "--foto-qc:url('img/Inspection/UT/UT Inspection (17).jpeg');")

# ---------------------------------------------------------------- 2. foto bagian Mutu (sesuai tiga jenis uji)
a = h.index('<div class="qph')
b = h.index('<span>Komponen</span></div></div>') + len('<span>Komponen</span></div></div>')
qph = ('<div class="qph rv l" style="--d:.38s">'
       '<div class="ph" style="--foto:url(\'img/Inspection/UT/UT Inspection (18).jpeg\')" data-label=""><span>Uji ultrasonik (UT)</span></div>'
       '<div class="ph" style="--foto:url(\'img/Inspection/Welding/Welding (3).jpeg\')" data-label=""><span>Inspeksi las</span></div>'
       '<div class="ph" style="--foto:url(\'img/Inspection/Painting Inpection/Painting (1).jpeg\')" data-label=""><span>Ketebalan cat</span></div></div>')
h = h[:a] + qph + h[b:]

# ---------------------------------------------------------------- 3. foto di panel peta
rep('<div class="peta-info"><h3>Lokasi workshop</h3>',
    '<div class="peta-info"><div class="peta-foto ph" style="--foto:url(\'img/Workshop_Area.png\')" data-label="" role="img" aria-label="Kompleks workshop PT Murinda Sentra Baja, tampak udara"></div><h3>Lokasi workshop</h3>')

# ---------------------------------------------------------------- 4. muat foto secara bertahap (hemat data di ponsel)
# slide hero: hanya foto pertama dimuat di awal
a = h.index('<div class="cf f1 ss">')
b = h.index('<div class="cf f2 ph"')
h = h[:a] + h[a:b].replace('class="ph vis"', 'class="ph"') + h[b:]
# slide "Tentang kami"
a = h.index('<div class="abv ss wipe"')
b = h.index('<div class="route glass"')
h = h[:a] + h[a:b].replace('class="ph vis"', 'class="ph"') + h[b:]
# foto klien: dimuat saat mendekati layar
a = h.index('<div class="cph rv">')
b = h.index('</div>', h.index('Dump truck</figcaption>')) + len('</div>')
h = h[:a] + h[a:b].replace('class="ph vis"', 'class="ph"') + h[b:]

# ---------------------------------------------------------------- 5. galeri: foto baru, filter Inspeksi, halaman bertahap
G0 = h.index('<div class="gal" id="gal">\n') + len('<div class="gal" id="gal">\n')
G1 = h.index('  </div>\n</div></section>', G0)
lines = [l for l in h[G0:G1].split('\n') if l.strip()]
groups = {'area': [], 'mesin': [], 'produk': [], 'inspeksi': []}
for l in lines:
    g = re.search(r'data-g="(\w+)"', l).group(1)
    groups[g].append(l)
assert [len(groups[k]) for k in ('area', 'mesin', 'produk')] == [5, 10, 7], {k: len(v) for k, v in groups.items()}


def fig(g, url, cap, cls='', fit=False):
    phc = 'ph fit' if fit else 'ph'
    c = ('gt ' + cls).strip()
    return (f'    <figure class="{c}" tabindex="0" role="button" data-g="{g}" aria-label="{cap}">'
            f'<div class="{phc}" style="--foto:url(\'{url}\')" data-label="{cap}"></div>'
            f'<figcaption>{cap}</figcaption><span class="zm"><svg viewBox="0 0 24 24"><use href="#i-plus"/></svg></span></figure>')


FM = 'img/Fasilitas Mesin/Fasilitas dan Mesin (%d).jpeg'
groups['area'] += [
    fig('area', 'img/Workshop_Area.png', 'Kompleks workshop dan area sekitar, tampak udara', 'wide'),
    fig('area', 'img/MSB_Plant.jpg', 'Bangunan plant dan area penyimpanan material, tampak udara'),
    fig('area', 'img/Main_Office.jpg', 'Gedung kantor Murinda'),
]
fm = [
    ('Mesin perakitan profil H-beam dengan rol konveyor', False),
    ('Mesin las SAW untuk profil H-beam', False),
    ('Mesin potong CNC gantri di area pemotongan plat', False),
    ('Mesin potong CNC gantri bersama operator', False),
    ('Mesin potong plat multi-torch', False),
    ('Panel kontrol dan gulungan kawat las SAW', False),
    ('Mesin roll forming', True),
    ('Lini mesin roll forming', False),
    ('Mesin roll forming, tampak dari ujung lini', True),
    ('Mesin potong plat multi-torch di area pemotongan', False),
]
groups['mesin'] += [fig('mesin', FM % (i + 1), c, fit=f) for i, (c, f) in enumerate(fm)]
CW = 'img/Product/Counterweight/Counterweight (%d).jpeg'
DL = 'img/Proses Fabrikasi/Counterweight/Delivery/Delivery (%d).jpeg'
# sisipkan sebelum "Vessel dump truck" (lebar) agar kelompok produk tetap rapi
vessel = groups['produk'].pop()
groups['produk'] += [
    fig('produk', CW % 3, 'Counterweight excavator, tampak miring'),
    fig('produk', CW % 4, 'Counterweight excavator dengan titik angkat'),
    fig('produk', 'img/Product/Counterweight/Counterweight.jpeg', 'Counterweight excavator berjajar di dalam hall workshop'),
    fig('produk', DL % 1, 'Pengiriman counterweight dengan trailer flatbed'),
    fig('produk', DL % 2, 'Counterweight dimuat di trailer flatbed, tampak belakang'),
    fig('produk', DL % 3, 'Pengiriman counterweight dengan trailer lowbed'),
    vessel,
]
UT = 'img/Inspection/UT/UT Inspection (%d).jpeg'
groups['inspeksi'] = [
    fig('inspeksi', UT % 17, 'Pengujian ultrasonik (UT) pada sambungan las'),
    fig('inspeksi', UT % 18, 'Pengujian ultrasonik (UT), inspektur dan perangkat uji'),
    fig('inspeksi', UT % 19, 'Inspeksi UT pada area sambungan'),
    fig('inspeksi', UT % 20, 'Pembacaan hasil uji ultrasonik (UT)'),
    fig('inspeksi', 'img/Inspection/MPI/MPI (1).jpeg', 'Magnetic Particle Inspection (MPI) pada sambungan las', fit=True),
    fig('inspeksi', 'img/Inspection/MPI/MPI (2).jpeg', 'Pemeriksaan MPI pada permukaan las', fit=True),
    fig('inspeksi', 'img/Inspection/Penetran/PT.jpeg', 'Penetrant Test (PT) pada sambungan las', fit=True),
    fig('inspeksi', 'img/Inspection/Penetran/PT (2).jpeg', 'Penetrant Test (PT), area sambungan las'),
    fig('inspeksi', 'img/Inspection/Painting Inpection/Painting (1).jpeg', 'Pengukuran ketebalan cat dengan coating thickness gauge', fit=True),
    fig('inspeksi', 'img/Inspection/Painting Inpection/Painting (5).jpeg', 'Verifikasi ketebalan cat (DFT)', fit=True),
    fig('inspeksi', 'img/Inspection/Welding/Welding (3).jpeg', 'Pemeriksaan dimensi las dengan weld gauge'),
    fig('inspeksi', 'img/Inspection/Welding/Welding (4).jpeg', 'Pengukuran sambungan las dengan weld gauge'),
    fig('inspeksi', 'img/Inspection/Welding/Welding (5).jpeg', 'Pemeriksaan tinggi las dengan weld gauge'),
    fig('inspeksi', 'img/Inspection/Welding/Welding (1).jpeg', 'Pemeriksaan las dengan weld gauge pada komponen', fit=True),
    fig('inspeksi', 'img/Inspection/Welding/Welding (6).jpeg', 'Pengukuran las dengan weld gauge, tampak dekat'),
    fig('inspeksi', UT % 9, 'Inspektur mengoperasikan perangkat uji ultrasonik pada plat'),
]
new_gal = '\n'.join(groups['area'] + groups['mesin'] + groups['produk'] + groups['inspeksi']) + '\n'
more = ('  <div class="more" id="galmore" hidden><button class="btn" id="galbtn" type="button">'
        '<svg viewBox="0 0 24 24"><use href="#i-plus"/></svg><span>Tampilkan lebih banyak (<span id="galleft">0</span>)</span></button></div>\n')
h = h[:G0] + new_gal + h[G1:]
G1b = h.index('  </div>\n</div></section>', G0) + len('  </div>\n')
h = h[:G1b] + more + h[G1b:]

rep('data-f="produk">Produk</button>',
    'data-f="produk">Produk</button><button type="button" aria-pressed="false" data-f="inspeksi">Inspeksi</button>')

# ---------------------------------------------------------------- 6. JS
# 6a. hanya foto non-slide yang diamati; slide dimuat satu per satu
rep("$$('.ph').forEach(e=>pio.observe(e));", "$$('.ph').filter(e=>!e.closest('.ss')).forEach(e=>pio.observe(e));")
rep("$$('.ss').forEach(el=>{const ps=$$('.ph',el);if(ps.length<2||RM)return;let i=0;setInterval(()=>{ps[i].classList.remove('on');i=(i+1)%ps.length;ps[i].classList.add('on')},4500)});",
    "$$('.ss').forEach(el=>{const ps=$$('.ph',el);if(ps.length<2||RM)return;let i=0;const ld=n=>ps[n%ps.length].classList.add('vis');addEventListener('load',()=>ld(1));setInterval(()=>{ps[i].classList.remove('on');i=(i+1)%ps.length;ps[i].classList.add('on');ld(i+1)},4500)});")

# 6b. PF: path foto alur produksi (P, B, I, D) tanpa path cadangan yang 404
a = h.index('const PF=u=>{')
b = h.index('\n', a)
h = h[:a] + ("const PF=u=>{const m=u.match(/^([PBID]):(.*)$/);if(!m)return `var(--${u})`;"
             "const d={P:'img/Proses Fabrikasi/Counterweight/',B:'img/Product/Built-Up/',I:'img/Inspection/',D:'img/Proses Fabrikasi/Counterweight/Delivery/'}[m[1]];"
             "return `url('${d}${m[2]}')`};") + h[b:]

# 6c. tahap "Pemeriksaan akhir": foto inspeksi dan pengiriman
rep("'Pemeriksaan akhir sebelum pengiriman.',['a-rak']]]},",
    "'Pemeriksaan akhir sebelum pengiriman.',['I:UT/UT Inspection (18).jpeg','I:Welding/Welding (3).jpeg','I:Painting Inpection/Painting (5).jpeg','D:Delivery (3).jpeg']]]},")

# 6d. foto alur produksi dimuat saat dekat; langkah bisa diketuk di ponsel tanpa meloncat
rep('<div class="ph vis${k?\'\':\' on\'}" style="--foto:${PF(u)}"', '<div class="ph${k?\'\':\' on\'}" style="--foto:${PF(u)}"')
rep("let cyt,pci=0;", "let cyt,pci=0,pnear=false;")
rep("const goStep=i=>scrollTo(", "const goStep=i=>innerWidth<=900?setStep(i):scrollTo(")
m = re.search(r"if\(k!==pcur\)\{pcur=k;.*?cyc\(\)\}", h)
assert m
h = h[:m.start()] + ("const k2=innerWidth>900?k:(pcur<0?0:pcur);"
                     "if(innerWidth<=900)$('.pr',pc).style.setProperty('--pp',((k2+1)/steps.length).toFixed(3));"
                     "if(k2!==pcur)setStep(k2);") + h[m.end():]
rep("function upd(){tk=0;",
    "const pld=k=>{if(!pnear)return;[k,k+1].forEach(i=>shots[i]&&$$('.ph',shots[i]).forEach(p=>p.classList.add('vis')))};\n"
    "function setStep(k){pcur=k;steps.forEach((s,i)=>s.classList.toggle('act',i===k));shots.forEach((s,i)=>s.classList.toggle('act',i===k));"
    "$('#pbig').textContent=k+1;$('#ptitle').textContent=tx('h3',steps[k]);$('#pdesc').textContent=steps[k].dataset.cap||'';pld(k);cyc()}\n"
    "new IntersectionObserver(es=>{if(es.some(e=>e.isIntersecting)){pnear=true;pld(Math.max(pcur,0))}},{rootMargin:'1400px 0px'}).observe(pc);\n"
    "function upd(){tk=0;")

# 6e. galeri
a = h.index('/* galeri: filter dan pratinjau */')
b = h.index('/* formulir: membuka aplikasi email')
gal_js = r"""/* galeri: filter, halaman bertahap, dan pratinjau */
const lb=$('#lb'),figs=$$('.gt'),more=$('#galmore'),gl=$('#galleft'),FG=v=>figs.find(f=>$('.ph',f).getAttribute('style').includes('var(--'+v+')'));
let vl=[],li=0,gf='all',gn=0;
const gc=()=>innerWidth<=900?2:innerWidth<=1280?3:4,
ga=g=>g.classList.contains('big')?(gc()===2?2:4):g.classList.contains('wide')?2:1,
gp=()=>gc()===4?16:12;
function galShow(reset){const c=gc(),m=figs.filter(g=>gf==='all'||g.dataset.g===gf);if(reset)gn=gp();
  let k=Math.min(gn,m.length),a=0;for(let i=0;i<k;i++)a+=ga(m[i]);
  while(k<m.length&&k>c&&a%c){k--;a-=ga(m[k])}
  vl=m;
  figs.forEach(g=>{const i=m.indexOf(g);if(i>-1&&i<k){if(g.hidden){g.hidden=false;g.classList.add('out');requestAnimationFrame(()=>requestAnimationFrame(()=>g.classList.remove('out')))}}else g.hidden=true});
  const left=m.length-k;more.hidden=left<=0;gl.textContent=left}
$$('.filt button').forEach(b=>b.addEventListener('click',()=>{$$('.filt button').forEach(x=>x.setAttribute('aria-pressed',x===b));gf=b.dataset.f;galShow(true)}));
$('#galbtn').addEventListener('click',()=>{gn+=gp();galShow(false)});
const show=()=>{const f=vl[li];$('#lbph').style.setProperty('--foto',getComputedStyle($('.ph',f)).getPropertyValue('--foto'));$('#lbcap').textContent=tx('figcaption',f)};
const openLb=f=>{li=vl.indexOf(f);show();lb.classList.add('open')};
const step=d=>{li=(li+d+vl.length)%vl.length;show()};
figs.forEach(f=>{f.onclick=()=>openLb(f);f.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();openLb(f)}}});
$('.x',lb).onclick=()=>lb.classList.remove('open');$('.pv',lb).onclick=()=>step(-1);$('.nx',lb).onclick=()=>step(1);
lb.addEventListener('click',e=>{if(e.target===lb)lb.classList.remove('open')});
galShow(true);

"""
h = h[:a] + gal_js + h[b:]

# 6f. brosur memilih foto lewat nama, bukan nomor urut (urutan galeri berubah)
rep("[0,1,2,3,9,12,11,13].map(i=>figs[i]).map(f=>", "['a-plant','a-builtup','a-komp1','a-komp2','m5','m8','m7','m9'].map(FG).map(f=>")
rep("[0,1,2,3,9,12].map(i=>ph(ft($('.ph',figs[i])))).join('')", "['a-plant','a-builtup','a-komp1','a-komp2','m5','m8'].map(v=>ph(ft($('.ph',FG(v))))).join('')")
rep("[0,1,9].map(i=>ph(ft($('.ph',figs[i])))).join('')", "['a-plant','a-builtup','m5'].map(v=>ph(ft($('.ph',FG(v))))).join('')")
rep("addEventListener('resize',()=>{lay();scale();thumbs();on()});", "addEventListener('resize',()=>{lay();scale();thumbs();galShow(false);on()});")


# ---------------------------------------------------------------- 6g. pratinjau brosur: kontrol zoom (teks A4 terlalu kecil di ponsel)
rep('<div class="bk-tip">Pada jendela cetak, pilih tujuan <b>Simpan sebagai PDF</b>. Ukuran A4 lanskap dan tanpa margin sudah diatur otomatis.</div>',
    '<div class="bk-tip"><span class="tp d">Pada jendela cetak, pilih tujuan <b>Simpan sebagai PDF</b>. Ukuran A4 lanskap dan tanpa margin sudah diatur otomatis.</span>'
    '<span class="tp m">Ketuk <b>+</b> untuk memperbesar, lalu geser. Hasil PDF tetap berukuran penuh.</span>'
    '<div class="bk-zoom" role="group" aria-label="Perbesar tampilan"><button type="button" id="bk-zo" aria-label="Perkecil">&minus;</button>'
    '<button type="button" id="bk-zv" aria-label="Sesuaikan lebar layar">Pas</button><button type="button" id="bk-zi" aria-label="Perbesar">+</button></div></div>')
rep("const bk=$('#bk'),pg=$('#bk-pages');", "const bk=$('#bk'),pg=$('#bk-pages');let bz=1;")
rep("function scale(){const s=cl(($('#bk-body').clientWidth-2*cl(innerWidth*.026,16,40))/PW,.3,1.6);",
    "function scale(){const s=cl(($('#bk-body').clientWidth-2*cl(innerWidth*.026,16,40))/PW,.3,1.6)*bz;")
rep("const openBk=(f,pr)=>{render(f);",
    "const bbd=$('#bk-body'),bzl=$('#bk-zv');\n"
    "function zoom(z){z=cl(z,1,3);if(Math.abs(z-bz)<.001)return;const cx=(bbd.scrollLeft+bbd.clientWidth/2)/bbd.scrollWidth,cy=(bbd.scrollTop+bbd.clientHeight/2)/bbd.scrollHeight;"
    "bz=z;scale();bbd.scrollLeft=cx*bbd.scrollWidth-bbd.clientWidth/2;bbd.scrollTop=cy*bbd.scrollHeight-bbd.clientHeight/2;bzl.textContent=bz===1?'Pas':bz.toFixed(1).replace('.',',')+'×'}\n"
    "$('#bk-zi').onclick=()=>zoom(bz*1.4);$('#bk-zo').onclick=()=>zoom(bz/1.4);bzl.onclick=()=>zoom(1);\n"
    "const openBk=(f,pr)=>{bz=1;bzl.textContent='Pas';render(f);")
rep("  #bk-pages{display:block!important}", "  #bk-pages{display:block!important;width:auto!important;min-width:0!important}")

# ---------------------------------------------------------------- 7. CSS
css = open('/home/claude/tools/mobile.css', encoding='utf-8').read()
rep('</style></head>', css + '\n</style></head>')

open(DST, 'w', encoding='utf-8').write(h)
print('ok', len(h))
