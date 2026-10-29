import pymupdf
from pathlib import Path
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

dossier_pdf = Path("pdfs")

def extraire_texte_pdf(donnees_pdf):
    document = pymupdf.open(            # ouvre les données comme un document PDF
        stream=donnees_pdf,
        filetype="pdf"
    )
    texte = ""
    for page in document:
        texte += page.get_text()
    document.close()
    return texte

@tool
def lister_documents() -> str:
    """Liste les noms des documents PDF disponibles."""
    fichiers = list(dossier_pdf.glob("*.pdf"))
    if not fichiers:
        return "Aucun document disponible."
    return str([fichier.name for fichier in fichiers])

@tool
def lire_document(nom_fichier: str) -> str:
    """Lit le contenu d'un PDF à partir de son nom."""
    chemin = dossier_pdf / Path(nom_fichier).name
    if not chemin.is_file() or chemin.suffix.lower() != ".pdf":
        return "Ce fichier n'existe pas."
    return extraire_texte_pdf(chemin.read_bytes())

def creer_agent():
    modele = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    agent = create_agent(
        model=modele,
        tools=[lister_documents, lire_document],
        system_prompt="""
        Tu es un assistant spécialisé dans l'analyse de documents PDF.
        Lorsque l'utilisateur pose une question sur un document :
        1. Utilise lister_documents pour connaître les PDF disponibles.
        2. Choisis le document pertinent.
        3. Utilise lire_document pour récupérer son contenu.
        4. Réponds à partir des informations trouvées.

         Règles importantes :
        - Si ta réponse provient d'un PDF que tu as réellement consulté,
        indique à la fin : "Source : document PDF [nom du fichier]".
        - Si le document ne contient pas la réponse, tu peux utiliser
        tes connaissances générales, mais indique clairement :
        "Source : connaissances générales".
        - Si tu combines les deux sources, distingue les informations
        provenant du PDF de celles provenant de tes connaissances.
        - Ne prétends jamais avoir consulté un document sans avoir
        utilisé l'outil lire_document.
        - Réponds toujours en français.
        """
    )
    return agent
