import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import SEO from '../components/SEO';

/* ─── Background étoiles ─── */
const CosmicBg = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    resize();
    window.addEventListener('resize', resize);

    let stars = Array.from({ length: 150 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: Math.random() * 2,
      speed: Math.random() * 0.3,
    }));

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      stars.forEach(s => {
        s.y += s.speed;
        if (s.y > canvas.height) s.y = 0;

        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255,255,255,0.6)';
        ctx.fill();
      });

      requestAnimationFrame(draw);
    };

    draw();
  }, []);

  return <canvas ref={canvasRef} className="fixed inset-0 z-0" />;
};

const Index = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [question, setQuestion] = useState('');

  return (
    <div className="relative min-h-screen flex items-center justify-center text-center px-6"
      style={{
        background: 'linear-gradient(180deg, #1E1B4B, #0F172A)'
      }}
    >

      <SEO path="/" />
      <CosmicBg />

      {/* Aura mystique */}
      <div className="absolute w-[500px] h-[500px] rounded-full blur-3xl opacity-30"
        style={{
          background: 'radial-gradient(circle, rgba(232,121,249,0.4), transparent)'
        }}
      />

      <div className="relative z-10 max-w-xl w-full">

        <p className="text-xs uppercase tracking-[0.3em] mb-4 text-pink-400">
          Oracle Personnel
        </p>

        <h1 className="text-4xl md:text-6xl mb-6 text-white"
          style={{ fontFamily: 'Cinzel, serif' }}>
          Pose ta question<br />à ton Oracle
        </h1>

        <p className="mb-8 text-lg text-gray-300">
          Une réponse claire pour ce qui te traverse en ce moment.
        </p>

        {/* INPUT */}
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ex : Vais-je prendre la bonne décision ?"
          className="w-full px-6 py-4 rounded-full text-center mb-6"
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(232,121,249,0.3)',
            color: '#fff'
          }}
        />

        {/* CTA */}
        <button
          onClick={() => navigate('/oracle')}
          className="px-8 py-4 rounded-full font-semibold transition hover:scale-105 flex items-center justify-center gap-2 w-full"
          style={{
            background: 'linear-gradient(135deg, #F4C542, #E879F9)',
            color: '#0F172A'
          }}
        >
          <Sparkles size={16} />
          Consulter mon Oracle
        </button>

        <p className="text-xs mt-6 text-gray-400">
          +2 000 consultations réalisées
        </p>

      </div>
    </div>
  );
};

export default Index;
