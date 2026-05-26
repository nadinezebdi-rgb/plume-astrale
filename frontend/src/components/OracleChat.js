import React, { useState } from 'react';

const OracleChat = ({ userData }) => {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'bot', content: 'Bienvenue dans votre espace sacré. Posez-moi une question sur votre destin...' }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!message.trim()) return;

    const newHistory = [...chatHistory, { role: 'user', content: message }];
    setChatHistory(newHistory);
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/astro-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          user_data: userData // On envoie les infos de naissance (date, heure, lieu)
        }),
      });

      const data = await response.json();
      
      if (data.success) {
        setChatHistory([...newHistory, { role: 'bot', content: data.answer }]);
      } else {
        setChatHistory([...newHistory, { role: 'bot', content: "Les astres sont embrumés... Réessayez dans un instant." }]);
      }
    } catch (error) {
      console.error("Erreur Oracle:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>L'Oracle de Plume Astrale</h2>
      
      <div style={styles.chatBox}>
        {chatHistory.map((msg, index) => (
          <div key={index} style={msg.role === 'user' ? styles.userMsg : styles.botMsg}>
            <strong>{msg.role === 'user' ? 'Vous' : 'L\'Oracle'}:</strong>
            <p>{msg.content}</p>
          </div>
        ))}
        {isLoading && <p style={styles.loading}>L&#39;oracle consulte les étoiles...</p>}
      </div>

      <div style={styles.inputArea}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Votre question ici..."
          style={styles.input}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <button onClick={handleSendMessage} style={styles.button} disabled={isLoading}>
          Consulter
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: { maxWidth: '600px', margin: '20px auto', padding: '20px', backgroundColor: 'rgba(26, 11, 46, 0.9)', borderRadius: '15px', border: '1px solid #d4af37' },
  title: { color: '#d4af37', textAlign: 'center', fontFamily: 'serif' },
  chatBox: { height: '400px', overflowY: 'auto', marginBottom: '20px', padding: '10px', display: 'flex', flexDirection: 'column' },
  userMsg: { alignSelf: 'flex-end', backgroundColor: '#4a148c', color: 'white', padding: '10px', borderRadius: '10px', margin: '5px', maxWidth: '80% '},
  botMsg: { alignSelf: 'flex-start', backgroundColor: '#2e003e', color: '#e0e0e0', padding: '10px', borderRadius: '10px', margin: '5px', maxWidth: '80%', border: '1px solid #d4af37' },
  inputArea: { display: 'flex', gap: '10px' },
  input: { flex: 1, padding: '10px', borderRadius: '5px', border: 'none', backgroundColor: '#331a4d', color: 'white' },
  button: { padding: '10px 20px', backgroundColor: '#d4af37', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold' },
  loading: { fontStyle: 'italic', color: '#d4af37', fontSize: '0.9em' }
};

export default OracleChat;
