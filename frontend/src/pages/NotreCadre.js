import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Shield, Heart, BookOpen, ArrowLeft } from 'lucide-react';

const Section = ({ icon: Icon, title, children, testid }) => (
  <section
    data-testid={testid}
    style={{
      background: 'rgba(255,255,255,0.025)',
      border: '1px solid rgba(212,180,106,0.18)',
      borderRadius: 18, padding: '28px 26px', marginBottom: 18,
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
      <Icon style={{ width: 22, height: 22, color: '#D4B46A' }} strokeWidth={1.4} />
      <h2 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 22, color: '#F0E6D3', fontWeight: 400, margin: 0 }}>
        {title}
      </h2>
    </div>
    <div style={{ color: 'rgba(240,230,211,0.85)', fontSize: 15, lineHeight: 1.75, fontFamily: 'Cormorant Garamond, serif' }}>
      {children}
    </div>
  </section>
);

const NotreCadre = () => (
  <div style={{ minHeight: '100vh', padding: '120px 20px 100px', maxWidth: 760, margin: '0 auto' }} data-testid="notre-cadre-page">
    <Link to="/"
      style={{ display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'rgba(184,176,200,0.7)', textDecoration: 'none', letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 28 }}>
      <ArrowLeft style={{ width: 13, height: 13 }} /> Retour
    </Link>

    <div style={{ textAlign: 'center', marginBottom: 40 }}>
      <p style={{ fontSize: 11, letterSpacing: '0.3em', color: '#D4B46A', textTransform: 'uppercase', fontFamily: 'Cinzel, serif', marginBottom: 14 }}>
        Notre engagement
      </p>
      <h1 style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 'clamp(34px, 6vw, 54px)', color: '#F0E6D3', fontWeight: 300, lineHeight: 1.1, marginBottom: 16 }}>
        Notre cadre
      </h1>
      <p style={{ fontSize: 16, color: 'rgba(184,176,200,0.85)', maxWidth: 540, margin: '0 auto', lineHeight: 1.65 }}>
        Ce que nous croyons. Ce que nous ne ferons jamais. Comment nous accompagnons votre regard sur vous-même.
      </p>
    </div>

    <Section icon={Sparkles} title="L'astrologie comme miroir, jamais comme prédiction" testid="cadre-symbolic">
      <p style={{ marginBottom: 12 }}>
        Plume Astrale ne <em>prédit pas</em> votre avenir. Aucune carte, aucun thème natal, aucun transit
        ne déterminera ce qui doit se produire dans votre vie.
      </p>
      <p style={{ marginBottom: 12 }}>
        Ce que nous proposons est un <strong style={{ color: '#D4B46A' }}>langage symbolique</strong>
        — celui des étoiles et des cycles — pour vous inviter à mieux écouter ce qui vibre déjà en vous.
        Pour clarifier, ralentir, déposer.
      </p>
      <p>
        Votre vie reste votre œuvre. L&apos;astrologie n&apos;en est qu&apos;une lecture poétique, pas un manuel d&apos;exécution.
        Aucune décision médicale, financière ou juridique ne devrait reposer sur une lecture astrologique.
      </p>
    </Section>

    <Section icon={Shield} title="Ce que nous ne ferons jamais" testid="cadre-ethics">
      <ul style={{ paddingLeft: 18, margin: 0, listStyle: 'none' }}>
        {[
          "Vous faire peur pour vendre quelque chose.",
          "Vous promettre la rencontre, l'argent ou la guérison « certaine ».",
          "Vous enfermer dans un signe ou un destin figé.",
          "Vous envoyer des notifications culpabilisantes (« tu vas perdre ta série »).",
          "Vous vendre l'urgence artificielle ou la rareté fabriquée.",
          "Partager ou vendre vos données. Jamais.",
        ].map((it, i) => (
          <li key={i} style={{ position: 'relative', paddingLeft: 22, marginBottom: 10 }}>
            <span style={{ position: 'absolute', left: 0, color: '#D4B46A' }}>·</span>
            {it}
          </li>
        ))}
      </ul>
    </Section>

    <Section icon={Heart} title="Ce que nous croyons vraiment" testid="cadre-belief">
      <p style={{ marginBottom: 12 }}>
        Que vous êtes l&apos;experte de votre vie. Que l&apos;astrologie est un outil parmi d&apos;autres,
        précieux quand il vous renvoie à vous-même.
      </p>
      <p style={{ marginBottom: 12 }}>
        Que le rituel quotidien — quelques minutes d&apos;écoute, le matin, le soir — change plus
        de vies que n&apos;importe quelle « grande révélation ».
      </p>
      <p style={{ marginBottom: 12 }}>
        Que la <strong style={{ color: '#D4B46A' }}>tension n&apos;est pas un signe d&apos;incompatibilité</strong> dans
        un thème ou dans une relation : c&apos;est un chemin de croissance. Nous nommerons toujours
        les difficultés en termes de potentiel à explorer, jamais comme un mauvais présage.
      </p>
      <p>
        Que l&apos;oubli n&apos;est pas une faute. Si vous ne venez pas un matin, votre journée n&apos;en sera
        pas brisée. Si une série s&apos;interrompt, elle se reprend en douceur — sans culpabilité.
      </p>
    </Section>

    <Section icon={BookOpen} title="Vos données, votre journal" testid="cadre-privacy">
      <p style={{ marginBottom: 12 }}>
        Tout ce que vous écrivez dans votre <em>Réflexion du soir</em> ou dans vos journaux privés
        reste <strong style={{ color: '#D4B46A' }}>strictement entre vous et vous</strong>. Aucune équipe
        humaine n&apos;y a accès. Aucun algorithme n&apos;analyse vos confidences.
      </p>
      <p style={{ marginBottom: 12 }}>
        Vos données natales (date, heure, lieu) servent uniquement à calculer vos lectures.
        Elles ne quittent jamais notre infrastructure et ne sont jamais revendues.
      </p>
      <p>
        Vous pouvez à tout moment exporter vos données ou demander leur suppression définitive
        depuis votre espace Mon Compte.
      </p>
    </Section>

    <div style={{
      background: 'linear-gradient(135deg, rgba(212,180,106,0.08) 0%, rgba(167,139,250,0.06) 100%)',
      border: '1px solid rgba(212,180,106,0.3)',
      borderRadius: 18, padding: 30, textAlign: 'center', marginTop: 24,
    }}>
      <p style={{ fontSize: 11, letterSpacing: '0.2em', color: '#D4B46A', textTransform: 'uppercase', marginBottom: 12, fontFamily: 'Cinzel, serif' }}>
        Notre promesse
      </p>
      <p style={{ fontFamily: 'Cormorant Garamond, serif', fontSize: 22, color: '#F0E6D3', fontStyle: 'italic', lineHeight: 1.45, fontWeight: 300, margin: 0 }}>
        « Nous ne prédisons pas votre avenir. Nous vous invitons à le co-créer,
        un matin, un souffle, une intention à la fois. »
      </p>
    </div>
  </div>
);

export default NotreCadre;
