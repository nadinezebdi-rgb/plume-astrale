"""Client Supabase admin (service_role) + helpers de requete."""
from functools import lru_cache
from supabase import create_client, Client
from config import get_settings


@lru_cache
def get_admin_client() -> Client:
    """Client Supabase avec service_role — bypass RLS. JAMAIS exposer au frontend."""
    s = get_settings()
    return create_client(s.SUPABASE_URL, s.SUPABASE_SERVICE_ROLE_KEY)
