/**
 * SERVICE RESERVATION — Node.js / Express
 * Responsabilite : gerer les reservations de chambres
 * Port : 5002
 *
 * NOUVEAU : Apres chaque reservation confirmee, ce service appelle
 * le Service Chambres (Python) pour mettre a jour la disponibilite.
 * Principe SOA : communication service-a-service.
 */

const express = require("express");
const cors    = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

// URL interne du service-chambres (reseau Docker)
const CHAMBRES_SERVICE_URL = process.env.CHAMBRES_SERVICE_URL || "http://service-chambres:5001";

// Stockage en memoire
const reservations = [];
let compteurId = 1;


// ─── Informations du service ───────────────────────────────────────────────
app.get("/", (req, res) => {
  res.json({
    service: "Service Reservation",
    version: "1.1.0",
    langage: "Node.js / Express",
    port: 5002,
    endpoints: {
      "GET  /reservations":     "Liste toutes les reservations",
      "POST /reservations":     "Creer une reservation + notifie service-chambres",
      "GET  /reservations/:id": "Detail d'une reservation",
      "GET  /health":           "Statut du service"
    }
  });
});


// ─── Sante du service ─────────────────────────────────────────────────────
app.get("/health", (req, res) => {
  res.json({ statut: "ok", service: "service-reservation" });
});


// ─── Lister toutes les reservations ───────────────────────────────────────
app.get("/reservations", (req, res) => {
  res.json({
    service: "Service Reservation (Node.js/Express)",
    reservations,
    total: reservations.length
  });
});


// ─── Detail d'une reservation ─────────────────────────────────────────────
app.get("/reservations/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const reservation = reservations.find(r => r.id === id);
  if (!reservation) {
    return res.status(404).json({ erreur: `Reservation ${id} introuvable` });
  }
  res.json(reservation);
});


// ─── Creer une reservation ────────────────────────────────────────────────
app.post("/reservations", async (req, res) => {
  const { nom_client, prenom_client, id_chambre, type_chambre, tarif, date_arrivee, date_depart } = req.body;

  // Validation
  if (!nom_client || !id_chambre || !date_arrivee || !date_depart) {
    return res.status(400).json({
      erreur: "Champs obligatoires manquants",
      requis: ["nom_client", "id_chambre", "date_arrivee", "date_depart"]
    });
  }

  // Creer la reservation
  const reservation = {
    id: compteurId++,
    numero_confirmation: `HTL-${Date.now()}`,
    nom_client,
    prenom_client: prenom_client || "",
    id_chambre,
    type_chambre: type_chambre || "Non specifie",
    tarif: tarif || 0,
    date_arrivee,
    date_depart,
    statut: "Confirmee",
    cree_le: new Date().toISOString()
  };

  reservations.push(reservation);

  // ─── COMMUNICATION SERVICE-A-SERVICE ─────────────────────────────────────
  // Node.js appelle Python pour marquer la chambre comme OCCUPEE
  // C'est le principe du couplage faible dans SOA :
  // chaque service fait sa specialite et communique via contrat REST
  let statut_mise_a_jour = "non_effectuee";
  try {
    const reponse = await fetch(
      `${CHAMBRES_SERVICE_URL}/chambres/${id_chambre}/disponibilite`,
      {
        method:  "PATCH",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ disponible: false })
      }
    );
    if (reponse.ok) {
      statut_mise_a_jour = "chambre_marquee_occupee";
      console.log(`[SOA] Service Chambres (Python) notifie : chambre ${id_chambre} → OCCUPEE`);
    }
  } catch (err) {
    console.error(`[SOA] Impossible de joindre service-chambres :`, err.message);
    statut_mise_a_jour = "erreur_notification";
  }

  res.status(201).json({
    service: "Service Reservation (Node.js/Express)",
    message: "Reservation confirmee avec succes",
    communication_soa: {
      action: "PATCH /chambres/" + id_chambre + "/disponibilite → service-chambres (Python)",
      statut: statut_mise_a_jour
    },
    reservation
  });
});


// ─── Demarrage ────────────────────────────────────────────────────────────
const PORT = 5002;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Service Reservation (Node.js/Express) demarre sur le port ${PORT}`);
  console.log(`Service Chambres URL : ${CHAMBRES_SERVICE_URL}`);
});
