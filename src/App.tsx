import { useState } from 'react';
import { ArrowDown, ArrowUpRight, Braces, Check, ChevronDown, ChevronLeft, ChevronRight, Code2, Github, Layers3, Mail, Workflow } from 'lucide-react';

type Project = {
  number: string;
  title: string;
  category: string;
  description: string;
  technologies: string[];
  link: string;
  action: string;
  illustration: string;
  featured?: boolean;
  preview?: string;
  short?: string;
};

const projects: Project[] = [
  {
    number: '01',
    title: 'Masadesk',
    category: 'AI / AUTOMAATIO / API',
    description: 'Proof of concept IT-tukipyyntöjen luokitteluun. Freshdesk, n8n ja paikallinen Ollama-kielimalli muodostavat perustellun AI-ehdotuksen tukihenkilön tarkistettavaksi.',
    technologies: ['n8n', 'Ollama', 'Qwen', 'Freshdesk API', 'Docker', 'JavaScript'],
    link: '#masadesk',
    action: 'Tutustu toteutukseen',
    illustration: 'masadesk',
    preview: new URL('./images/masadesk-workflow.png', import.meta.url).href,
    featured: true,
  },
  {
    number: '02',
    title: 'Taidekupla',
    category: 'WEB / PALVELUMUOTOILU',
    description: 'Kolmen hengen tiimissä kehitetty WordPress-pohjainen taideyhteisö. Työssä korostuivat käyttäjäymmärrys, SEO, analytiikka ja palvelun iterointi.',
    technologies: ['WordPress', 'SEO', 'Analytiikka', 'Palvelumuotoilu'],
    link: 'https://github.com/ylkka0/Portfolio/blob/main/taidekupla.fi.md',
    action: 'Projektin tiedot',
    illustration: 'taide',
    preview: 'https://github.com/user-attachments/assets/322ee75e-afb3-4a62-ab62-b17da68679b7',
  },
  {
    number: '03',
    title: 'Soite — Tukea digiasiointiin',
    category: 'UX / DIGITAALISET PALVELUT',
    description: 'Ikääntyneille suunnatun digiasioinnin tukipalvelun prototyyppi sekä verkkosivutoteutus. Painopisteenä saavutettavuus ja asiakaslähtöinen suunnittelu.',
    technologies: ['Figma', 'WordPress', 'UX', 'Saavutettavuus'],
    link: 'https://github.com/ylkka0/Portfolio/blob/main/SOITE%20Digipalvelut.md',
    action: 'Projektin tiedot',
    illustration: 'soite',
    preview: 'https://github.com/user-attachments/assets/a9aced46-303d-44be-9c2f-c180c58654f0',
  },
  {
    number: '04',
    title: 'PILKKI 1999',
    category: 'PELIKEHITYS / UNITY',
    description: 'Unitylla itsenäisesti toteutettu, fysiikkapainotteinen 2D-kalastuspeli. Projektiin sisältyy myös moninpelituki.',
    technologies: ['Unity', 'C#', 'Game Design'],
    link: 'https://ylkka0.itch.io/pilkki-1999',
    action: 'Pelaa peliä',
    illustration: 'pilkki',
    preview: 'https://github.com/user-attachments/assets/36b39f76-40e7-40ba-ba81-e6d428ddcc07',
  },
  {"number":"05","title":"Visual Design & UI","category":"GRAAFINEN SUUNNITTELU","description":"Kokoelma vektorigrafiikkaa: käyttöliittymää, typografiaa, kansisuunnittelua, mainoksia ja julisteita.","technologies":["Adobe Illustrator"],"link":"https://github.com/ylkka0/Portfolio/tree/main/Adobe%20Illustrator.imgs","action":"Katso kaikki työt","illustration":"illustrator","preview":"https://raw.githubusercontent.com/ylkka0/Portfolio/main/Adobe%20Illustrator.imgs/1_Lehtipainatus.png","short":"Graafinen suunnittelu"},
  {"number":"06","title":"Mpappa UI","category":"UI / PROTOTYYPPI","description":"Kuvitteellisen pelin käyttöliittymägrafiikkaa ja interaktiivinen Figma-prototyyppi.","technologies":["Figma","UI Design"],"link":"https://www.figma.com/proto/QtoQ1V1p8LAbF7n4c1X9dA/Mpappa?page-id=&node-id=4-6&starting-point-node-id=4%3A6&t=mQ1rwDTWHPIBbQIf-1","action":"Avaa Figma-prototyyppi","illustration":"mpappa","preview":new URL("./images/mpappa.webp", import.meta.url).href,"short":"Pelin käyttöliittymäprototyyppi"},
  {"number":"07","title":"WoW Forever – Fishing Bot","category":"PYTHON / AUTOMAATIO","description":"Henkilökohtainen Python-ohjelma, jossa yhdistyvät työpöytäsovelluksen käyttöliittymä, äänipohjainen tapahtumantunnistus ja automaatiologiikka. Tämähän on siis Blizzardin tukema luomus.","technologies":["Python","GUI","Tapahtumapohjainen ohjelmointi"],"link":"https://github.com/ylkka0/Portfolio/blob/main/WoW-Forever-Fishing-Bot.md","action":"Projektin tiedot","illustration":"fishing","preview":"https://github.com/user-attachments/assets/fa995d8b-78b1-4c7a-bb48-ed17cbe74607","short":"Python ja työpöytäautomaatio"},
  {"number":"08","title":"Djatlov.exe","category":"PELIKEHITYS / UNITY","description":"Kahdeksan viikon yksilöprojektina Unitylla toteutettu 3D-kauhudemo.","technologies":["Unity"],"link":"https://ylkka0.itch.io/djatlovgame","action":"Tutustu demoon","illustration":"djatlov","preview":new URL("./images/djatlov-rajattu.png", import.meta.url).href,"short":"Unity-kauhudemo"},
  {"number":"09","title":"kasinonaata.com","category":"WEB-KEHITYS / KESKENERÄINEN","description":"Keskeneräinen verkkosivuston kehitysprojekti.","technologies":["Web-kehitys"],"link":"https://www.kasinonaata.com/","action":"Avaa sivusto","illustration":"kasinonaata","preview":new URL("./images/kasinonaata.webp", import.meta.url).href,"short":"Keskeneräinen verkkosivusto"},
];

const stack = [
  { title: 'Kehitys', items: 'TypeScript · HTML · CSS · Python · C# · SQL · Git · GitHub · REST API · Unity · Cloudflare · React · Vite' },
  { title: 'Automaatio & AI', items: 'n8n · Power Automate · LLM · Ollama · Qwen · Docker · Freshdesk · API-integraatiot · Prompt engineering · AI-avusteinen ohjelmistokehitys · AI-agentit' },
  { title: 'Digitaalinen liiketoiminta & Design', items: 'WordPress · Shopify · Figma · Adobe Creative Cloud · GIMP · UI/UX · Palvelumuotoilu · Saavutettavuus · Data-analytiikka · CRM' },
  { title: 'Digitaalinen markkinointi', items: 'SEO · GEO · AEO · Google Analytics 4 · Google Search Console · Avainsanatutkimus · Sisältöstrategia · Konversio-optimointi (CRO)' },
];

function SectionHeading({ eyebrow, title, text }: { eyebrow: string; title: string; text?: string }) {
  return (
    <div className="section-heading">
      <span className="eyebrow"><span className="eyebrow-line" />{eyebrow}</span>
      <h2>{title}</h2>
      {text && <p>{text}</p>}
    </div>
  );
}

function ProjectVisual({ kind }: { kind: string }) {
  const project = projects.find(p => p.illustration === kind);
  if (project?.preview) return <div className="project-visual visual-image"><img src={project.preview} alt={project.title + ' – projektikuva'}/></div>;
  if (project && !['masadesk','taide','soite','pilkki'].includes(kind)) return <div className="project-visual visual-simple"><span>{project.title}</span></div>;
  if (kind === 'masadesk') return (
    <div className="project-visual visual-masadesk" aria-label="Masadesk-automaation havainnekuva">
      <div className="visual-grid" />
      <div className="mini-badge">WORKFLOW / ACTIVE CONCEPT</div>
      <div className="workflow-illustration">
        <span className="workflow-node"><Layers3 size={22} /><small>FRESHDESK</small></span>
        <span className="workflow-connector" />
        <span className="workflow-node node-accent"><Workflow size={22} /><small>N8N</small></span>
        <span className="workflow-connector" />
        <span className="workflow-node"><Braces size={22} /><small>OLLAMA</small></span>
      </div>
      <div className="visual-caption"><span className="status-dot" /> AI-AVUSTEINEN TUKIPYYNTÖPROSESSI</div>
    </div>
  );
  return (
    <div className={`project-visual visual-${kind}`} aria-hidden="true">
      <div className="visual-grid" />
      <span className="visual-initials">{kind === 'taide' ? 'TK.' : kind === 'soite' ? 'UX.' : 'P99.'}</span>
      <div className="visual-orb orb-one" /><div className="visual-orb orb-two" />
      <span className="visual-bottom-label">{kind === 'taide' ? 'DIGITAL EXPERIENCE' : kind === 'soite' ? 'ACCESSIBLE DESIGN' : 'INTERACTIVE PROJECT'}</span>
    </div>
  );
}

function App() {
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [activeProject, setActiveProject] = useState(0);
  const [caseSlide, setCaseSlide] = useState(0);
  const caseSlides = ['Demovideo', 'Miten ratkaisu toimii?', 'Lopputulos', 'Mitä opin?'];
  const closeMenu = () => setProjectsOpen(false);
  return (
    <div className="site">
      <header className="site-header">
        <a href="#alku" className="brand" onClick={closeMenu} aria-label="Takaisin alkuun">
          <span className="brand-symbol">M.</span>
        </a>
        <nav className="nav" aria-label="Päänavigaatio">
          <div className="project-nav" onMouseEnter={() => { if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) setProjectsOpen(true); }} onMouseLeave={() => { if (window.matchMedia('(hover: hover) and (pointer: fine)').matches) setProjectsOpen(false); }} onBlur={e => { if (!e.currentTarget.contains(e.relatedTarget)) setProjectsOpen(false); }} onKeyDown={e => { if (e.key === 'Escape') { setProjectsOpen(false); e.currentTarget.querySelector('button')?.focus(); } }}>
            <button className="project-trigger" aria-expanded={projectsOpen} aria-controls="project-dropdown" onClick={() => setProjectsOpen(!projectsOpen)}>Projektit <ChevronDown size={13}/></button>
            {projectsOpen && <div className="dropdown-wrap" id="project-dropdown"><div className="project-dropdown"><div className="dropdown-list">{projects.map((project,i) => <a key={project.number} className={activeProject===i?'selected':''} href={'#project-'+project.number} onMouseEnter={() => setActiveProject(i)} onFocus={() => setActiveProject(i)} onClick={closeMenu}><strong>{project.title}</strong><small>{project.short ?? ['AI ja automaatio','Web ja palvelumuotoilu','UX ja digitaaliset palvelut','Pelikehitys'][i]}</small></a>)}</div><div className="dropdown-preview" key={activeProject}><ProjectVisual kind={projects[activeProject].illustration}/><p>{projects[activeProject].description}</p></div></div></div>}
          </div>
          <a className="info-nav-link" href="#minusta" onClick={closeMenu}>Info</a>
        </nav>
        <div className="header-contact">
          <a className="nav-contact" href="https://www.linkedin.com/in/matti-yli-hukka/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
          <a className="mail-link" href="mailto:yli.hukka@gmail.com" aria-label="Lähetä sähköpostia" title="yli.hukka@gmail.com"><Mail size={19} strokeWidth={1.6}/></a>
        </div>
      </header>

      <main>
        <section id="alku" className="hero container">
          <div className="hero-copy"><p style={{ fontSize: 13, color: "#FFFFFF", letterSpacing: "0.16em", marginBottom: 20 }}>AI FIRST</p><h1>Web Development.<br/>Digital Design.<br/>SEO &amp; Marketing.</h1></div><a className="hero-scroll" href="#minusta">( &nbsp; scrollaa alas &nbsp; ) <ArrowDown size={12}/></a>
        </section>

        <section id="projektit" className="section projects-section">
          <div className="container">
            <SectionHeading eyebrow="01 / PROJEKTIT" title="Valikoituja töitä." text="Käytännön toteutuksia verkkopalveluista tekoälyautomaatioon." />
            <div className="projects-grid">
              {projects.map((project) => (
                <article id={'project-'+project.number} className={project.featured ? 'project-card project-featured' : 'project-card'} key={project.number}>
                  <ProjectVisual kind={project.illustration} />
                  <div className="project-info">
                    <div className="project-meta"><span>{project.number} / {project.category}</span>{project.featured && <span className="featured-label">FEATURED</span>}</div>
                    <h3>{project.title}</h3>
                    <p>{project.description}</p>
                    <div className="tech-tags">{project.technologies.map(tech => <span key={tech}>{tech}</span>)}</div>
                    <a className="project-link" href={project.link} {...(project.link.startsWith('http') ? {target:'_blank', rel:'noopener noreferrer'} : {})}>{project.action} <ArrowUpRight size={17}/></a>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section id="masadesk" className="section case-section">
          <div className="container case-layout masadesk-case">
            <div className="case-intro">
              <h2>Masadesk — AI-avusteinen IT-tukipalvelu</h2>
              <p>Paikalliseen tekoälyyn perustuva tukipyyntöjen luokitteludemo.</p>
              <p className="case-technologies">n8n · Ollama · Qwen · Freshdesk API · Docker · JavaScript</p>
              <h3>Projektin tavoite</h3>
              <p>Voisiko paikallisesti toimiva tekoäly helpottaa IT-tukipyyntöjen käsittelyä?</p>
              <p>Rakensin tätä varten Masadesk-demon, jossa n8n yhdistää Freshdesk-tukipalvelujärjestelmän paikallisesti ajettavaan Qwen-kielimalliin Ollaman kautta.</p>
              <p>Tavoitteena oli automatisoida tukipyyntöjen alustava luokittelu säilyttäen lopullinen päätöksenteko ihmisellä.</p>
            </div>
            <div className="case-example">
              <h3>Konkreettinen esimerkki</h3>
              <div className="case-panel">
                <div className="case-panel-head"><span><span className="status-dot"/> AI CLASSIFICATION SUGGESTION</span><span>DEMO</span></div>
                <div className="case-panel-body">
                  <span className="terminal-label">TESTITILANNE</span>
                  <p className="panel-subtitle">VPN-yhteyden toimintahäiriö</p>
                  <div className="case-row"><span>Tyyppi</span><strong>Incident</strong></div>
                  <div className="case-row"><span>Prioriteetti</span><strong>Undetermined</strong></div>
                  <div className="case-reason"><span>PERUSTELU</span><p>Tukipyynnön tiedoista ei voida riittävän varmasti päätellä häiriön liiketoimintavaikutuksia tai kiireellisyyttä.</p></div>
                  <div className="case-footer"><Check size={15}/> PENDING HUMAN REVIEW</div>
                </div>
              </div>
              <p>AI ei siis antanut perusteettoman korkeaa prioriteettia, vaan tunnisti tietojen riittämättömyyden.</p>
              <p className="case-caption">Esimerkin ongelmakuvaus on tiivistetty. AI:n luokittelutulos perustuu toteutuneeseen testiin. Paneeli havainnollistaa testitulosta.</p>
            </div>
            <section className="case-carousel" aria-label="Masadeskin lisätiedot" aria-roledescription="karuselli">
              <div className="case-carousel-nav">
                <div className="case-carousel-links" role="group" aria-label="Valitse sisältö">
                  {caseSlides.map((label,i)=><button type="button" key={label} aria-pressed={caseSlide === i} className={caseSlide === i ? 'is-active' : ''} onClick={()=>setCaseSlide(i)}>{label}</button>)}
                </div>
                <div className="case-carousel-arrows">
                  <button type="button" aria-label="Edellinen sisältö" onClick={()=>setCaseSlide(i=>(i+caseSlides.length-1)%caseSlides.length)}><ChevronLeft size={19}/></button>
                  <span aria-live="polite" aria-atomic="true">{caseSlide+1} / {caseSlides.length}</span>
                  <button type="button" aria-label="Seuraava sisältö" onClick={()=>setCaseSlide(i=>(i+1)%caseSlides.length)}><ChevronRight size={19}/></button>
                </div>
              </div>
              <div className="case-carousel-content" role="group" aria-label={caseSlides[caseSlide]} aria-roledescription="dia">
              {caseSlide === 0 && (
            <div className="case-demo">
              <h3>Demovideo</h3>
              <video className="case-video" controls playsInline preload="metadata" aria-label="Masadeskin toiminnallinen demovideo" width={1600} height={694}>
                <source src={new URL('./images/masadesk-demo.mp4', import.meta.url).href} type="video/mp4"/>
                Selaimesi ei tue videon toistoa.
              </video>
              <p className="case-caption">54 sekunnin toiminnallinen esittely.</p>
            </div>
              )}
              {caseSlide === 1 && (
            <div className="case-architecture">
              <h3>Miten ratkaisu toimii?</h3>
              <div className="case-flow" aria-label="Freshdesk, n8n, Ollama ja Qwen, n8n, Freshdesk">
                {['Freshdesk', 'n8n', 'Ollama / Qwen', 'n8n', 'Freshdesk'].map((name,i)=><div className="case-flow-stage" key={i}><span>{name}</span>{i<4&&<span className="case-flow-arrow" aria-hidden="true">→</span>}</div>)}
              </div>
              <figure className="case-workflow">
                <a href={new URL('./images/masadesk-workflow.png', import.meta.url).href} target="_blank" rel="noopener noreferrer" aria-label="Avaa n8n-työnkulun kuva täysikokoisena">
                  <img src={new URL('./images/masadesk-workflow.png', import.meta.url).href} width={1647} height={359} loading="lazy" alt="Masadeskin todellinen n8n-työnkulku: tukipyyntöjen haku, AI-luokittelu, validointi, aiempien muistiinpanojen tarkistus ja yksityisen AI-muistiinpanon tallennus"/>
                </a>
                <figcaption className="case-caption">n8n-työnkulku. Avaa kuva täysikokoisena painamalla sitä.</figcaption>
              </figure>
              <ol className="case-process">
                <li>n8n hakee tukipyynnön Freshdeskin REST API:sta.</li>
                <li>Tukipyynnön otsikko ja kuvaus välitetään Ollamassa toimivalle kielimallille.</li>
                <li>Tekoäly ehdottaa tukipyynnön tyyppiä ja prioriteettia sekä perustelee valintansa.</li>
                <li>n8n validoi vastauksen ja tarkistaa aiemmat AI-muistiinpanot.</li>
                <li>Luokitteluehdotus voidaan tallentaa Freshdeskiin yksityisenä muistiinpanona tukihenkilön tarkistettavaksi.</li>
              </ol>
            </div>
              )}
              {caseSlide === 2 && (
            <div className="case-outcome">
              <h3>Lopputulos</h3>
              <p>Toteutin toimivan proof of conceptin, jossa paikallinen kielimalli analysoi Freshdesk-tukipyynnön ja luokitteluehdotus tallennettiin onnistuneesti yksityiseksi muistiinpanoksi.</p>
              <p>Lisäksi testasin ajastettua tikettihakua, vastausten validointia ja duplikaattimuistiinpanojen tunnistusta.</p>
              <p>Projekti osoittaa, miten olemassa olevia järjestelmiä voidaan yhdistää paikalliseen tekoälyyn kevyellä automaatioratkaisulla.</p>
            </div>
              )}
              {caseSlide === 3 && (
            <div className="case-learning">
              <h3>Mitä opin?</h3>
              <p>Projektissa kehitin osaamistani REST API -integraatioissa, n8n-työnkuluissa, Docker-ympäristöissä ja paikallisten kielimallien hyödyntämisessä.</p>
              <p>Keskeinen oppi oli, että toimiva AI-integraatio vaatii kielimallin lisäksi huolellista tiedonkäsittelyä, vastausten validointia ja virhetilanteiden huomioimista.</p>
            </div>
              )}
              </div>
            </section>
            <p className="case-disclaimer">Projektin rajaus: Tekninen proof of concept. Tuotantokäyttöä tai mitattuja ajansäästöjä ei ole osoitettu.</p>
          </div>
        </section>

        <section id="osaaminen" className="section skills-section">
          <div className="container">
            <SectionHeading eyebrow="02 / TYÖKALUPAKKI" title="Osaaminen & teknologiat." />
            <div className="skills-grid">{stack.map((group,i) => <div className="skill-card" key={group.title}><div className="skill-top"><span>0{i+1}</span>{i===0?<Code2 size={23}/>:i===1?<Workflow size={23}/>:<Layers3 size={23}/>}</div><h3>{group.title}</h3><p>{group.items}</p></div>)}</div>
          </div>
        </section>

        <section id="minusta" className="section about-section">
          <div className="container about-grid">
            <div className="about-profile">
              <img className="about-portrait" src={new URL("./images/masa.png", import.meta.url).href} alt="Musta­valkoinen muotokuva" loading="lazy" width={1122} height={1402}/>
              <div className="about-manifesto">
                <h3>Älä palkkaa tätä tyyppiä. Eihän se ede näe?</h3>
                <p><em>&nbsp;&nbsp;Ensinnäkään, hän ei suostu tekemään sulle ilmaista nettisivua. Ja vielä väittää, ettei hienosta sivustosta ole hyötyä, jos kukaan ei sinne löydä.</em></p>
                <p><em>&nbsp;&nbsp;Toiseksi hän ei edes suostu keksimään asiakasmääriä saadakseen sut yhteistyöhön. Mielummin lupaa vähemmän ja toimittaa enemmän.</em></p>
                <p><em>&nbsp;&nbsp;No kolmanneksi hän painaa täysiä hakukoneoptimoinnin eteen, jotta asiakkaat löytäisivät yrityksesi Googlesta ja AI-koneista ilman, että sun rahaa palaa mainontaan.</em></p>
                <p><em>&nbsp;&nbsp;Ja kaiken huipuksi hän takaa vain aikansa, työpanoksensa ja sen, että sokkona ei huitaista. Miten kehtaa?</em></p>
                <p><strong>Älä siis ota yhteyttä. Ellet sitten halua oikeaa tekemistä tyhjän myyntipuheen sijaan.</strong></p>
              </div>
            </div>
            <div className="about-text"><p><strong>Masa = Tietojenkäsittelyn ja liiketoiminnan IT-tradenomi.</strong></p><p>Näissä käsissä yhdistyy digitaalisten palveluiden suunnittelu, web-kehitys, SEO-ympäristö ja tekoälyä hyödyntävät tekniset integraatiot. Oikeastaan, aina kun joku uusi kiehtoo mutta en osaa sitä, niin opettelen.</p><p>Uskon ratkaisuihin, joissa hyvä käyttökokemus, toimiva teknologia ja löydettävyys tukevat toisiaan. Täytyy muistaa, että AI:n mahdollisuudet ovat subjektiivisesti ~rajattomat.</p><p>Oli kyse digitaalisesta toimenpiteestä, luistimen terottamisesta tai kehitysideasta, teen taidonnäytteet asiakkaalle, en itselleni.</p><a href="https://github.com/ylkka0" target="_blank" rel="noopener noreferrer" className="inline-link"><Github size={17}/> Tutustu GitHub-profiiliini <ArrowUpRight size={16}/></a></div></div>
        </section>

        <section id="yhteys" className="contact-section"><div className="container contact-content"><span className="eyebrow"><span className="eyebrow-line" /> 04 / YHTEYS</span><h2>Rakennetaanko jotain<br /><em>kiinnostavaa yhdessä?</em></h2><p>Paa viestiä.</p><a className="button button-primary" href="https://github.com/ylkka0" target="_blank" rel="noopener noreferrer">Ota yhteyttä GitHubissa <ArrowUpRight size={18}/></a></div></section>
      </main>
      <footer className="site-footer container"><span>© {new Date().getFullYear()} · PORTFOLIO</span><span>DESIGN · DEVELOPMENT · AUTOMATION</span><a href="#alku">TAKAISIN ALKUUN ↑</a></footer>
    </div>
  );
}
export default App;
