import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { CheckCircle, Shield, CreditCard, ArrowLeft, Sparkles, Star, Heart, Eye, Download, Mail } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface UserData {
  prenom: string;
  dateNaissance: string;
  heureNaissance: string;
  ville: string;
  pays: string;
  email: string;
}

const Paiement = () => {
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserData | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    const data = localStorage.getItem('numerologie_data');
    if (!data) {
      navigate('/formulaire');
      return;
    }
    setUserData(JSON.parse(data));
  }, [navigate]);

  const handlePayment = async () => {
    if (!userData) return;
    
    setIsProcessing(true);
    
    try {
      // Simuler le processus de paiement Stripe
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Marquer comme payé
      localStorage.setItem('numerologie_paid', 'true');
      localStorage.setItem('numerologie_payment_date', new Date().toISOString());
      
      // Rediriger vers les résultats
      navigate('/resultats');
    } catch (error) {
      console.error('Erreur de paiement:', error);
      setIsProcessing(false);
    }
  };

  if (!userData) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/apercu')}
            className="mb-6 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Retour à l'aperçu
          </Button>
          
          <h1 className="text-4xl md:text-5xl font-bold mb-6 mystical-text">
            Déverrouillez Votre Destinée
          </h1>
          <p className="text-xl text-foreground/70 mb-8">
            Accédez à votre analyse complète et personnalisée
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12">
          {/* Récapitulatif de la commande */}
          <div>
            <Card className="mystical-card mb-8">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center gap-2">
                  <Sparkles className="w-6 h-6 text-accent" />
                  Étude Numérologie Complète
                </CardTitle>
                <CardDescription>
                  Analyse personnalisée basée sur vos données de naissance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Calcul précis de votre chemin de vie</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Analyse de votre année personnelle 2024</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Calcul astronomique de votre ascendant</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Lecture d'âme intuitive et symbolique</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Conseils d'alignement personnalisés</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Rapport PDF premium téléchargeable</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500" />
                    <span>Envoi sécurisé par email</span>
                  </div>
                </div>
                
                <Separator className="my-6" />
                
                <div className="flex justify-between items-center text-2xl font-bold">
                  <span>Total</span>
                  <span className="text-accent">19,90€</span>
                </div>
                
                <p className="text-sm text-muted-foreground mt-2">
                  Paiement unique • Accès immédiat • Garantie 30 jours
                </p>
              </CardContent>
            </Card>

            {/* Informations de sécurité */}
            <Card className="mystical-card">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="w-6 h-6 text-green-500" />
                  <span className="font-semibold">Paiement 100% Sécurisé</span>
                </div>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span>Chiffrement SSL 256 bits</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span>Traitement sécurisé par Stripe</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span>Aucune donnée bancaire stockée</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span>Conforme RGPD</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Formulaire de paiement */}
          <div>
            <Card className="mystical-card">
              <CardHeader>
                <CardTitle className="text-2xl flex items-center gap-2">
                  <CreditCard className="w-6 h-6 text-primary" />
                  Finaliser Votre Commande
                </CardTitle>
                <CardDescription>
                  Paiement sécurisé en un clic
                </CardDescription>
              </CardHeader>
              <CardContent>
                {/* Informations client */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-3">Vos informations</h3>
                  <div className="bg-muted/30 p-4 rounded-lg space-y-2 text-sm">
                    {userData.prenom && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Prénom :</span>
                        <span>{userData.prenom}</span>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Email :</span>
                      <span>{userData.email}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Date de naissance :</span>
                      <span>{new Date(userData.dateNaissance).toLocaleDateString('fr-FR')}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Lieu :</span>
                      <span>{userData.ville}, {userData.pays}</span>
                    </div>
                  </div>
                </div>

                <Separator className="mb-6" />

                {/* Bouton de paiement */}
                <div className="space-y-4">
                  <Button
                    onClick={handlePayment}
                    disabled={isProcessing}
                    className="golden-button w-full text-lg py-4"
                    size="lg"
                  >
                    {isProcessing ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-current mr-2" />
                        Traitement en cours...
                      </>
                    ) : (
                      <>
                        <CreditCard className="w-5 h-5 mr-2" />
                        Payer 19,90€ - Accès Immédiat
                      </>
                    )}
                  </Button>
                  
                  <p className="text-center text-xs text-muted-foreground">
                    En procédant au paiement, vous acceptez nos 
                    <button className="underline hover:text-foreground mx-1">conditions générales</button>
                    et notre 
                    <button className="underline hover:text-foreground mx-1">politique de confidentialité</button>
                  </p>
                </div>

                {/* Garantie */}
                <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
                  <div className="flex items-center gap-2 text-green-600 font-semibold mb-2">
                    <Shield className="w-5 h-5" />
                    Garantie Satisfait ou Remboursé
                  </div>
                  <p className="text-sm text-green-600/80">
                    Si vous n'êtes pas entièrement satisfait de votre étude, 
                    nous vous remboursons intégralement sous 30 jours.
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Ce que vous recevrez */}
            <Card className="mystical-card mt-6">
              <CardHeader>
                <CardTitle className="text-xl">Après Votre Paiement</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold">1</div>
                    <span>Accès immédiat à votre étude complète</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold">2</div>
                    <span>Génération automatique de votre PDF premium</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-semibold">3</div>
                    <span>Envoi sécurisé par email avec lien d'accès</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Paiement;