import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { UserPlus, Eye, EyeOff, ChevronRight, ChevronLeft } from 'lucide-react';

const COUNTRIES = [
  'France', 'Belgique', 'Suisse', 'Canada', 'Luxembourg', 'Monaco',
  'Algérie', 'Maroc', 'Tunisie', 'Sénégal', 'Côte d\'Ivoire',
  'États-Unis', 'Royaume-Uni', 'Allemagne', 'Espagne', 'Italie', 'Portugal', 'Autre',
];

export default function Register() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1);
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [birthDate, setBirthDate] = useState('');
  const [birthHour, setBirthHour] = useState('');
  const [birthMinute, setBirthMinute] = useState('');
  const [birthPlace, setBirthPlace] = useState('');
  const [birthCountry, setBirthCountry] = useState('France');

  const goStep2 = () => {
    if (!email || !password) {
      setError('Veuillez remplir tous les champs');
      return;
    }
    if (password.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }
    setError('');
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!birthDate || !birthPlace) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const h = (birthHour || "00").padStart(2, '0');
      const m = (birthMinute || "00").padStart(2, '0');
      const birthTime = `${h}:${m}`;

      const user = {
        email,
        birth_date: birthDate,
        birth_time: birthTime,
        birth_place: birthPlace,
        birth_country: birthCountry,
      };

      // 🔥 STOCKAGE LOCAL
      localStorage.setItem("plume_astrale_data", JSON.stringify(user));
      localStorage.setItem("plume_astrale_paid", "false");
      localStorage.setItem("plume_astrale_plan", "free");

      console.log("USER CREATED :", user);

      navigate("/tirage");

    } catch (err) {
      console.error("ERREUR :", err);
      setError("Erreur lors de l'inscription");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20 pb-12">
      <div className="w-full max-w-md">

        <div className="rounded-2xl p-8">

          <h1 className="text-2xl text-center mb-4">Créer un compte</h1>

          {error && (
            <div className="mb-4 text-red-400 text-center">
              {error}
            </div>
          )}

          {step === 1 ? (
            <div className="space-y-4">

              <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full border-b p-2"
              />

              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  placeholder="Mot de passe"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full border-b p-2"
                />
                <button onClick={() => setShowPw(!showPw)} type="button">
                  {showPw ? <EyeOff /> : <Eye />}
                </button>
              </div>

              <button onClick={goStep2}>
                Continuer
              </button>

            </div>
          ) : (

            <form onSubmit={handleSubmit} className="space-y-4">

              <input
                type="date"
                value={birthDate}
                onChange={e => setBirthDate(e.target.value)}
              />

              <input
                type="number"
                placeholder="Heure"
                value={birthHour}
                onChange={e => setBirthHour(e.target.value)}
              />

              <input
                type="number"
                placeholder="Minute"
                value={birthMinute}
                onChange={e => setBirthMinute(e.target.value)}
              />

              <input
                type="text"
                placeholder="Lieu de naissance"
                value={birthPlace}
                onChange={e => setBirthPlace(e.target.value)}
              />

              <select
                value={birthCountry}
                onChange={e => setBirthCountry(e.target.value)}
              >
                {COUNTRIES.map(c => <option key={c}>{c}</option>)}
              </select>

              <div className="flex gap-2">
                <button type="button" onClick={() => setStep(1)}>
                  Retour
                </button>

                <button type="submit" disabled={loading}>
                  {loading ? "Création..." : "Créer mon compte"}
                </button>
              </div>

            </form>
          )}

          <p className="text-center mt-4">
            Déjà un compte ? <Link to="/connexion">Se connecter</Link>
          </p>

        </div>
      </div>
    </div>
  );
}
