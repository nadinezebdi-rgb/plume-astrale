import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Calendar, MapPin, Clock, Mail, Sparkles, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface FormData {
  prenom: string;
  dateNaissance: string;
  heureNaissance: string;
  ville: string;
  pays: string;
  email: string;
}

const Formulaire = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    prenom: '',
    dateNaissance: '',
    heureNaissance: '',
    ville: '',
    pays: '',
    email: ''
  });
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<FormData> = {};

    if (!formData.dateNaissance) {
      newErrors.dateNaissance = 'La date de naissance est requise';
    }

    if (!formData.heureNaissance) {
      newErrors.heureNaissance = 'L\'heure de naissance est requise';
    }

    if (!formData.ville) {
      newErrors.ville = 'La ville de naissance est requise';
    }

    if (!formData.pays) {
      newErrors.pays = 'Le pays de naissance est requis';
    }

    if (!formData.email) {
      newErrors.email = 'L\'email est requis';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Format d\'email invalide';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsSubmitting(true);
    
    // Simuler le traitement
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Stocker les données pour l'aperçu
    localStorage.setItem('numerologie_data', JSON.stringify(formData));
    
    setIsSubmitting(false);
    navigate('/apercu');
  };

  return (
    <div className="min-h-screen py-12 px-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold mb-6 mystical-text">
            Révélez Votre Destinée
          </h1>
          <p className="text-xl text-foreground/70 mb-8">
            Partagez vos informations de naissance pour une analyse personnalisée précise
          </p>
          
          <div className="flex justify-center items-center gap-4 text-sm text-foreground/60">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary-glow font-semibold">1</div>
              <span>Informations</span>
            </div>
            <ArrowRight className="w-4 h-4" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground font-semibold">2</div>
              <span>Aperçu</span>
            </div>
            <ArrowRight className="w-4 h-4" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-muted-foreground font-semibold">3</div>
              <span>Étude complète</span>
            </div>
          </div>
        </div>

        {/* Formulaire */}
        <Card className="mystical-card">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl flex items-center justify-center gap-2">
              <Sparkles className="w-6 h-6 text-accent" />
              Vos Informations Cosmiques
            </CardTitle>
            <CardDescription>
              Toutes les informations sont sécurisées et utilisées uniquement pour votre analyse
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Informations personnelles */}
              <div className="space-y-6">
                <div className="flex items-center gap-2 text-lg font-semibold text-primary-glow">
                  <Mail className="w-5 h-5" />
                  Informations Personnelles
                </div>
                
                <div className="grid gap-4">
                  <div>
                    <Label htmlFor="prenom" className="text-foreground/80">
                      Prénom (optionnel)
                    </Label>
                    <Input
                      id="prenom"
                      type="text"
                      value={formData.prenom}
                      onChange={(e) => handleInputChange('prenom', e.target.value)}
                      placeholder="Votre prénom"
                      className="sacred-border"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="email" className="text-foreground/80">
                      Email *
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      value={formData.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      placeholder="votre@email.com"
                      className={`sacred-border ${errors.email ? 'border-destructive' : ''}`}
                      required
                    />
                    {errors.email && (
                      <p className="text-sm text-destructive mt-1">{errors.email}</p>
                    )}
                  </div>
                </div>
              </div>

              <Separator className="bg-border/50" />

              {/* Informations de naissance */}
              <div className="space-y-6">
                <div className="flex items-center gap-2 text-lg font-semibold text-primary-glow">
                  <Calendar className="w-5 h-5" />
                  Informations de Naissance
                </div>
                
                <div className="grid gap-4">
                  <div>
                    <Label htmlFor="dateNaissance" className="text-foreground/80">
                      Date de naissance *
                    </Label>
                    <Input
                      id="dateNaissance"
                      type="date"
                      value={formData.dateNaissance}
                      onChange={(e) => handleInputChange('dateNaissance', e.target.value)}
                      className={`sacred-border ${errors.dateNaissance ? 'border-destructive' : ''}`}
                      required
                    />
                    {errors.dateNaissance && (
                      <p className="text-sm text-destructive mt-1">{errors.dateNaissance}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="heureNaissance" className="text-foreground/80">
                      Heure de naissance *
                    </Label>
                    <div className="relative">
                      <Clock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                      <Input
                        id="heureNaissance"
                        type="time"
                        value={formData.heureNaissance}
                        onChange={(e) => handleInputChange('heureNaissance', e.target.value)}
                        className={`sacred-border pl-10 ${errors.heureNaissance ? 'border-destructive' : ''}`}
                        required
                      />
                    </div>
                    {errors.heureNaissance && (
                      <p className="text-sm text-destructive mt-1">{errors.heureNaissance}</p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      L'heure exacte est essentielle pour le calcul de votre ascendant
                    </p>
                  </div>
                </div>
              </div>

              <Separator className="bg-border/50" />

              {/* Lieu de naissance */}
              <div className="space-y-6">
                <div className="flex items-center gap-2 text-lg font-semibold text-primary-glow">
                  <MapPin className="w-5 h-5" />
                  Lieu de Naissance
                </div>
                
                <div className="grid gap-4">
                  <div>
                    <Label htmlFor="ville" className="text-foreground/80">
                      Ville de naissance *
                    </Label>
                    <Input
                      id="ville"
                      type="text"
                      value={formData.ville}
                      onChange={(e) => handleInputChange('ville', e.target.value)}
                      placeholder="Paris, Lyon, Marseille..."
                      className={`sacred-border ${errors.ville ? 'border-destructive' : ''}`}
                      required
                    />
                    {errors.ville && (
                      <p className="text-sm text-destructive mt-1">{errors.ville}</p>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="pays" className="text-foreground/80">
                      Pays de naissance *
                    </Label>
                    <Input
                      id="pays"
                      type="text"
                      value={formData.pays}
                      onChange={(e) => handleInputChange('pays', e.target.value)}
                      placeholder="France, Belgique, Suisse..."
                      className={`sacred-border ${errors.pays ? 'border-destructive' : ''}`}
                      required
                    />
                    {errors.pays && (
                      <p className="text-sm text-destructive mt-1">{errors.pays}</p>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      Nécessaire pour les calculs astronomiques précis
                    </p>
                  </div>
                </div>
              </div>

              {/* Bouton de soumission */}
              <div className="pt-6">
                <Button
                  type="submit"
                  disabled={isSubmitting}
                  className="golden-button w-full text-lg py-4"
                  size="lg"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-current mr-2" />
                      Calcul en cours...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      Générer Mon Aperçu Gratuit
                    </>
                  )}
                </Button>
                
                <p className="text-center text-sm text-muted-foreground mt-4">
                  En continuant, vous acceptez nos conditions d'utilisation et notre politique de confidentialité
                </p>
              </div>
            </form>
          </CardContent>
        </Card>

        {/* Sécurité */}
        <div className="mt-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-card/50 rounded-lg border border-border/30">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-sm text-foreground/70">Connexion sécurisée SSL</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Formulaire;