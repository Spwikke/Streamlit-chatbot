import pymupdf
import os
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

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

def question_gemini(question, texte_pdf, messages):
    instructions = f"""
    Réponds en priorité à partir du document fourni.
    Si le document ne contient pas la réponse, utilise tes connaissances générales pour répondre.
    Précise si ta réponse provient du document ou de tes connaissances générales.
    DOCUMENT :
    {texte_pdf}
    QUESTION :
    {question}
    """
    historique = []     # on crée un historique pour gemini
    for message in messages:
        if message["role"] == "assistant":
            role = "model"
        else:
            role = "user"
        historique.append({     # on ajoute la nouvelle question
            "role": role,
            "parts": [{"text": message["content"]}]
        })
    historique.append({
        "role": "user",
        "parts": [{"text": instructions}]
    })
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=historique
    )
    return response.text

def choisir_document(question, noms_fichiers):
    instructions = f"""
    Question : {question}
    Documents disponibles :
    {noms_fichiers}
    Choisis le document le plus pertinent pour répondre
    à la question, uniquement à partir de son nom.

    Réponds uniquement avec le nom exact du fichier.
    Si aucun document ne semble pertinent, réponds AUCUN.
    """
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=instructions
    )
    choix = response.text
    if choix in noms_fichiers:
        return choix
    return None
