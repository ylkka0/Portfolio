import { useState } from 'react';
import { ArrowDown, ArrowUpRight, Braces, Check, ChevronDown, Code2, Github, Layers3, Mail, Workflow } from 'lucide-react';

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
    technologies: ['n8n', 'Freshdesk API', 'Ollama', 'Docker', 'JavaScript'],
    link: '#masadesk',
    action: 'Tutustu toteutukseen',
    illustration: 'masadesk',
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
  },
  {
    number: '04',
    title: 'PILKKI 1999',
    category: 'PELIKEHITYS / UNITY',
    description: 'Itsenäisesti toteutettu, fysiikkapainotteinen 2D-kalastuspeli. Projektiin sisältyy myös moninpelituki.',
    technologies: ['Unity', 'C#', 'Game Design'],
    link: 'https://ylkka0.itch.io/pilkki-1999',
    action: 'Pelaa peliä',
    illustration: 'pilkki',
  },
  {"number":"05","title":"Adobe Illustrator","category":"GRAAFINEN SUUNNITTELU","description":"Kokoelma Adobe Illustrator -töitä: typografiaa, kansisuunnittelua, mainoksia ja julisteita.","technologies":["Adobe Illustrator"],"link":"https://github.com/ylkka0/Portfolio/tree/main/Adobe%20Illustrator.imgs","action":"Katso kaikki työt","illustration":"illustrator","preview":"https://raw.githubusercontent.com/ylkka0/Portfolio/main/Adobe%20Illustrator.imgs/Expressiivinen%20typografia.png","short":"Graafinen suunnittelu"},
  {"number":"06","title":"Mpappa UI","category":"UI / PROTOTYYPPI","description":"Kuvitteellisen pelin käyttöliittymägrafiikkaa ja interaktiivinen Figma-prototyyppi.","technologies":["Figma","UI Design"],"link":"https://www.figma.com/proto/QtoQ1V1p8LAbF7n4c1X9dA/Mpappa?page-id=&node-id=4-6&starting-point-node-id=4%3A6&t=mQ1rwDTWHPIBbQIf-1","action":"Avaa Figma-prototyyppi","illustration":"mpappa","short":"Pelin käyttöliittymäprototyyppi"},
  {"number":"07","title":"WoW Forever – Fishing Bot","category":"PYTHON / AUTOMAATIO","description":"Henkilökohtainen Python-ohjelmointiharjoitus, jossa yhdistyvät työpöytäsovelluksen käyttöliittymä, äänipohjainen tapahtumantunnistus ja automaatiologiikka. Tämähän on siis Blizzardin oma luomus.","technologies":["Python","GUI","Tapahtumapohjainen ohjelmointi"],"link":"https://github.com/ylkka0/Portfolio/blob/main/WoW-Forever-Fishing-Bot.md","action":"Projektin tiedot","illustration":"fishing","preview":"https://github.com/user-attachments/assets/fa995d8b-78b1-4c7a-bb48-ed17cbe74607","short":"Python ja työpöytäautomaatio"},
  {"number":"08","title":"Djatlov.exe","category":"PELIKEHITYS / UNITY","description":"Kahdeksan viikon yksilöprojektina Unitylla toteutettu 3D-kauhudemo.","technologies":["Unity"],"link":"https://ylkka0.itch.io/djatlovgame","action":"Tutustu demoon","illustration":"djatlov","short":"Unity-kauhudemo"},
  {"number":"09","title":"kasinonaata.com","category":"WEB-KEHITYS / KESKENERÄINEN","description":"Keskeneräinen verkkosivuston kehitysprojekti.","technologies":["Web-kehitys"],"link":"https://www.kasinonaata.com/","action":"Avaa sivusto","illustration":"kasinonaata","short":"Keskeneräinen verkkosivusto"},
];

const stack = [
  { title: 'Kehitys', items: 'React · JavaScript · TypeScript · REST API' },
  { title: 'Automaatio & AI', items: 'n8n · Ollama · Docker · API-integraatiot' },
  { title: 'Digitaaliset palvelut', items: 'WordPress · Figma · UX · SEO' },
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
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [projectsOpen, setProjectsOpen] = useState(false);
  const [activeProject, setActiveProject] = useState(0);
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
        </nav>
        <div className="header-contact">
          <a className="nav-contact" href="https://www.linkedin.com/in/matti-yli-hukka/" target="_blank" rel="noopener noreferrer">LinkedIn</a>
          <a className="mail-link" href="mailto:yli.hukka@gmail.com" aria-label="Lähetä sähköpostia" title="yli.hukka@gmail.com"><Mail size={19} strokeWidth={1.6}/></a>
        </div>
      </header>

      <main>
        <section id="alku" className="hero container">
          <div className="hero-copy"><p style={{ fontSize: 15, letterSpacing: "0.16em", marginBottom: 20 }}>AI FIRST</p><h1>Web Development.<br/>Digital Design.<br/>SEO &amp; Marketing.</h1></div><a className="hero-scroll" href="#minusta">( &nbsp; scrollaa alas &nbsp; ) <ArrowDown size={12}/></a>
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
          <div className="container case-layout">
            <div className="case-intro">
              <span className="eyebrow"><span className="eyebrow-line" /> CASE STUDY / MASADESK</span>
              <h2>Paikallinen AI.<br /><span>Älykkäämpi IT-tuki.</span></h2>
              <p>Masadesk on proof of concept, jossa yhdistin Freshdesk-tukijärjestelmän, n8n-työnkulkuautomaation ja Ollaman kautta paikallisesti ajettavan Qwen-kielimallin.</p>
              <p>Ratkaisu luokittelee tukipyynnön, ehdottaa prioriteettia ja kirjoittaa perustelun yksityiseksi muistiinpanoksi. Tukihenkilö säilyttää päätösvastuun.</p>
              <button className="outline-action" onClick={() => setDetailsOpen(!detailsOpen)} aria-expanded={detailsOpen} aria-controls="masadesk-details">{detailsOpen ? 'Piilota toteutuksen vaiheet' : 'Näytä toteutuksen vaiheet'} <ChevronDown className={detailsOpen ? 'rotated' : ''} size={16}/></button>
            </div>
            <div className="case-panel">
              <div className="case-panel-head"><span><span className="status-dot"/> AI CLASSIFICATION SUGGESTION</span><span>DEMO / 001</span></div>
              <div className="case-panel-body"><span className="terminal-label">TICKET #5</span><p className="panel-subtitle">VPN-yhteys ei toimi</p><div className="case-row"><span>Suggested type</span><strong>Incident</strong></div><div className="case-row"><span>Suggested priority</span><strong>Undetermined</strong></div><div className="case-reason"><span>REASON</span><p>Tukipyynnön vaikutuksista ei ole riittävästi tietoa prioriteetin varmaan arviointiin.</p></div><div className="case-footer"><Check size={15}/> PENDING HUMAN REVIEW</div></div>
            </div>
            {detailsOpen && <div className="case-details" id="masadesk-details">
              {[
                ['01', 'Tukipyyntö Freshdeskistä', 'n8n hakee tukipyynnön Freshdesk API:n kautta.'],
                ['02', 'Paikallinen kielimalli', 'Ollama välittää tiketin Qwen-mallille.'],
                ['03', 'Tuloksen validointi', 'Luokittelun tyyppi, prioriteetti ja perustelu tarkistetaan.'],
                ['04', 'Yksityinen AI-muistiinpano', 'Tuloksesta muodostetaan tarkistettava ehdotus Freshdeskiin.']
              ].map(([number,title,detail]) => <div className="case-step" key={number}><span>{number}</span><div><strong>{title}</strong><p>{detail}</p></div></div>)}
              <p className="case-disclaimer">Toteutettu ja testattu teknisenä demona. Ei tuotantovalmis automaatio tai automaattinen päätöksentekojärjestelmä.</p>
            </div>}
          </div>
        </section>

        <section id="osaaminen" className="section skills-section">
          <div className="container">
            <SectionHeading eyebrow="02 / TYÖKALUPAKKI" title="Osaaminen & teknologiat." />
            <div className="skills-grid">{stack.map((group,i) => <div className="skill-card" key={group.title}><div className="skill-top"><span>0{i+1}</span>{i===0?<Code2 size={23}/>:i===1?<Workflow size={23}/>:<Layers3 size={23}/>}</div><h3>{group.title}</h3><p>{group.items}</p></div>)}</div>
          </div>
        </section>

        <section id="minusta" className="section about-section">
          <div className="container about-grid"><div><span className="eyebrow"><span className="eyebrow-line" /> 03 / MINUSTA</span><h2>Uteliaisuudesta<br /><em>toimivaksi koodiksi.</em></h2></div><div className="about-text"><p><strong>Masa = Tietojenkäsittelyn ja liiketoiminnan IT-tradenomi.</strong></p><p>Näissä käsissä yhdistyy digitaalisten palveluiden suunnittelu, web-kehitys, SEO-markkinointi ja tekoälyä hyödyntävät tekniset integraatiot. Oikeastaan, aina kun joku uusi kiehtoo mutta en osaa sitä, niin opettelen.</p><p>Uskon ratkaisuihin, joissa hyvä käyttökokemus, toimiva teknologia ja löydettävyys tukevat toisiaan. Täytyy muistaa, että AI:n mahdollisuudet ovat subjektiivisesti ~rajattomat.</p><p>Oli kyse verkkopalvelusta, automaatiosta tai uudesta ideasta, teen taidonnäytteet asiakkaalle, en itselleni.</p><a href="https://github.com/ylkka0" target="_blank" rel="noopener noreferrer" className="inline-link"><Github size={17}/> Tutustu GitHub-profiiliini <ArrowUpRight size={16}/></a></div></div>
        </section>

        <section id="yhteys" className="contact-section"><div className="container contact-content"><span className="eyebrow"><span className="eyebrow-line" /> 04 / YHTEYS</span><h2>Rakennetaanko jotain<br /><em>kiinnostavaa yhdessä?</em></h2><p>Kiinnostuitko toteutuksista tai haluatko keskustella yhteistyöstä?</p><a className="button button-primary" href="https://github.com/ylkka0" target="_blank" rel="noopener noreferrer">Ota yhteyttä GitHubissa <ArrowUpRight size={18}/></a></div></section>
      </main>
      <footer className="site-footer container"><span>© {new Date().getFullYear()} · PORTFOLIO</span><span>DESIGN · DEVELOPMENT · AUTOMATION</span><a href="#alku">TAKAISIN ALKUUN ↑</a></footer>
    </div>
  );
}
export default App;
