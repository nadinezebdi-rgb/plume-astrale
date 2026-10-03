import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import SEO from '@/components/SEO';
import PsPageShell from '@/components/PsPageShell';

const QUESTIONS = [
  {
    question: 'Comment choisir le service qui me correspond ?',
    answer: <>Partez de ce que vous traversez : <Link to="/decouvrir">le parcours de recommandation</Link> vous oriente vers une lecture adaptée. Vous pouvez aussi parcourir directement <Link to="/#home-gateway-services">toutes les prestations</Link>.</>,
  },
  {
    question: 'Les lectures sont-elles personnalisées ?',
    answer: 'Oui. Les lectures astrologiques sont préparées à partir des informations demandées sur la page de chaque service. Les détails et le prix sont indiqués avant l’achat.',
  },
  {
    question: 'Puis-je choisir une seule lecture ?',
    answer: 'Oui. Chaque prestation dispose de son propre parcours de commande. Vous choisissez uniquement les lectures ou services qui vous intéressent.',
  },
  {
    question: 'Comment retrouver mes achats ?',
    answer: <>Connectez-vous à <Link to="/mon-compte">votre espace</Link> pour retrouver vos lectures et crédits associés à votre compte.</>,
  },
];

export default function FAQ() {
  return (
    <PsPageShell background="light">
      <SEO path="/faq" title="Questions fréquentes · Plume Astrale" description="Réponses aux questions sur les lectures, services et achats Plume Astrale." />
      <main data-testid="faq-page" style={{ maxWidth: 820, minHeight: '70vh', margin: '0 auto', padding: '72px 24px 96px' }}>
        <p style={{ margin: '0 0 12px', color: 'var(--plume-gold)', font: '12px Inter, sans-serif', letterSpacing: '0.12em', textTransform: 'uppercase' }}>Besoin d&apos;un repère</p>
        <h1 style={{ margin: '0 0 32px', color: 'var(--plume-night)', font: '500 42px/1.12 Playfair Display, Georgia, serif' }}>Questions fréquentes</h1>
        <div style={{ borderTop: '1px solid rgba(17,22,37,0.15)' }}>
          {QUESTIONS.map(({ question, answer }) => (
            <details key={question} data-testid="faq-item" style={{ padding: '20px 0', borderBottom: '1px solid rgba(17,22,37,0.15)' }}>
              <summary style={{ color: 'var(--plume-night)', font: '500 18px/1.4 Playfair Display, Georgia, serif', cursor: 'pointer' }}>{question}</summary>
              <p style={{ margin: '12px 0 0', color: 'var(--pa-muted)', font: '14px/1.7 Inter, sans-serif' }}>{answer}</p>
            </details>
          ))}
        </div>
        <Link to="/decouvrir" style={{ display: 'inline-flex', minHeight: 48, alignItems: 'center', gap: 10, marginTop: 28, padding: '0 20px', borderRadius: 3, background: 'var(--plume-gold)', color: 'var(--plume-night)', font: '600 13px Inter, sans-serif', textDecoration: 'none' }}>
          Trouver ma lecture <ArrowRight size={16} aria-hidden="true" />
        </Link>
      </main>
    </PsPageShell>
  );
}