import pymupdf      # ouvrir et de lire des documents PDF
from pathlib import Path       # manipuler les chemins et les fichiers
from langchain.tools import tool    # transformer une fonction Python en outil utilisable par un agent
from langchain.agents import create_agent   # créer un agent IA
from langchain_google_genai import ChatGoogleGenerativeAI   # pour utiliser le modèle Gemini de Google avec LangChain
from simpleeval import simple_eval  # évaluer des expressions mathématiques

dossier_pdf = Path("pdfs")  # chemin du dossier dans lequel sont enregistrés les documents PDF

def extraire_texte_pdf(donnees_pdf):
    document = pymupdf.open(            # ouvre les données comme un document PDF
        stream=donnees_pdf,
        filetype="pdf"
    )
    texte = ""          # chaine pour stocker le texte
    for page in document:       # on récup le texte de chaque page
        texte += page.get_text()
    document.close()        # on ferme le document
    return texte

@tool
def lister_documents() -> str:
    """Liste les noms des documents PDF disponibles."""
    fichiers = list(dossier_pdf.glob("*.pdf"))  # récupère tous les fichiers .pdf dans le dossier
    if not fichiers:
        return "Aucun document disponible."
    return str([fichier.name for fichier in fichiers])  # renvoie la liste des noms de fichiers

@tool
def lire_document(nom_fichier: str) -> str:
    """Lit le contenu d'un PDF à partir de son nom."""
    chemin = dossier_pdf / Path(nom_fichier).name   # assemble les deux chemins pour construire le chemin demandé
    if not chemin.is_file() or chemin.suffix.lower() != ".pdf":
        return "Ce fichier n'existe pas."
    return extraire_texte_pdf(chemin.read_bytes())  # lit les données du PDF, extrait son texte et le renvoie

@tool
def calculatrice(expression: str) -> str:
    """Effectue des calculs mathématiques."""
    return str(simple_eval(expression))    # convertit le résultat en texte

def creer_agent():
    modele = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")  # initialise le modele utilisé par l'agent
    agent = create_agent(   
        model=modele,
        tools=[lister_documents, lire_document, calculatrice],
        system_prompt="""
Tu es un assistant intelligent capable de répondre aux questions de l'utilisateur en français.
Tu disposes de plusieurs outils, mais tu dois les utiliser uniquement lorsqu'ils sont nécessaires.

CHOISIS TON COMPORTEMENT SELON LA QUESTION :
1. QUESTION GÉNÉRALE
- Réponds directement avec tes connaissances.
- N'utilise aucun outil.
- Précise : "Source : connaissances générales".
2. CALCUL MATHÉMATIQUE
- Utilise obligatoirement l'outil calculatrice, même pour un calcul simple.
- N'utilise pas les outils PDF.
- Précise : "Source : outil Calculatrice".
3. QUESTION SUR UN DOCUMENT PDF
- Si le nom du PDF est indiqué, utilise directement lire_document.
- Sinon, utilise lister_documents pour identifier les PDF disponibles.
- Lis uniquement les documents nécessaires.
- Réponds à partir des informations trouvées.
- Précise : "Source : document PDF [nom du fichier]".
4. QUESTION COMBINANT PLUSIEURS BESOINS
- Utilise uniquement les outils nécessaires à chaque partie.
- Distingue clairement les différentes sources utilisées.

RÈGLES IMPORTANTES :
- N'utilise jamais un outil sans raison.
- Ne consulte pas les PDF pour une question générale.
- Ne consulte pas plusieurs fois le même PDF pour une même question.
- Ne prétends jamais avoir utilisé un outil sans l'avoir réellement appelé.
- Si un PDF ne contient pas la réponse, indique-le clairement.
- Si tu complètes avec tes connaissances générales, précise-le.
- Réponds de manière claire, concise et toujours en français.
"""
    )
    return agent
