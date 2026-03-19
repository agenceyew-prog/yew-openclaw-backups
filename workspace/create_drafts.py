import urllib.request, os, json, base64
from email.message import EmailMessage

API_KEY = os.environ.get("MATON_API_KEY")

prospects = [
  {
    "email": "paris@sport-u.com",
    "subject": "Capter l'audience étudiante : Vos prochaines finales universitaires sur Twitch 🎮",
    "body": "Bonjour l'équipe du LSU IDF,\n\nJ'ai observé l'intensité grandissante des derbys et championnats universitaires franciliens cette saison.\n\nAujourd'hui, le public étudiant (18-25 ans) vit le sport différemment : ils attendent les codes de Twitch. Ils veulent de l'interactivité, réagir en direct dans le tchat et faire partie de l'événement. C'est un levier d'engagement massif, et un argument de poids pour valoriser vos compétitions auprès des sponsors ciblant les jeunes.\n\nC’est exactement ce que nous construisons chez Yew : une réalisation multicam premium (ralentis immédiats, habillage dynamique) mariée à la culture Twitch pour transformer vos tournois inter-écoles en véritables shows interactifs.\n\nSeriez-vous disponibles pour un bref échange téléphonique la semaine prochaine afin d'évoquer la captation de vos prochaines finales régionales ?\n\nBien à vous,\n\nMichael & Guillaume – Agence Yew\nwww.agenceyew.fr",
    "row": 12
  },
  {
    "email": "ligue.bretagne@fft.fr",
    "subject": "Sublimer vos prochaines finales régionales de Padel en Bretagne",
    "body": "Bonjour,\n\nJ’observe avec beaucoup d'enthousiasme l'explosion de la pratique du Padel au sein de la Ligue de Bretagne (l'engouement sur les nouveaux courts est exceptionnel !).\n\nPour un sport aussi intense et spectaculaire, le rythme visuel fait tout : vos spectateurs (et vos partenaires) s'attendent à vivre l'intensité des échanges au plus près de la piste (caméras embarquées sur les vitres, ralentis immédiats sur les smashs, intégration des scores en direct).\n\nC’est exactement ce que nous construisons chez Yew : une réalisation multicam premium qui transforme l'événement sportif en un véritable show immersif.\n\nSeriez-vous disponibles pour un bref échange téléphonique la semaine prochaine afin d'évoquer la captation de vos prochaines finales régionales de Padel ?\n\nBien à vous,\n\nMichael & Guillaume – Agence Yew\nwww.agenceyew.fr",
    "row": 13
  },
  {
    "email": "iledefrance@ffgym.fr",
    "subject": "Vos prochaines compétitions IDF : rapprocher les familles des agrès",
    "body": "Bonjour,\n\nJe suis régulièrement impressionné par le dynamisme et l'ampleur des compétitions organisées par le Comité Régional Île-de-France. Gérer autant de plateaux et de clubs sur un même week-end est un immense défi.\n\nIl reste pourtant une frustration classique lors de ces événements : avec 4 à 6 agrès qui tournent en simultané, les familles reléguées dans les gradins lointains peinent souvent à voir les détails, et ratent parfois le passage crucial de leur enfant.\n\nPour pallier cela, l'Agence Yew a développé une approche de captation pensée pour la gymnastique. Nous déployons une caméra par agrès, et notre réalisation bascule en direct sur l'action principale. Surtout, nous intégrons des ralentis sur les figures les plus complexes.\n\nL'expérience spectateur est totalement transformée : les familles vivent l'intensité au plus près de la magnésie, sans rien manquer. Ce format immersif est d'ailleurs particulièrement adapté si vous souhaitez mettre en place une billetterie vidéo (Pay-Per-View) pour valoriser vos événements.\n\nSeriez-vous disponible mardi ou jeudi prochain pour un échange de 10 minutes afin d'en discuter ?\n\nBien à vous,\n\nMichael & Guillaume\nAgence Yew - www.agenceyew.fr",
    "row": 15
  },
  {
    "email": "contact@hexagonemma.fr",
    "subject": "Hexagone MMA : Un rendu cinématique pour sublimer vos PPV",
    "body": "Bonjour,\n\nLa croissance foudroyante du MMA en France doit beaucoup à la force de frappe d'Hexagone MMA. Vous remplissez les Zéniths et vos audiences explosent sur Twitch et RMC Sport.\n\nAujourd'hui, votre modèle (PPV, abonnements) repose sur une promesse : offrir un spectacle total aux fans qui ne sont pas dans l'arène. L'intensité de la cage doit transpercer l'écran.\n\nC'est là que l'agence Yew intervient. Nous ne faisons pas de la simple captation classique : nous apportons une direction artistique brutale et un rendu véritablement cinématique qui matche l'ADN de votre ligue.\n\nConcrètement : des caméras immersives au ras du grillage pour ressentir chaque impact, des ralentis extrêmes pour sublimer les KO, et une captation sonore qui plonge le spectateur avec les combattants. L'objectif est de maximiser la valeur perçue de vos diffusions pour booster l'engagement et vos ventes PPV.\n\nSeriez-vous ouverts à un échange rapide au téléphone pour discuter de l'expérience spectateur de vos prochains galas ? Vous pouvez jeter un œil à notre approche sur www.agenceyew.fr.\n\nAu plaisir d'en discuter,\n\nMichael et Guillaume\nAgence Yew",
    "row": 16
  },
  {
    "email": "contact@triathlon-hdf.fr",
    "subject": "Nouveau Championnat Régional : et si le public voyait vraiment la course ?",
    "body": "Bonjour,\n\nBravo pour le lancement du tout premier Championnat Régional des clubs de Triathlon cette année. C’est une superbe évolution pour dynamiser la Ligue des Hauts-de-France et ses licenciés.\n\nMais on le sait, le triathlon est souvent très frustrant pour le public : on assiste au départ dans l'eau, puis les proches attendent de longs moments près de la ligne d'arrivée sans rien voir des parcours vélo et course à pied. Techniquement, couvrir 3 sports sur des dizaines de kilomètres en extérieur est un véritable cauchemar de production.\n\nC'est exactement notre terrain de jeu chez Yew. \n\nNotre mission est d'amener la course jusqu'aux spectateurs. Pour vos prochaines étapes, nous mettons en place un dispositif immersif : des caméras fixes sur les zones de transition complexes, des motos et vélos suiveurs pour être au cœur de l'effort (grâce à nos systèmes de transmission 4G/5G fiables), et des drones pour des plans aériens spectaculaires de la natation.\n\nLe résultat ? Un flux vidéo unifié, diffusé en direct sur écran géant à l'arrivée (et sur vos réseaux). L'ambiance y est exceptionnelle bien avant que les premiers athlètes ne franchissent la ligne, car tout le monde vit la course en temps réel.\n\nVous pouvez découvrir nos dernières productions ici : www.agenceyew.fr\n\nÊtes-vous disponibles la semaine prochaine pour un rapide échange téléphonique afin de discuter de la mise en valeur de ce nouveau Championnat ?\n\nBien à vous,\n\nMichael & Guillaume\nAgence Yew",
    "row": 14
  }
]

def create_draft(p):
    msg = EmailMessage()
    msg.set_content(p["body"])
    msg["To"] = p["email"]
    msg["Subject"] = p["subject"]
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    
    data = json.dumps({"message": {"raw": raw}}).encode("utf-8")
    req = urllib.request.Request("https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts", data=data, method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read().decode())
    except Exception as e:
        print(f"Error creating draft for {p['email']}: {e}")
        return None

def update_sheet(row):
    # column O is Statut Contact (index 14, A=0) -> "Brouillon préparé"
    # A=1 -> O=15. So column O.
    cell = f"'Organisateurs Majeurs'!O{row}"
    data = json.dumps({
        "values": [["Brouillon préparé"]]
    }).encode("utf-8")
    req = urllib.request.Request(f"https://gateway.maton.ai/google-sheets/v4/spreadsheets/1fIaChyoYhRt0RmsBIS7Z4SbSRukkXAwRZ5y01_uIVVQ/values/{urllib.parse.quote(cell)}?valueInputOption=USER_ENTERED", data=data, method="PUT")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read().decode())
    except Exception as e:
        print(f"Error updating sheet row {row}: {e}")
        return None

for p in prospects:
    print(f"Drafting for {p['email']}...")
    create_draft(p)
    update_sheet(p["row"])

print("All done.")
