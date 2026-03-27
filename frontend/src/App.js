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
      email: email || "Utilisateur",
      prenom: email?.split("@")[0] || "Utilisateur",
      dateNaissance: birthDate,
      heureNaissance: birthTime,
      lieuNaissance: birthPlace,
      pays: birthCountry,
    };

    // ✅ stockage clean
    localStorage.setItem("plume_astrale_data", JSON.stringify(user));
    localStorage.setItem("plume_astrale_paid", "false");
    localStorage.setItem("plume_astrale_plan", "free");

    console.log("USER CREATED :", user);

    // ✅ navigation OK
    navigate("/tarot");

  } catch (err) {
    console.error("ERREUR :", err);
    setError("Erreur lors de l'inscription");
  } finally {
    setLoading(false);
  }
};
