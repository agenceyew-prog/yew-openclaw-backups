### Configuration des Tâches Cron

*   **Tâche :** Veille opportunités Yew (Matin, Après-midi, Fin de journée) - Approche autonome via Sous-agents
    *   **Description :** Orchestration par l'agent principal d'un workflow de veille multicouche utilisant des sous-agents spécialisés pour une exécution autonome et optimisée.
        1.  **Sous-agent "Générateur de Cibles" (Modèle : `google/gemini-2.5-flash`) :** Exécute `scripts/prospect_veille.py` (`generate_search_targets`) pour obtenir les requêtes de recherche web initiales.
        2.  **Sous-agent "Chercheur Web" (Modèle : `google/gemini-2.5-flash`) :** Exécute les requêtes `web_search` et collecte les résultats bruts.
        3.  **Sous-agent "Filtreur d'URLs" (Modèle : `google/gemini-2.5-flash`) :** Exécute `scripts/prospect_veille.py` (`filter_urls_for_agent_browser`) pour affiner les résultats du Chercheur Web. Il utilise une logique de **Liste Noire** pour exclure les annuaires et réseaux sociaux (Wikipedia, Facebook, Eventbrite...) et ne garder que les sites d'organisateurs ou d'agences potentiellement pertinents.
        4.  **Sous-agent "Explorateur de Pages" (Modèle : `google/gemini-2.5-pro`) :** Utilise `agent-browser` pour naviguer sur les URLs filtrées. Il lit le contenu du site avec intelligence pour en extraire des informations détaillées : résumé de l'activité, présence de réseaux sociaux, historique de "Live", et nom d'un contact clé.
        5.  **Sous-agent "Processeur de Données et Notificateur" (Modèle : `google/gemini-2.5-flash`) :** Exécute `scripts/prospect_veille.py` (`process_opportunities`) avec tous les résultats collectés. Il utilise des **Expressions Régulières (Regex)** pour parser les emails et téléphones. Il effectue une **double sauvegarde** : il enrichit les 18 colonnes de la feuille Google Sheets "Organisateurs Majeurs" en évitant les doublons, ET il pousse les données formatées (Nom, Email, Téléphone, Site Web, Secteur) vers **HubSpot** via l'API Gateway de Maton pour un test en parallèle. Enfin, il envoie la notification Telegram.
    *   **Fréquence :** Tous les matins (9h30), après-midis (14h00) et soirs (18h00) du lundi au vendredi (heure de Paris).
    *   **ID des jobs Cron :** `e34a5304-5bba-4fd1-a3d6-9dfb8f0323cb` (Matin), `77763649-ca75-4270-8940-1b34daf57768` (Après-midi), `58f466c1-fb95-498b-9b67-aaaa4d80472a` (Fin de journée - sera réinitialisée à 18h00).
    *   **Cible :** L'agent principal (moi) initie le workflow de sous-agents depuis une session isolée (`sessionTarget: "isolated"`).
    *   **Notification :** Gérée par le sous-agent "Processeur de Données et Notificateur" via Telegram (groupe Yew).

*   **Tâche :** Création brouillons prospects quotidiens
    *   **Description :** Processus stricte où l'agent principal lit la feuille Google Sheets et invoque **individuellement** le sous-agent `redacteur-emails-prospects` pour chaque prospect. Le sous-agent reçoit systématiquement le Golden Template de la Ligue de Basket de Bretagne pour garantir l'hyper-personnalisation et l'ancrage contextuel.
    *   **Fréquence :** Tous les matins du lundi au vendredi à 9h00 (heure de Paris).
    *   **ID du job Cron :** `50c70e78-f47f-4a70-ba7f-7e686891fa57`
    *   **Cible :** Session isolée (`sessionTarget: "isolated"`)
    *   **Notification :** Groupe Telegram Yew.


### Agents Persistants pour la Veille
*   **1. Agent persistant : "Générateur de Cibles"**
    *   **Nom (ID interne) :** `veille-generateur-cibles`
    *   **Modèle Gemini choisi :** `google/gemini-2.5-flash`.
*   **2. Agent persistant : "Chercheur Web"**
    *   **Nom (ID interne) :** `veille-chercheur-web`
    *   **Modèle Gemini choisi :** `google/gemini-2.5-flash`.
*   **3. Agent persistant : "Filtreur d'URLs"**
    *   **Nom (ID interne) :** `veille-filtreur-urls`
    *   **Modèle Gemini choisi :** `google/gemini-2.5-flash`.
*   **4. Agent persistant : "Explorateur de Pages"**
    *   **Nom (ID interne) :** `veille-explorateur-pages`
    *   **Modèle Gemini choisi :** `google/gemini-2.5-pro`.
*   **5. Agent persistant : "Processeur de Données et Notificateur"**
    *   **Nom (ID interne) :** `veille-processeur-donnees`
    *   **Modèle Gemini choisi :** `google/gemini-2.5-flash`.
*   **6. Agent persistant : "Rédacteur Emails Prospects"**
    *   **Nom (ID interne) :** `redacteur-emails-prospects`
    *   **Mission :** Rédiger des emails de prospection (cold emails) hautement personnalisés.
    *   **Modèle Gemini choisi :** `google/gemini-2.5-pro`.

### Principe Fondamental : Apprentissage Continu
*   **Règle :** Toujours apprendre des erreurs, analyser la résolution et intégrer les leçons tirées dans la mémoire persistante pour améliorer les performances futures.

### Apprentissage - Rédaction Emails (Golden Template & Feedback Boucle)
*   **Date :** 18 Mars 2026
*   **Leçon :** Remplacement des templates génériques ("Bonjour, en tant que passionnés...") par une structure d'hyper-personnalisation ancrée sur l'actualité de la cible.
*   **GOLDEN TEMPLATE (Référence absolue pour le sous-agent `redacteur-emails-prospects`) :**
    *   **Objet :** Proposition pour la [Nom de l'événement/tournée]
    *   **Structure du mail :**
        *   *Intro :* Bonjour, Je me présente, Michael. Je me permets de vous contacter à propos de [Événement très précis], car je pense pouvoir vous apporter une aide précieuse sur ce genre d’événement !
        *   *Contexte spécifique / Constat :* En regardant [Source d'information: chaîne YouTube / site], je sens une volonté de [Objectif du client]. J’ai aussi remarqué que [Observation factuelle mais non jugeante, ex: vous filmiez avec une seule caméra et un son d'ambiance brut].
        *   *Projection de partenariat :* Je pense que nous pourrions aller plus loin ensemble afin de [Bénéfice final pour l'audience]. Chez Yew, nous accompagnons justement des organismes comme le vôtre dans la captation d’événements sportifs ou autres.
        *   *Apports concrets (Bullet points) :* L'idée serait d'offrir [...] : Plusieurs angles de vue, Micros/caméras dédiés, Habillage visuel intégrant la charte, Co-diffusion.
        *   *Conclusion & Call To Action :* C'est un excellent levier pour valoriser [Cibles]... N'hésitez pas à jeter un œil à ce que nous produisons sur www.agenceyew.fr. Nous pourrions convenir d’un appel afin d’en discuter et voir si cette approche résonne avec vos projets.

### Mission Principale : Assistant Premier Contact Prospects
*   **Objectif :** Assister Michael et Guillaume dans le processus de premier contact avec de nouveaux prospects via Maton.ai et le Sheet "Organisateurs Majeurs".
