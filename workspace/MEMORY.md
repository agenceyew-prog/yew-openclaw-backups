# Récapitulatif des configurations et décisions importantes (auto-généré)

## 2026-03-12

### Initialisation & Identité
*   **Nom:** Léa, Assistante IA pour l'agence Yew (www.agenceyew.fr).
*   **Vibe:** Directe et concise en interne (Michael & Guillaume), polie et adaptable en externe.
*   **Objectif:** Aider à la production de solutions techniques et créatives de haut niveau.

### Skills Installés
*   `self-improving-agent` (pskoett) : Pour l'apprentissage continu et la documentation des erreurs/améliorations.
*   `api-gateway` (byungkyu) : Connecté à Maton via `MATON_API_KEY`.
*   `agent-browser-clawdbot` (MaTriXy) : Pour le contrôle du navigateur.
*   `find-skills` (JimLiuxinghai) : Pour la recherche de skills ClawHub.
*   `proactive-agent` (halthelobster) : Pour une autonomie accrue et des initiatives.

### Configuration Telegram
*   **Bot Token:** `8755473082:AAHD1ICvFTMMtV0BCSkiaxX7t4r22FhZRiA` (masqué dans la config).
*   **DM Policy:** `allowlist` pour `6163128980` (Michael/Mikha).
*   **Group Policy:** `open` pour tous les groupes (`groupAllowFrom: ["*"]`).
*   **Notifications:** Actives pour les messages importants (ex: sauvegardes).

### Sauvegardes Automatiques Récurrentes
*   **Scope:** `/data/.openclaw/` (inclut configuration, workspace, skills, .learnings, .env).
*   **Destination:** `/data/openclaw_backups/` (répertoire dans le volume Docker persistant `/docker/openclaw-px9u/data` de l'hôte).
*   **Méthode:** Script `backup_script.sh` (`bash`) qui utilise `tar -czf`.
    *   **Améliorations:** `flock` (anti-concurrence), `umask 077`, `mkdir -p` et `chmod 700` sur le répertoire de destination, vérification d'intégrité (`tar -tzf >/dev/null`), `chmod 600` sur les archives.
    *   **Rétention:** Conserve les 7 derniers jours (`find -mtime +7 -delete`).
*   **Fréquence:** Trois tâches Cron (via API Gateway) à 12h00, 22h00, 23h59 (Europe/Paris).
*   **Limitation connue:** Sauvegardes sur le même volume que la source (risque en cas de corruption/perte du volume entier). Réplication externe recommandée pour une résilience complète.
