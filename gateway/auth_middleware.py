"""Middleware d'authentification et d'autorisation"""

from fastapi import HTTPException, Header
from typing import Optional

# Simulation de vérification de token (à remplacer par JWT)
def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """Vérifier le token d'authentification"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    # Simulation - En production, décoder le JWT ici
    # Pour l'instant, on accepte un format simple: "Bearer role:username"
    try:
        token = authorization.replace("Bearer ", "")
        parts = token.split(":")
        if len(parts) == 2:
            role, username = parts
            return {"username": username, "role": role}
    except:
        pass
    
    raise HTTPException(status_code=401, detail="Token invalide")

def require_admin(user: dict) -> dict:
    """Vérifier que l'utilisateur est admin"""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Accès refusé. Rôle admin requis."
        )
    return user

def require_auth(user: dict) -> dict:
    """Vérifier que l'utilisateur est authentifié (admin ou technicien)"""
    if user.get("role") not in ["admin", "technicien", "operator"]:
        raise HTTPException(
            status_code=403,
            detail="Accès refusé. Authentification requise."
        )
    return user
