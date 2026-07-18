import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Simple redirect component that navigates to a new URL
 * Useful for maintaining backward compatibility with old routes
 */
export default function Redirect({ to }) {
  const navigate = useNavigate();
  
  useEffect(() => {
    navigate(to, { replace: true });
  }, [to, navigate]);
  
  return null;
}
