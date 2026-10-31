# Fonctions utilitaires

def has_valid_search_inputs(form):
    """
    Valide que les inputs respectent les règles métier:
    - SOIT un ID réclamation
    - SOIT date + heure + coordonnées
    """
    has_claim_id = form.id_reclamation.data is not None and form.id_reclamation.data.strip() != ''
    has_date = form.date.data is not None
    has_time = form.heure.data is not None
    has_coordinates = form.lat.data is not None and form.long.data is not None

    # Une des deux conditions doit être vraie
    id_only = has_claim_id and not (has_date or has_time or has_coordinates)
    date_time_and_coordinates = (has_date and has_time and has_coordinates) and not has_claim_id
    all_fields = has_claim_id and has_date and has_time and has_coordinates

    return id_only or date_time_and_coordinates or all_fields


def build_search_payload(form):
    """Construit le payload de recherche avec les données du formulaire"""
    search_date = form.date.data.strftime("%Y-%m-%d") if form.date.data else None
    search_time = form.heure.data.strftime("%H:%M") if form.heure.data else None

    payload = {
        "id_reclamation": form.id_reclamation.data if form.id_reclamation.data else None,
        "date": search_date,
        "heure": search_time,
        "latitude": form.lat.data,
        "longitude": form.long.data
    }

    return payload
    # # Nettoyer les None du payload
    # return {k: v for k, v in payload.items() if v is not None}
    #
