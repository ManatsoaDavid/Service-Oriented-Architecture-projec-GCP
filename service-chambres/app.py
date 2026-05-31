"""
SERVICE CHAMBRES — Python / Flask
Responsabilite : exposer et gerer la disponibilite des chambres
Port : 5001
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Donnees en memoire — modifiables via PATCH
CHAMBRES = [
    {
        "id": 1,
        "type": "Standard",
        "numero": "101",
        "tarif": 50000,
        "devise": "Ar",
        "disponible": True,
        "description": "Chambre confortable avec vue sur jardin",
        "articles": ["Gel douche", "Papier hygienique", "Pantoufle", "Brosse a dent"]
    },
    {
        "id": 2,
        "type": "Suite Senior",
        "numero": "201",
        "tarif": 120000,
        "devise": "Ar",
        "disponible": True,
        "description": "Suite spacieuse avec salon separe et terrasse",
        "articles": ["Gel douche", "Papier hygienique", "Pantoufle", "Brosse a dent"]
    },
    {
        "id": 3,
        "type": "Suite Prestige",
        "numero": "301",
        "tarif": 250000,
        "devise": "Ar",
        "disponible": False,
        "description": "Suite de luxe avec vue panoramique sur la ville",
        "articles": ["Gel douche", "Papier hygienique", "Pantoufle", "Brosse a dent"]
    },
    {
        "id": 4,
        "type": "Standard",
        "numero": "102",
        "tarif": 50000,
        "devise": "Ar",
        "disponible": True,
        "description": "Chambre standard cote piscine",
        "articles": ["Gel douche", "Papier hygienique", "Pantoufle", "Brosse a dent"]
    },
    {
        "id": 5,
        "type": "Suite Senior",
        "numero": "202",
        "tarif": 120000,
        "devise": "Ar",
        "disponible": True,
        "description": "Suite avec jacuzzi prive",
        "articles": ["Gel douche", "Papier hygienique", "Pantoufle", "Brosse a dent"]
    }
]


@app.route("/", methods=["GET"])
def info():
    return jsonify({
        "service": "Service Chambres",
        "version": "1.1.0",
        "langage": "Python 3 / Flask",
        "port": 5001,
        "endpoints": {
            "GET  /chambres":                     "Liste toutes les chambres",
            "GET  /chambres/<id>":                "Detail d'une chambre",
            "GET  /chambres/disponibles":         "Chambres disponibles uniquement",
            "PATCH /chambres/<id>/disponibilite": "Mettre a jour la disponibilite",
            "GET  /health":                       "Statut du service"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"statut": "ok", "service": "service-chambres"})


@app.route("/chambres", methods=["GET"])
def get_chambres():
    return jsonify({
        "service": "Service Chambres (Python/Flask)",
        "chambres": CHAMBRES,
        "total": len(CHAMBRES)
    })


@app.route("/chambres/disponibles", methods=["GET"])
def get_disponibles():
    disponibles = [c for c in CHAMBRES if c["disponible"]]
    return jsonify({
        "service": "Service Chambres (Python/Flask)",
        "chambres": disponibles,
        "total": len(disponibles)
    })


@app.route("/chambres/<int:chambre_id>", methods=["GET"])
def get_chambre(chambre_id):
    chambre = next((c for c in CHAMBRES if c["id"] == chambre_id), None)
    if not chambre:
        return jsonify({"erreur": f"Chambre {chambre_id} introuvable"}), 404
    return jsonify(chambre)


# ─── NOUVEAU : Mise a jour de la disponibilite ───────────────────────────────
# Appelee par le Service Reservation (Node.js) apres chaque reservation
# Demonstration de la communication service-a-service dans SOA
@app.route("/chambres/<int:chambre_id>/disponibilite", methods=["PATCH"])
def update_disponibilite(chambre_id):
    """
    Appele par le Service Reservation (Node.js) pour marquer
    une chambre comme occupee apres une reservation confirmee.
    Principe SOA : service-a-service communication.
    """
    chambre = next((c for c in CHAMBRES if c["id"] == chambre_id), None)
    if not chambre:
        return jsonify({"erreur": f"Chambre {chambre_id} introuvable"}), 404

    data = request.get_json()
    if data is None or "disponible" not in data:
        return jsonify({"erreur": "Le champ 'disponible' est requis (true/false)"}), 400

    ancien_statut = chambre["disponible"]
    chambre["disponible"] = bool(data["disponible"])

    return jsonify({
        "message": "Disponibilite mise a jour avec succes",
        "appele_par": "Service Reservation (Node.js/Express)",
        "chambre_id": chambre_id,
        "ancien_statut": "Disponible" if ancien_statut else "Occupee",
        "nouveau_statut": "Disponible" if chambre["disponible"] else "Occupee",
        "chambre": chambre
    })


if __name__ == "__main__":
    print("Service Chambres (Python/Flask) demarre sur le port 5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
