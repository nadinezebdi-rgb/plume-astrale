import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpenCheck, BrainCircuit, MailCheck, UserRoundPen } from 'lucide-react';

const STEPS = [
  {
    icon: UserRoundPen,
    number: '01',
    title: 'Vous renseignez votre ciel',
    body: 'Date, heure et lieu de naissance : les données qui rendent chaque lecture réellement unique.',
  },
  {
    icon: BrainCircuit,
    number: '02',
    title: 'Le moteur interprète',
    body: 'Les calculs deviennent une trame cohérente, structurée autour de vos cycles et de vos points d’appui.',
  },
  {
    icon: BookOpenCheck,
    number: '03',
    title: 'Votre livre est composé',
    body: 'Le contenu est rédigé, hiérarchisé et mis en page comme une édition personnelle premium.',
  },
  {
    icon: MailCheck,
    number: '04',
    title: 'Vous le recevez',
    body: 'Le PDF est livré automatiquement par email, prêt à être lu, imprimé et conservé.',
  },
];

export default function ConcoursImpact() {
  return (
    <section className="ne-section ne-section-paper ne-impact" data-testid="concours-impact">
      <div className="ne-container">
        <div className="ne-impact-heading">
          <div>
            <div className="ne-overline">Construit avec Emergent &middot; Utilisé dans une activité réelle</div>
            <h2 className="ne-h1 ne-impact-title">
              Une expertise artisanale,
              <span className="ne-serif-italic"> rendue instantanée.</span>
            </h2>
          </div>
          <p className="ne-body ne-impact-intro">
            Plume Astrale réunit dans un seul parcours ce qui demandait auparavant une succession
            d&rsquo;étapes manuelles : collecte, calcul, rédaction, composition, paiement et livraison.
          </p>
        </div>

        <div className="ne-impact-rail" data-testid="concours-impact-steps">
          {STEPS.map((step) => {
            const Icon = step.icon;
            return (
              <article className="ne-impact-step" key={step.number}>
                <div className="ne-impact-step-top">
                  <span className="ne-impact-number">{step.number}</span>
                  <span className="ne-impact-icon"><Icon aria-hidden="true" /></span>
                </div>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </article>
            );
          })}
        </div>

        <div className="ne-impact-cta">
          <div>
            <strong>Le meilleur moyen de comprendre Plume Astrale est de la vivre.</strong>
            <span>Votre aperçu de 5 pages est offert, sans carte bancaire.</span>
          </div>
          <Link to="/inscription" className="ne-btn ne-btn-primary" data-testid="concours-impact-cta">
            Commencer mon expérience
            <ArrowRight style={{ width: 16, height: 16 }} strokeWidth={1.6} />
          </Link>
        </div>
      </div>
    </section>
  );
}
