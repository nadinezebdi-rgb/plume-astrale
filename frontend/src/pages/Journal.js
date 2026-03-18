import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Journal = () => {
  const navigate = useNavigate();

  useEffect(() => {
    navigate('/mon-compte', { replace: true });
  }, [navigate]);

  return null;
};

export default Journal;
