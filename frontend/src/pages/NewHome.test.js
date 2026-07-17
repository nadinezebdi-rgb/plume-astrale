/**
 * Tests pour la nouvelle page d'accueil NewHome
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import NewHome from './NewHome';
import { NEW_DESIGN_CONFIG } from '../config/newDesignConfig';

// Mock du composant EnhancedMoon3D
jest.mock('../components/EnhancedMoon3D', () => () => (
  <div data-testid="enhanced-moon-3d">Mocked Moon3D</div>
));

// Mock du contexte Auth
jest.mock('../context/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: false,
  }),
}));

describe('NewHome Component', () => {
  beforeEach(() => {
    // Mock localStorage
    Storage.prototype.getItem = jest.fn();
    Storage.prototype.setItem = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders correctly', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // Vérifier le bandeau d'urgence
    expect(screen.getByTestId('launch-banner')).toBeInTheDocument();
    expect(screen.getByText(/OFFRE DE LANCEMENT/)).toBeInTheDocument();
    expect(screen.getByText(/20 CRÉDITS OFFERTS/)).toBeInTheDocument();

    // Vérifier le logo
    expect(screen.getByTestId('hero-brand-logo')).toBeInTheDocument();
    expect(screen.getByText('PLUME ASTRALE')).toBeInTheDocument();

    // Vérifier le bouton Mon Compte
    expect(screen.getByTestId('hero-account-btn')).toBeInTheDocument();
    expect(screen.getByText('Mon Compte')).toBeInTheDocument();

    // Vérifier le titre principal
    expect(screen.getByTestId('hero-title')).toBeInTheDocument();
    expect(screen.getByText(/Qui est écrit/)).toBeInTheDocument();
    expect(screen.getByText(/dans vos étoiles/)).toBeInTheDocument();

    // Vérifier le sous-titre
    expect(screen.getByTestId('hero-subtitle')).toBeInTheDocument();
    expect(screen.getByText(/Trois étapes suffisent/)).toBeInTheDocument();

    // Vérifier l'indicateur d'étape
    expect(screen.getByTestId('step-progress')).toBeInTheDocument();

    // Vérifier le formulaire
    expect(screen.getByTestId('moon-form')).toBeInTheDocument();

    // Vérifier la lune 3D
    expect(screen.getByTestId('enhanced-moon-3d')).toBeInTheDocument();
  });

  test('displays step 1 form correctly', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // Vérifier l'étape 1
    expect(screen.getByText('Étape 1 · Indiquez votre jour de naissance')).toBeInTheDocument();
    
    // Vérifier les champs
    expect(screen.getByTestId('moon-day')).toBeInTheDocument();
    expect(screen.getByTestId('moon-month')).toBeInTheDocument();
    expect(screen.getByTestId('moon-year')).toBeInTheDocument();
    
    // Vérifier le bouton Continuer
    expect(screen.getByTestId('moon-next-1')).toBeInTheDocument();
    expect(screen.getByText('Continuer')).toBeInTheDocument();
  });

  test('navigates to step 2 when step 1 is complete', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // Remplir les champs de l'étape 1
    const dayInput = screen.getByTestId('moon-day');
    const monthSelect = screen.getByTestId('moon-month');
    const yearInput = screen.getByTestId('moon-year');
    const nextButton = screen.getByTestId('moon-next-1');

    fireEvent.change(dayInput, { target: { value: '15' } });
    fireEvent.change(monthSelect, { target: { value: '6' } });
    fireEvent.change(yearInput, { target: { value: '1990' } });
    fireEvent.click(nextButton);

    // Vérifier que nous sommes à l'étape 2
    expect(screen.getByText('Étape 2 · L\'heure exacte')).toBeInTheDocument();
    expect(screen.getByTestId('moon-hour')).toBeInTheDocument();
    expect(screen.getByTestId('moon-minute')).toBeInTheDocument();
  });

  test('navigates to step 3 when step 2 is complete', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // Remplir l'étape 1
    const dayInput = screen.getByTestId('moon-day');
    const monthSelect = screen.getByTestId('moon-month');
    const yearInput = screen.getByTestId('moon-year');
    const nextButton1 = screen.getByTestId('moon-next-1');

    fireEvent.change(dayInput, { target: { value: '15' } });
    fireEvent.change(monthSelect, { target: { value: '6' } });
    fireEvent.change(yearInput, { target: { value: '1990' } });
    fireEvent.click(nextButton1);

    // Remplir l'étape 2
    const hourInput = screen.getByTestId('moon-hour');
    const minuteInput = screen.getByTestId('moon-minute');
    const nextButton2 = screen.getByTestId('moon-next-2');

    fireEvent.change(hourInput, { target: { value: '14' } });
    fireEvent.change(minuteInput, { target: { value: '30' } });
    fireEvent.click(nextButton2);

    // Vérifier que nous sommes à l'étape 3
    expect(screen.getByText('Étape 3 · Votre lieu de naissance')).toBeInTheDocument();
    expect(screen.getByTestId('moon-place')).toBeInTheDocument();
    expect(screen.getByTestId('moon-submit-btn')).toBeInTheDocument();
  });

  test('shows back button on step 2 and 3', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // L'étape 1 ne devrait pas avoir de bouton retour
    expect(screen.queryByTestId('moon-back-btn')).not.toBeInTheDocument();

    // Aller à l'étape 2
    const dayInput = screen.getByTestId('moon-day');
    const monthSelect = screen.getByTestId('moon-month');
    const yearInput = screen.getByTestId('moon-year');
    const nextButton = screen.getByTestId('moon-next-1');

    fireEvent.change(dayInput, { target: { value: '15' } });
    fireEvent.change(monthSelect, { target: { value: '6' } });
    fireEvent.change(yearInput, { target: { value: '1990' } });
    fireEvent.click(nextButton);

    // L'étape 2 devrait avoir le bouton retour
    expect(screen.getByTestId('moon-back-btn')).toBeInTheDocument();
    expect(screen.getByText(/Étape précédente/)).toBeInTheDocument();
  });

  test('goes back to previous step when back button is clicked', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // Aller à l'étape 2
    const dayInput = screen.getByTestId('moon-day');
    const monthSelect = screen.getByTestId('moon-month');
    const yearInput = screen.getByTestId('moon-year');
    const nextButton = screen.getByTestId('moon-next-1');

    fireEvent.change(dayInput, { target: { value: '15' } });
    fireEvent.change(monthSelect, { target: { value: '6' } });
    fireEvent.change(yearInput, { target: { value: '1990' } });
    fireEvent.click(nextButton);

    // Retour à l'étape 1
    const backButton = screen.getByTestId('moon-back-btn');
    fireEvent.click(backButton);

    // Vérifier que nous sommes retournés à l'étape 1
    expect(screen.getByText('Étape 1 · Indiquez votre jour de naissance')).toBeInTheDocument();
  });

  test('disables next button when form is incomplete', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // Le bouton Continuer de l'étape 1 devrait être désactivé
    const nextButton = screen.getByTestId('moon-next-1');
    expect(nextButton).toBeDisabled();
  });

  test('enables next button when form is complete', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    // Remplir les champs
    const dayInput = screen.getByTestId('moon-day');
    const monthSelect = screen.getByTestId('moon-month');
    const yearInput = screen.getByTestId('moon-year');
    const nextButton = screen.getByTestId('moon-next-1');

    fireEvent.change(dayInput, { target: { value: '15' } });
    fireEvent.change(monthSelect, { target: { value: '6' } });
    fireEvent.change(yearInput, { target: { value: '1990' } });

    // Le bouton devrait être activé
    expect(nextButton).not.toBeDisabled();
  });

  test('has correct styling classes', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    const form = screen.getByTestId('moon-form');
    expect(form).toHaveStyle('backdrop-filter: blur(16px)');
    expect(form).toHaveStyle('border-radius: 28px');
  });

  test('displays Solena discovery button', () => {
    render(
      <MemoryRouter>
        <NewHome />
      </MemoryRouter>
    );

    expect(screen.getByTestId('discover-solena-btn')).toBeInTheDocument();
    expect(screen.getByText('Découvrir Solena')).toBeInTheDocument();
  });
});

describe('NEW_DESIGN_CONFIG', () => {
  test('has correct color palette', () => {
    expect(NEW_DESIGN_CONFIG.colors.background.primary).toBe('#000000');
    expect(NEW_DESIGN_CONFIG.colors.gold.primary).toBe('#E2BF65');
    expect(NEW_DESIGN_CONFIG.colors.gold.light).toBe('#F4D98C');
    expect(NEW_DESIGN_CONFIG.colors.gold.dark).toBe('#B8860B');
    expect(NEW_DESIGN_CONFIG.colors.aura.violet).toBe('#8B6FE6');
  });

  test('has correct typography', () => {
    expect(NEW_DESIGN_CONFIG.typography.fontFamily.serif).toContain('Cinzel');
    expect(NEW_DESIGN_CONFIG.typography.fontFamily.body).toContain('Inter');
  });

  test('has correct form steps', () => {
    expect(NEW_DESIGN_CONFIG.form.steps).toHaveLength(3);
    expect(NEW_DESIGN_CONFIG.form.steps[0].id).toBe(1);
    expect(NEW_DESIGN_CONFIG.form.steps[0].label).toContain('jour de naissance');
    expect(NEW_DESIGN_CONFIG.form.steps[1].id).toBe(2);
    expect(NEW_DESIGN_CONFIG.form.steps[1].label).toContain('heure exacte');
    expect(NEW_DESIGN_CONFIG.form.steps[2].id).toBe(3);
    expect(NEW_DESIGN_CONFIG.form.steps[2].label).toContain('lieu de naissance');
  });

  test('has correct moon3d configuration', () => {
    expect(NEW_DESIGN_CONFIG.moon3d.size.diameter).toBe(1.1);
    expect(NEW_DESIGN_CONFIG.moon3d.size.distance).toBe(5.5);
    expect(NEW_DESIGN_CONFIG.moon3d.rotation.mouseSensitivity).toBe(0.4);
  });
});
