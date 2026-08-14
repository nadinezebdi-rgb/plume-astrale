import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Sparkles, Download, Mail, ShieldCheck } from 'lucide-react';
import SEO from '@/components/SEO';
import PsPageShell from '@/components/PsPageShell';
import CelestialBackdrop from '@/components/CelestialBackdrop';
import { LECTURES } from '@/config/catalog';

/**
 * /nos-livres — Vitrine des lectures premium PDF · Charte v3 (light).
 *
 * Chaque lecture est une lecture personnalisée au format PDF premium
 * à télécharger. Aucun livre imprimé n'est vendu.
 */

const DETAILS = {
  natal:        { pages: 49, accent: 'La signature Plume', long: 'Onze planètes qui racontent qui tu es vraiment. Écrit à partir de 73 dimensions astrologiques croisées — le socle de toutes les autres lectures.' },
  kabbale:      { pages: 15, accent: 'Kabbalistique',        long: '10 Sephiroth et 22 chemins hébraïques posés sur ta cartographie d\'âme. Où tu rayonnes, où tu ancres, où tu montes.' },
  astrocarto:   { pages: 18, accent: 'Géographie astrale',   long: 'Sept lignes planétaires posées sur la carte du monde. Où vivre ta meilleure vie, où l\'amour te touche, où ton corps se pose enfin.' },
  karma:        { pages: 22, accent: 'Chemin d\'âme',        long: 'Ta lignée karmique décodée : ce que tu portes de tes vies antérieures, ce que tu viens réparer, ce que tu viens accomplir cette fois-ci.' },
  numerologie:  { pages: 16, accent: 'Numérologie sacrée',   long: 'Chemin de vie, année personnelle, nombres actifs. Une lecture chiffrée qui complète l\'astrologie avec précision.' },
  karmique:     { pages: 40, accent: 'L\'écrin ultime',       long: 'Le format le plus profond de Plume Astrale — ton empreinte karmique, ton Arbre de Vie et ta synthèse d\'âme réunis dans un même PDF premium.' },
  synastry:     { pages: 25, accent: 'Astro relationnelle', long: 'L\'aspectarium de votre lien — les deux ciels dansent ensemble. Points d\'harmonie, tensions à cultiver, langages d\'amour croisés.' },
};

const BENEFITS = [
  { icon: Download, title: 'PDF premium à télécharger', body: 'Livré par email après paiement. Aucun envoi physique — tu conserves ta lecture indéfiniment.' },
  { icon: Mail, title: 'Réponse en quelques minutes', body: 'Le PDF arrive sous 5 minutes après validation. En cas de retard, écris-nous, on retrouve ton dossier.' },
  { icon: ShieldCheck, title: 'Paiement sécurisé Stripe', body: 'Carte bancaire, 3-D Secure, PCI-DSS. Aucune donnée bancaire stockée chez nous.' },
];

export default function NosLivres() {
  return (
    <PsPageShell background="light">
      <SEO
        path="/nos-livres"
        title="Nos lectures · Bibliothèque Plume Astrale"
        description="Sept lectures astrologiques premium en PDF à télécharger — Thème Natal, Astrologie relationnelle, Arbre de Vie, Astrocartographie, Pack Karmique, Karma & Destin, Numérologie."
      />

      {/* Section hero */}
      <section className="ps-section ps-section-light" data-testid="nos-livres-page">
        <div className="ps-container">
          <div style={{ maxWidth: 720, marginBottom: 64 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>La bibliothèque Plume Astrale</p>
            <h1 className="ps-h1" style={{ color: '#0F1A3C', marginBottom: 20 }}>
              Sept lectures, <span className="ps-italic">une seule signature.</span>
            </h1>
            <p className="ps-body" style={{ color: '#232323' }}>
              Chaque lecture est un PDF premium à télécharger, personnalisé à partir de ton thème natal
              (date, heure et lieu de naissance). Aucune vente de livre physique — l&apos;objet est le texte,
              soigné et unique.
            </p>
          </div>

          {/* Grille des lectures */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: 24,
          }}>
            {LECTURES.map((lec) => {
              const detail = DETAILS[lec.key] || {};
              return (
                <Link key={lec.key} to={lec.to}
                  className="ps-card"
                  data-testid={`nos-livres-card-${lec.key}`}
                  style={{
                    textDecoration: 'none',
                    display: 'flex', flexDirection: 'column',
                    borderColor: lec.highlight ? '#C9A24B' : '#E3E1DC',
                    background: lec.highlight ? 'linear-gradient(135deg, #FFFEF8 0%, #FFFFFF 100%)' : '#fff',
                  }}>
                  {lec.highlight && (
                    <div style={{
                      alignSelf: 'flex-start',
                      background: '#C9A24B', color: '#0F1A3C',
                      fontFamily: 'Inter, sans-serif', fontSize: 11, fontWeight: 600,
                      letterSpacing: '0.12em', textTransform: 'uppercase',
                      padding: '4px 10px', borderRadius: 6,
                      marginBottom: 12,
                    }}>
                      L&apos;offre écrin
                    </div>
                  )}

                  <div style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 11, fontWeight: 600,
                    letterSpacing: '0.16em', textTransform: 'uppercase',
                    color: '#C9A24B', marginBottom: 8,
                  }}>
                    {detail.accent}
                  </div>

                  <h2 className="ps-h3" style={{ color: '#0F1A3C', marginBottom: 8 }}>{lec.title}</h2>

                  <p style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14, lineHeight: 1.55, color: '#6B7280',
                    margin: 0, marginBottom: 20, flex: 1,
                  }}>
                    {detail.long}
                  </p>

                  <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end',
                    paddingTop: 16, borderTop: '1px solid #E3E1DC',
                  }}>
                    <div>
                      <div style={{
                        fontFamily: 'Playfair Display, serif',
                        fontSize: 24, fontWeight: 500,
                        color: '#0F1A3C', lineHeight: 1,
                      }}>{lec.price}</div>
                      <div style={{
                        fontFamily: 'Inter, sans-serif',
                        fontSize: 12, color: '#6B7280',
                        marginTop: 4,
                      }}>{detail.pages} pages · PDF</div>
                    </div>
                    <span style={{
                      display: 'inline-flex', alignItems: 'center', gap: 4,
                      fontFamily: 'Inter, sans-serif',
                      fontSize: 13, fontWeight: 500, color: '#C9A24B',
                    }}>
                      Découvrir
                      <ArrowRight style={{ width: 14, height: 14 }} strokeWidth={2} />
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* Section bénéfices (sombre) */}
      <section className="ps-section ps-section-dark" data-testid="nos-livres-benefits">
        <CelestialBackdrop density={75} shootingStars interval={13000} />
        <div className="ps-container">
          <div style={{ maxWidth: 720, marginBottom: 56 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Comment ça marche</p>
            <h2 className="ps-h2" style={{ color: '#F7F5F0', marginBottom: 20 }}>
              Ton PDF <span className="ps-italic">t&apos;attend dans ta boîte mail</span> en quelques minutes.
            </h2>
          </div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: 24,
          }}>
            {BENEFITS.map((b) => {
              const Icon = b.icon;
              return (
                <div key={b.title} className="ps-card" data-testid={`benefit-${b.title.toLowerCase().replace(/\s+/g, '-')}`}>
                  <div style={{
                    width: 44, height: 44, borderRadius: 10,
                    background: 'rgba(201,162,75,0.10)',
                    display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                    marginBottom: 16,
                  }}>
                    <Icon style={{ width: 20, height: 20, color: '#C9A24B' }} strokeWidth={1.6} />
                  </div>
                  <h3 className="ps-h3" style={{ color: '#F7F5F0', marginBottom: 10, fontSize: 20 }}>{b.title}</h3>
                  <p style={{
                    fontFamily: 'Inter, sans-serif',
                    fontSize: 14, lineHeight: 1.6,
                    color: 'rgba(247,245,240,0.72)', margin: 0,
                  }}>{b.body}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA final */}
      <section className="ps-section ps-section-light" data-testid="nos-livres-cta">
        <div className="ps-container">
          <div style={{ maxWidth: 640 }}>
            <p className="ps-eyebrow" style={{ marginBottom: 16 }}>Prête à commencer ?</p>
            <h2 className="ps-h2" style={{ color: '#0F1A3C', marginBottom: 24 }}>
              20 crédits <span className="ps-italic">offerts</span> à l&apos;inscription.
            </h2>
            <p className="ps-body" style={{ color: '#232323', marginBottom: 32 }}>
              Crée ton compte gratuit et découvre Soléna à ton rythme — sans carte bancaire, sans engagement.
            </p>
            <Link to="/inscription" className="ps-btn ps-btn-primary"
              data-testid="nos-livres-cta-final"
              style={{ padding: '16px 32px', fontSize: 16 }}>
              Créer mon compte
              <Sparkles style={{ width: 18, height: 18 }} strokeWidth={2} />
            </Link>
          </div>
        </div>
      </section>
    </PsPageShell>
  );
}
