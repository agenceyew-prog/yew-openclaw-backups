import urllib.request, os, json, sys, base64
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr

MATON_API_KEY = os.environ.get("MATON_API_KEY")

def api_call(url, method='GET', data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
    if data:
        req.add_header('Content-Type', 'application/json; charset=utf-8')
    with urllib.request.urlopen(req, data) as response:
        return json.loads(response.read().decode('utf-8'))

# Delete the 5 most recent drafts
print("Récupération des anciens brouillons...")
drafts_list_url = 'https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts?maxResults=5'
drafts_resp = api_call(drafts_list_url)
if 'drafts' in drafts_resp:
    for d in drafts_resp['drafts']:
        print(f"Suppression de l'ancien brouillon {d['id']}...")
        req = urllib.request.Request(f"https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts/{d['id']}", method='DELETE')
        req.add_header('Authorization', f'Bearer {MATON_API_KEY}')
        try:
            urllib.request.urlopen(req)
        except Exception as e:
            pass

def create_draft(to_email, subject, body_html):
    encoded_subject = Header(subject, 'utf-8').encode()
    msg = MIMEText(body_html, 'html', 'utf-8')
    msg['to'] = to_email
    msg['from'] = formataddr((str(Header('Agence Yew', 'utf-8')), 'contact@agenceyew.fr'))
    msg['subject'] = encoded_subject
    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    draft_payload = {'message': {'raw': raw_message}}
    url = 'https://gateway.maton.ai/google-mail/gmail/v1/users/me/drafts'
    api_call(url, method='POST', data=json.dumps(draft_payload).encode('utf-8'))

emails = [
    {
        "to": "communication@lfhf.fff.fr",
        "subject": "Proposition pour la captation de vos Finales Régionales",
        "body": """Bonjour,<br><br>
Je me présente, Michael. Je me permets de vous contacter à propos des Finales de Coupes Régionales de la LFHF, car je pense pouvoir vous apporter une aide précieuse sur ce genre d’événement !<br><br>
En regardant vos résumés vidéos et vos réseaux, je sens une forte volonté de mettre en avant les clubs amateurs de la région. J’ai aussi remarqué que la captation vidéo lors des finales se limitait souvent à un plan large assez statique, sans retransmission en direct pour les supporters qui n'ont pas pu se déplacer.<br><br>
Je pense que nous pourrions aller plus loin ensemble afin d'offrir au football amateur une diffusion digne des professionnels. Chez Yew, nous accompagnons justement des instances sportives comme la vôtre dans la captation de finales et grands événements.<br><br>
L'idée serait d'offrir aux supporters et aux clubs une expérience premium :<br>
- Plusieurs angles de vue autour du terrain pour ne rien rater des actions clés<br>
- L'intégration de ralentis en direct (Action Replay) pour décortiquer le jeu<br>
- Des micros d'ambiance et une régie pour des commentaires en direct<br>
- Un habillage visuel intégrant la charte graphique de la Ligue et de vos partenaires officiels (comme le Crédit Agricole)<br>
- Une co-diffusion en simultané sur YouTube ou Facebook<br><br>
C'est un excellent levier pour valoriser les joueurs amateurs, ravir les supporters et consolider votre relation avec vos sponsors en leur offrant une visibilité à l'écran.<br><br>
N'hésitez pas à jeter un œil à ce que nous produisons sur <a href="https://www.agenceyew.fr">www.agenceyew.fr</a><br><br>
Nous pourrions convenir d’un appel afin d’en discuter et voir si cette approche résonne avec vos projets.<br><br>
Bien à vous,<br>
Michael & Guillaume - Agence Yew<br>
www.agenceyew.fr"""
    },
    {
        "to": "iledefrance@franceolympique.com",
        "subject": "Proposition pour vos Trophées des Sports et Assemblées Générales",
        "body": """Bonjour,<br><br>
Je me présente, Michael. Je me permets de vous contacter à propos de vos prochains Trophées des Sports ou Assemblées Générales du CROS Île-de-France, car je pense pouvoir vous apporter une aide précieuse sur ce type d'événements !<br><br>
En regardant vos publications, je sens une vraie volonté de fédérer et de mettre en lumière les acteurs du sport francilien. J’ai aussi remarqué que les diffusions ou captations institutionnelles souffraient parfois d'un manque de dynamisme (souvent un plan fixe sur l'estrade) et d'une image très conventionnelle.<br><br>
Je pense que nous pourrions aller plus loin ensemble afin de dépoussiérer la forme et d'offrir un rendu "premium" à ces moments clés de l'institution. Chez Yew, nous accompagnons justement des organismes de votre envergure dans la captation d’événements sportifs et de remises de prix.<br><br>
L'idée serait d'offrir aux spectateurs (sur place et à distance) une expérience de qualité supérieure :<br>
- Une réalisation "Brutalisme Premium", très moderne et immersive, qui casse les codes de la conférence classique<br>
- Plusieurs angles de vue (public, scène, intervenants) pour rythmer la diffusion<br>
- Un habillage visuel dynamique intégrant les logos de vos partenaires et les noms des lauréats<br>
- Un flux sécurisé pour un stream privé ou une diffusion en direct sur LinkedIn pour vos réseaux professionnels<br><br>
C'est un excellent levier pour valoriser les lauréats, dynamiser l'image du CROS et renforcer le sentiment d'appartenance de vos membres institutionnels.<br><br>
N'hésitez pas à jeter un œil à ce que nous produisons sur <a href="https://www.agenceyew.fr">www.agenceyew.fr</a><br><br>
Nous pourrions convenir d’un appel afin d’en discuter et voir si cette approche résonne avec vos projets.<br><br>
Bien à vous,<br>
Michael & Guillaume - Agence Yew<br>
www.agenceyew.fr"""
    },
    {
        "to": "contact@lhdfa.fr",
        "subject": "Proposition pour la diffusion de vos Championnats Régionaux et Meetings",
        "body": """Bonjour,<br><br>
Je me présente, Michael. Je me permets de vous contacter à propos de vos Championnats Régionaux d'Athlétisme et de vos grands meetings en salle, car je pense pouvoir vous apporter une aide précieuse sur ces compétitions !<br><br>
En suivant vos événements, je sens une belle volonté de faire rayonner l'athlétisme dans les Hauts-de-France. Cependant, j’ai remarqué qu'il est souvent très complexe de retranscrire toute la densité d'un meeting : filmer la piste et les concours en même temps est un défi technique que les captations traditionnelles peinent à relever.<br><br>
Je pense que nous pourrions aller plus loin ensemble afin d'offrir aux spectateurs et aux passionnés une couverture exhaustive et fluide de vos épreuves. Chez Yew, nous accompagnons justement les ligues dans la captation d’événements sportifs complexes.<br><br>
L'idée serait de proposer une expérience télévisuelle directement sur vos réseaux :<br>
- Une régie mobile multicam capable de gérer des caméras sur la piste (courses) ET sur les sautoirs/lancers simultanément<br>
- L'incrustation en direct des chronomètres officiels et des classements grâce à nos flux de données<br>
- Des ralentis (Action Replay) pour sublimer l'effort des athlètes<br>
- Une co-diffusion en simultané là où se trouve votre audience (YouTube, Facebook, Twitch)<br><br>
C'est un excellent levier pour valoriser chaque discipline de l'athlétisme, ravir les clubs et accroître la visibilité de la Ligue auprès de nouveaux partenaires.<br><br>
N'hésitez pas à jeter un œil à ce que nous produisons sur <a href="https://www.agenceyew.fr">www.agenceyew.fr</a><br><br>
Nous pourrions convenir d’un appel afin d’en discuter et voir si cette approche résonne avec vos projets.<br><br>
Bien à vous,<br>
Michael & Guillaume - Agence Yew<br>
www.agenceyew.fr"""
    },
    {
        "to": "secretariat@lif-natation.fr",
        "subject": "Proposition pour la retransmission de vos Championnats d'Île-de-France",
        "body": """Bonjour,<br><br>
Je me présente, Michael. Je me permets de vous contacter à propos de vos Championnats d'Île-de-France de Natation, car je pense pouvoir vous apporter une aide précieuse sur ce genre d’événement !<br><br>
En observant la communication autour de vos compétitions, je sens une vraie volonté de permettre aux clubs et aux familles de suivre les performances des nageurs. J’ai aussi remarqué que la captation en milieu aquatique était souvent freinée par des difficultés techniques (réseau instable dans les piscines, son réverbéré, angles de vue limités depuis les gradins).<br><br>
Je pense que nous pourrions aller plus loin ensemble afin d'offrir une retransmission fluide et immersive, malgré les contraintes du lieu. Chez Yew, nous accompagnons justement des fédérations et ligues dans la captation d’événements sportifs en environnements complexes.<br><br>
L'idée serait d'offrir aux proches et aux clubs une expérience de qualité sans compromis technique :<br>
- Un dispositif hybride de caméras au bord des bassins pour des plans dynamiques et proches de l'effort<br>
- Un habillage visuel intégrant vos partenaires, les noms des nageurs et potentiellement le chronométrage<br>
- Une sécurisation intégrale des flux (bonding / redondance 4G) pour garantir un live sans coupure, même si le Wi-Fi de la piscine est faible<br>
- Des micros directionnels pour atténuer le brouhaha ambiant et isoler les annonces officielles<br><br>
C'est un excellent levier pour valoriser les athlètes, rassurer et ravir les familles à distance, et donner une image moderne à la Ligue IDF.<br><br>
N'hésitez pas à jeter un œil à ce que nous produisons sur <a href="https://www.agenceyew.fr">www.agenceyew.fr</a><br><br>
Nous pourrions convenir d’un appel afin d’en discuter et voir si cette approche résonne avec vos projets.<br><br>
Bien à vous,<br>
Michael & Guillaume - Agence Yew<br>
www.agenceyew.fr"""
    },
    {
        "to": "contact@ffc-bretagne.com",
        "subject": "Proposition pour la captation de vos Championnats de Bretagne (Route et Cyclo-cross)",
        "body": """Bonjour,<br><br>
Je me présente, Michael. Je me permets de vous contacter à propos des Championnats de Bretagne (Route et Cyclo-cross), car je pense pouvoir vous apporter une aide précieuse sur ce genre d’événement si particulier à filmer !<br><br>
En suivant le cyclisme breton, je sens votre volonté de faire vivre l'intensité des courses au plus grand nombre. J’ai aussi remarqué que les captations amateurs se limitaient souvent à des caméras fixes sur la ligne d'arrivée, ce qui fait perdre toute la narration et le suspense de la course en peloton ou dans les sous-bois.<br><br>
Je pense que nous pourrions aller plus loin ensemble afin de plonger le spectateur au cœur de l'action. Chez Yew, nous accompagnons justement des organisations sportives dans la captation de sports en mouvement et sur de vastes zones géographiques.<br><br>
L'idée serait d'offrir aux passionnés de cyclisme une expérience de retransmission complète :<br>
- L'utilisation de drones 4K (notre grande expertise) pour suivre les échappées et offrir des vues aériennes spectaculaires des pelotons<br>
- Des caméras embarquées (motos) reliées à notre régie mobile<br>
- Une technologie de redondance 4G/5G (Bonding) garantissant un flux live continu, même dans les zones blanches ou les forêts du cyclo-cross<br>
- Un habillage dynamique (écarts, chronos, sponsors) et des micros d'ambiance pour ressentir l'effort<br><br>
C'est un excellent levier pour valoriser le terroir breton, immerger les familles et consolider votre relation avec vos partenaires financiers.<br><br>
N'hésitez pas à jeter un œil à ce que nous produisons sur <a href="https://www.agenceyew.fr">www.agenceyew.fr</a><br><br>
Nous pourrions convenir d’un appel afin d’en discuter et voir si cette approche résonne avec vos projets.<br><br>
Bien à vous,<br>
Michael & Guillaume - Agence Yew<br>
www.agenceyew.fr"""
    }
]

print("Création des 5 nouveaux brouillons ultra-personnalisés...")
for mail in emails:
    create_draft(mail['to'], mail['subject'], mail['body'])
    print(f"Brouillon créé pour {mail['to']}")
