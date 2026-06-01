"""
SERVICE CHAMBRES — Python / Flask
Responsabilite : exposer et gerer les chambres de l'hotel
Port : 5001

Routes :
  API REST  → /chambres, /chambres/<id>, etc.
  Interface → /admin  (page HTML pour ajouter/gerer les chambres)
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ─── Données en mémoire ───────────────────────────────────────────────────
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

prochain_id = 6  # compteur auto-increment

# ─── Template HTML de l'interface d'administration ───────────────────────
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Admin — Service Chambres (Python/Flask)</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; background: #0f0f0f; color: #e8e2d9; min-height: 100vh; }

  .header {
    background: #161616;
    border-bottom: 1px solid rgba(201,168,76,.25);
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .header h1 { font-size: 1.1rem; font-weight: 500; color: #C9A84C; }
  .badge {
    font-size: .7rem; font-weight: 500; letter-spacing: .12em;
    text-transform: uppercase; padding: .25rem .75rem;
    background: rgba(59,130,246,.15); color: #60a5fa;
    border: 1px solid rgba(59,130,246,.3); border-radius: 3px;
  }

  .container { max-width: 960px; margin: 0 auto; padding: 2rem; }

  .grid { display: grid; grid-template-columns: 1fr 1.4fr; gap: 1.5rem; align-items: start; }

  .panel {
    background: #161616;
    border: 1px solid rgba(201,168,76,.15);
    border-radius: 10px;
    padding: 1.5rem;
  }
  .panel h2 {
    font-size: .85rem; font-weight: 500; letter-spacing: .12em;
    text-transform: uppercase; color: #C9A84C;
    margin-bottom: 1.25rem; padding-bottom: .75rem;
    border-bottom: 1px solid rgba(201,168,76,.15);
  }

  .form-group { margin-bottom: 1rem; }
  .form-group label {
    display: block; font-size: .7rem; font-weight: 500;
    letter-spacing: .1em; text-transform: uppercase;
    color: #7a7060; margin-bottom: .35rem;
  }
  .form-group input, .form-group select, .form-group textarea {
    width: 100%; background: #1e1e1e;
    border: 1px solid rgba(201,168,76,.2); border-radius: 5px;
    padding: .6rem .8rem; color: #e8e2d9;
    font-family: system-ui, sans-serif; font-size: .85rem; outline: none;
    transition: border-color .2s;
  }
  .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
    border-color: rgba(201,168,76,.5);
  }
  .form-group textarea { resize: vertical; min-height: 70px; }
  .form-group select option { background: #1e1e1e; }

  .btn {
    width: 100%; padding: .7rem;
    background: linear-gradient(135deg, #C9A84C, #a8832a);
    border: none; border-radius: 5px;
    color: #0f0f0f; font-family: system-ui, sans-serif;
    font-size: .8rem; font-weight: 600;
    letter-spacing: .08em; text-transform: uppercase;
    cursor: pointer; transition: opacity .2s;
    margin-top: .5rem;
  }
  .btn:hover { opacity: .88; }

  .alert {
    padding: .75rem 1rem; border-radius: 5px;
    font-size: .82rem; margin-bottom: 1rem;
    display: none; line-height: 1.5;
  }
  .alert.ok  { background: rgba(34,197,94,.1);  color: #4ade80; border: 1px solid rgba(34,197,94,.3); display: block; }
  .alert.err { background: rgba(239,68,68,.1);  color: #f87171; border: 1px solid rgba(239,68,68,.3); display: block; }

  /* ── Table des chambres ── */
  .search-bar {
    width: 100%; background: #1e1e1e;
    border: 1px solid rgba(201,168,76,.2); border-radius: 5px;
    padding: .55rem .8rem; color: #e8e2d9;
    font-size: .82rem; outline: none; margin-bottom: 1rem;
    transition: border-color .2s;
  }
  .search-bar:focus { border-color: rgba(201,168,76,.4); }

  .chambre-item {
    background: #1e1e1e;
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 7px; padding: .9rem 1rem;
    margin-bottom: .6rem;
    display: flex; align-items: center;
    justify-content: space-between; gap: .75rem;
    transition: border-color .2s;
  }
  .chambre-item:hover { border-color: rgba(201,168,76,.25); }

  .chambre-info { flex: 1; min-width: 0; }
  .chambre-info .top {
    display: flex; align-items: center; gap: .5rem;
    margin-bottom: .25rem;
  }
  .chambre-info .num {
    font-size: 1rem; font-weight: 500; color: #C9A84C;
  }
  .chambre-info .type {
    font-size: .65rem; font-weight: 500; text-transform: uppercase;
    letter-spacing: .1em; color: #7a7060;
  }
  .chambre-info .desc {
    font-size: .75rem; color: #7a7060;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .chambre-info .tarif {
    font-size: .78rem; color: #e8e2d9; margin-top: .2rem; font-weight: 500;
  }

  .chambre-actions { display: flex; flex-direction: column; gap: .4rem; align-items: flex-end; }

  .badge-dispo {
    font-size: .65rem; font-weight: 500; padding: .2rem .55rem;
    border-radius: 3px; white-space: nowrap;
  }
  .badge-dispo.ok  { background: rgba(34,197,94,.12);  color: #4ade80; }
  .badge-dispo.non { background: rgba(239,68,68,.12);  color: #f87171; }

  .btn-small {
    font-size: .65rem; font-weight: 500; padding: .25rem .65rem;
    border: 1px solid; border-radius: 3px;
    cursor: pointer; background: transparent;
    transition: background .15s; white-space: nowrap;
  }
  .btn-suppr { border-color: rgba(239,68,68,.4); color: #f87171; }
  .btn-suppr:hover { background: rgba(239,68,68,.12); }

  .stats {
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: .75rem; margin-bottom: 1.5rem;
  }
  .stat {
    background: #161616; border: 1px solid rgba(201,168,76,.12);
    border-radius: 7px; padding: .75rem 1rem; text-align: center;
  }
  .stat .val { font-size: 1.5rem; font-weight: 500; color: #C9A84C; }
  .stat .lbl { font-size: .68rem; color: #7a7060; margin-top: .15rem;
    text-transform: uppercase; letter-spacing: .08em; }

  .empty { text-align: center; color: #7a7060; font-size: .82rem;
    padding: 1.5rem 0; font-style: italic; }

  .api-info {
    margin-top: 1.5rem; background: #1a1a1a;
    border: 1px solid rgba(201,168,76,.1); border-radius: 7px;
    padding: 1rem;
  }
  .api-info h3 { font-size: .72rem; font-weight: 500; letter-spacing: .1em;
    text-transform: uppercase; color: #7a7060; margin-bottom: .6rem; }
  .api-info code {
    display: block; font-size: .7rem; font-family: 'Courier New', monospace;
    color: #60a5fa; line-height: 1.8;
  }
</style>
</head>
<body>

<div class="header">
  <h1>Service Chambres — Interface d'administration</h1>
  <div class="badge">Python / Flask · Port 5001</div>
</div>

<div class="container">

  <!-- Stats -->
  <div class="stats" id="stats">
    <div class="stat"><div class="val" id="stat-total">—</div><div class="lbl">Total chambres</div></div>
    <div class="stat"><div class="val" id="stat-dispo" style="color:#4ade80">—</div><div class="lbl">Disponibles</div></div>
    <div class="stat"><div class="val" id="stat-occup" style="color:#f87171">—</div><div class="lbl">Occupées</div></div>
  </div>

  <div class="grid">

    <!-- ── Formulaire ajout ── -->
    <div class="panel">
      <h2>Ajouter une chambre</h2>

      <div class="alert" id="alert"></div>

      <div class="form-group">
        <label>Numéro de chambre *</label>
        <input type="text" id="f-numero" placeholder="ex: 103"/>
      </div>
      <div class="form-group">
        <label>Catégorie *</label>
        <select id="f-type">
          <option value="">-- Choisir --</option>
          <option value="Standard">Standard</option>
          <option value="Suite Senior">Suite Senior</option>
          <option value="Suite Prestige">Suite Prestige</option>
        </select>
      </div>
      <div class="form-group">
        <label>Tarif (Ar / nuit) *</label>
        <input type="number" id="f-tarif" placeholder="ex: 50000" min="0"/>
      </div>
      <div class="form-group">
        <label>Description</label>
        <textarea id="f-desc" placeholder="Description de la chambre..."></textarea>
      </div>
      <div class="form-group">
        <label>Disponible au départ</label>
        <select id="f-dispo">
          <option value="true">Oui — Disponible</option>
          <option value="false">Non — Occupée</option>
        </select>
      </div>

      <button class="btn" onclick="ajouterChambre()">+ Ajouter la chambre</button>

      <div class="api-info">
        <h3>Endpoint utilisé</h3>
        <code>POST http://localhost:5001/chambres</code>
        <code>Content-Type: application/json</code>
      </div>
    </div>

    <!-- ── Liste des chambres ── -->
    <div class="panel">
      <h2>Chambres enregistrées</h2>
      <input class="search-bar" type="text" id="search"
             placeholder="Rechercher par numéro, type..."
             oninput="filtrerChambres()"/>
      <div id="liste-chambres"><div class="empty">Chargement...</div></div>
    </div>

  </div>
</div>

<script>
let toutesChambres = [];

// ── Charger les chambres depuis l'API REST ──────────────────────────────
async function charger() {
  const r    = await fetch('/chambres');
  const data = await r.json();
  toutesChambres = data.chambres || [];
  mettreAJourStats(toutesChambres);
  afficherChambres(toutesChambres);
}

function mettreAJourStats(chambres) {
  const dispo = chambres.filter(c => c.disponible).length;
  document.getElementById('stat-total').textContent = chambres.length;
  document.getElementById('stat-dispo').textContent = dispo;
  document.getElementById('stat-occup').textContent = chambres.length - dispo;
}

function afficherChambres(chambres) {
  const el = document.getElementById('liste-chambres');
  if (!chambres.length) {
    el.innerHTML = '<div class="empty">Aucune chambre trouvée.</div>';
    return;
  }
  el.innerHTML = chambres.map(c => `
    <div class="chambre-item" id="item-${c.id}">
      <div class="chambre-info">
        <div class="top">
          <span class="num">N° ${c.numero}</span>
          <span class="type">${c.type}</span>
        </div>
        <div class="desc">${c.description}</div>
        <div class="tarif">${c.tarif.toLocaleString('fr')} Ar / nuit</div>
      </div>
      <div class="chambre-actions">
        <span class="badge-dispo ${c.disponible ? 'ok' : 'non'}">
          ${c.disponible ? 'Disponible' : 'Occupée'}
        </span>
        <button class="btn-small btn-suppr" onclick="supprimerChambre(${c.id})">
          Supprimer
        </button>
      </div>
    </div>
  `).join('');
}

function filtrerChambres() {
  const q = document.getElementById('search').value.toLowerCase();
  const filtrees = toutesChambres.filter(c =>
    c.numero.toLowerCase().includes(q) ||
    c.type.toLowerCase().includes(q) ||
    c.description.toLowerCase().includes(q)
  );
  afficherChambres(filtrees);
}

// ── Ajouter une chambre via POST /chambres ──────────────────────────────
async function ajouterChambre() {
  const numero = document.getElementById('f-numero').value.trim();
  const type   = document.getElementById('f-type').value;
  const tarif  = parseInt(document.getElementById('f-tarif').value);
  const desc   = document.getElementById('f-desc').value.trim();
  const dispo  = document.getElementById('f-dispo').value === 'true';
  const alertEl = document.getElementById('alert');

  alertEl.className = 'alert';

  if (!numero || !type || !tarif) {
    alertEl.className = 'alert err';
    alertEl.textContent = 'Veuillez remplir les champs obligatoires (numéro, catégorie, tarif).';
    return;
  }

  try {
    const r = await fetch('/chambres', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        numero, type, tarif,
        description: desc || `Chambre ${type} N°${numero}`,
        disponible: dispo
      })
    });
    const data = await r.json();

    if (!r.ok) {
      alertEl.className = 'alert err';
      alertEl.textContent = data.erreur || 'Erreur lors de l\'ajout.';
      return;
    }

    alertEl.className = 'alert ok';
    alertEl.textContent = `✓ Chambre N°${data.chambre.numero} ajoutée avec succès (ID: ${data.chambre.id})`;

    // Réinitialiser le formulaire
    document.getElementById('f-numero').value = '';
    document.getElementById('f-type').value   = '';
    document.getElementById('f-tarif').value  = '';
    document.getElementById('f-desc').value   = '';

    await charger();

    setTimeout(() => { alertEl.className = 'alert'; }, 4000);

  } catch (e) {
    alertEl.className = 'alert err';
    alertEl.textContent = 'Erreur réseau : impossible de joindre le service.';
  }
}

// ── Supprimer une chambre via DELETE /chambres/<id> ─────────────────────
async function supprimerChambre(id) {
  const chambre = toutesChambres.find(c => c.id === id);
  if (!confirm(`Supprimer la chambre N°${chambre?.numero} ?`)) return;

  const r = await fetch(`/chambres/${id}`, { method: 'DELETE' });
  if (r.ok) {
    await charger();
  }
}

charger();
</script>
</body>
</html>
"""


# ══════════════════════════════════════════════════════════════════════════════
# API REST ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/", methods=["GET"])
def info():
    return jsonify({
        "service": "Service Chambres",
        "version": "1.2.0",
        "langage": "Python 3 / Flask",
        "port": 5001,
        "endpoints": {
            "GET  /admin":                        "Interface HTML d'administration",
            "GET  /chambres":                     "Liste toutes les chambres",
            "POST /chambres":                     "Ajouter une nouvelle chambre",
            "GET  /chambres/<id>":                "Detail d'une chambre",
            "GET  /chambres/disponibles":         "Chambres disponibles uniquement",
            "PATCH /chambres/<id>/disponibilite": "Mettre a jour la disponibilite",
            "DELETE /chambres/<id>":              "Supprimer une chambre",
            "GET  /health":                       "Statut du service"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"statut": "ok", "service": "service-chambres"})


# ── Interface d'administration HTML ──────────────────────────────────────────
@app.route("/admin", methods=["GET"])
def admin():
    """Interface HTML pour gérer les chambres (ajout, suppression, liste)"""
    return render_template_string(ADMIN_HTML)


# ── Lister toutes les chambres ────────────────────────────────────────────────
@app.route("/chambres", methods=["GET"])
def get_chambres():
    return jsonify({
        "service": "Service Chambres (Python/Flask)",
        "chambres": CHAMBRES,
        "total": len(CHAMBRES)
    })


# ── Chambres disponibles uniquement ──────────────────────────────────────────
@app.route("/chambres/disponibles", methods=["GET"])
def get_disponibles():
    disponibles = [c for c in CHAMBRES if c["disponible"]]
    return jsonify({
        "service": "Service Chambres (Python/Flask)",
        "chambres": disponibles,
        "total": len(disponibles)
    })


# ── Détail d'une chambre ──────────────────────────────────────────────────────
@app.route("/chambres/<int:chambre_id>", methods=["GET"])
def get_chambre(chambre_id):
    chambre = next((c for c in CHAMBRES if c["id"] == chambre_id), None)
    if not chambre:
        return jsonify({"erreur": f"Chambre {chambre_id} introuvable"}), 404
    return jsonify(chambre)


# ── Ajouter une nouvelle chambre ──────────────────────────────────────────────
@app.route("/chambres", methods=["POST"])
def ajouter_chambre():
    """Ajoute une nouvelle chambre — appelé depuis l'interface /admin"""
    global prochain_id
    data = request.get_json()

    if not data:
        return jsonify({"erreur": "Body JSON requis"}), 400

    numero = data.get("numero", "").strip()
    type_c = data.get("type", "").strip()
    tarif  = data.get("tarif")

    if not numero or not type_c or tarif is None:
        return jsonify({
            "erreur": "Champs obligatoires manquants",
            "requis": ["numero", "type", "tarif"]
        }), 400

    if type_c not in ["Standard", "Suite Senior", "Suite Prestige"]:
        return jsonify({
            "erreur": "Type invalide",
            "valeurs_acceptees": ["Standard", "Suite Senior", "Suite Prestige"]
        }), 400

    # Vérifier doublon de numéro
    if any(c["numero"] == numero for c in CHAMBRES):
        return jsonify({"erreur": f"Le numéro de chambre '{numero}' existe déjà"}), 409

    nouvelle_chambre = {
        "id":          prochain_id,
        "type":        type_c,
        "numero":      numero,
        "tarif":       int(tarif),
        "devise":      "Ar",
        "disponible":  bool(data.get("disponible", True)),
        "description": data.get("description", f"Chambre {type_c} N°{numero}"),
        "articles":    ["Gel douche", "Papier hygienique", "Pantoufle", "Brosse a dent"]
    }

    CHAMBRES.append(nouvelle_chambre)
    prochain_id += 1

    return jsonify({
        "message": "Chambre ajoutee avec succes",
        "chambre": nouvelle_chambre
    }), 201


# ── Mettre à jour la disponibilité (appelé par Node.js) ──────────────────────
@app.route("/chambres/<int:chambre_id>/disponibilite", methods=["PATCH"])
def update_disponibilite(chambre_id):
    chambre = next((c for c in CHAMBRES if c["id"] == chambre_id), None)
    if not chambre:
        return jsonify({"erreur": f"Chambre {chambre_id} introuvable"}), 404

    data = request.get_json()
    if data is None or "disponible" not in data:
        return jsonify({"erreur": "Le champ 'disponible' est requis"}), 400

    ancien = chambre["disponible"]
    chambre["disponible"] = bool(data["disponible"])

    return jsonify({
        "message":        "Disponibilite mise a jour",
        "appele_par":     "Service Reservation (Node.js/Express)",
        "chambre_id":     chambre_id,
        "ancien_statut":  "Disponible" if ancien else "Occupee",
        "nouveau_statut": "Disponible" if chambre["disponible"] else "Occupee",
        "chambre":        chambre
    })


# ── Supprimer une chambre ─────────────────────────────────────────────────────
@app.route("/chambres/<int:chambre_id>", methods=["DELETE"])
def supprimer_chambre(chambre_id):
    chambre = next((c for c in CHAMBRES if c["id"] == chambre_id), None)
    if not chambre:
        return jsonify({"erreur": f"Chambre {chambre_id} introuvable"}), 404
    CHAMBRES.remove(chambre)
    return jsonify({
        "message":    f"Chambre {chambre_id} supprimee avec succes",
        "chambre_id": chambre_id
    })


if __name__ == "__main__":
    print("Service Chambres (Python/Flask) demarre sur le port 5001")
    print("Interface admin : http://localhost:5001/admin")
    app.run(host="0.0.0.0", port=5001, debug=False)