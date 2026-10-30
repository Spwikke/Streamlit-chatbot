import pymupdf      # ouvrir et de lire des documents PDF
from pathlib import Path       # manipuler les chemins et les fichiers
from langchain.tools import tool    # transformer une fonction Python en outil utilisable par un agent
from langchain.agents import create_agent   # créer un agent IA
from langchain_google_genai import ChatGoogleGenerativeAI   # pour utiliser le modèle Gemini de Google avec LangChain
from simpleeval import simple_eval  # évaluer des expressions mathématiques
from langchain_core.documents import Document    # pour représenter les documents avec leurs métadonnées
from langchain_text_splitters import RecursiveCharacterTextSplitter # pour découper le texte en chunks
from langchain_google_genai import GoogleGenerativeAIEmbeddings    # pour transformer les textes en vecteurs
from langchain_chroma import Chroma     # pour stocker les vecteurs et effectuer des recherches
from uuid import uuid4      # pour générer des identifiants uniques

dossier_pdf = Path("pdfs")  # chemin du dossier dans lequel sont enregistrés les documents PDF

# 1ère étape : Pour un RAG, il est préférable de transformer chaque page en objet Document de LangChain.
def charger_pdf(chemin: Path):
    documents = []      # liste qui contiendra les pages du PDF
    with pymupdf.open(chemin) as pdf:
        for numero_page, page in enumerate(pdf):    # donne à la fois l'indice de la page et l'objet page
            texte = page.get_text()
            if not texte.strip():   # si pas de texte
                continue
            document = Document(     # crée un objet Document LangChain pour chaque page
                page_content=texte,
                metadata={
                    "source": chemin.name,      # nom du PDF
                    "page": numero_page + 1     # numéro de page (+1 car commence à 0)
                }
            )
            documents.append(document)    # ajoute la page à la liste
    return documents    # renvoie toutes les pages sous forme de Documents

# 2ème étape :  Use text splitters to break large Documents into smaller chunks.
def decouper_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # chunks de 1000 caractères avec chevauchement de 200 caractères 
    chunks = splitter.split_documents(documents)
    return chunks   # renvoie la liste des morceaux de texte

#3ème étape : Embeddings models convert each chunk into a numeric vector that captures its 
#             meaning, enabling similarity search over your content.
def creer_embeddings():
    embeddings = GoogleGenerativeAIEmbeddings(      # on initialise le modèle Gemini qui transforme les textes en vecteurs
        model="gemini-embedding-2-preview"
    )
    return embeddings   # renvoie le modèle d'embeddings

# 4ème étape : Use a VectorStore to index chunks and their embeddings for retrieval.
def creer_base_vectorielle():
    embeddings = creer_embeddings()     # récupère le modèle d'embeddings
    vector_store = Chroma(
        collection_name="documents_pdf",
        embedding_function=embeddings,      # modèle utilisé pour calculer les vecteurs
        persist_directory="./chroma_db"     # dossier où les vecteurs sont enregistrés
    )  
    return vector_store     # renvoie la base vectorielle

def indexation(chemin: Path):
    documents = charger_pdf(chemin)
    if not documents:
        raise ValueError("Aucun texte trouvé dans le PDF.")
    chunks = decouper_documents(documents)
    vector_store = creer_base_vectorielle()
    anciens = vector_store.get(     # on recherche les anciens chunks associés au même nom de PDF
        where={"source": chemin.name}
    )
    if anciens["ids"]:      # on supprime les anciens chunks pour éviter les doublons
        vector_store.delete(ids=anciens["ids"])
    uuids = [str(uuid4()) for _ in chunks]     # génère un identifiant unique pour chaque chunk
    vector_store.add_documents(     # attribuer un identifiant unique à chaque chunk
        documents=chunks,
        ids=uuids
    )
    return len(chunks)  # on renvoie le nombre de chunks indexés

@tool
def lister_documents() -> str:
    """Liste les noms des documents PDF disponibles."""
    fichiers = list(dossier_pdf.glob("*.pdf"))  # récupère tous les fichiers .pdf dans le dossier
    if not fichiers:
        return "Aucun document disponible."
    return str([fichier.name for fichier in fichiers])  # renvoie la liste des noms de fichiers

@tool
def calculatrice(expression: str) -> str:
    """Effectue des calculs mathématiques."""
    return str(simple_eval(expression))    # convertit le résultat en texte

@tool
def rechercher_documents(question: str) -> str:
    """Recherche les passages pertinents dans les PDF indexés."""
    base = creer_base_vectorielle()
    documents = base.similarity_search(     # on recherche les chunks similaires
        query=question,
        k=4     # maximum 4 chunks
    )
    if not documents: 
        return "Aucun passage trouvé."
    resultats = []      # liste pour stocker les passages retrouvés
    for document in documents:      # on parcourt les chunks retrouvés
        texte = document.page_content   # récupère le texte du chunk
        source = document.metadata.get("source", "Inconnue")
        page = document.metadata.get("page", "Inconnue")
        resultat = (        # texte contenant le passage et ses références
            f"Source : {source}\n"
            f"Page : {page}\n"
            f"Texte : {texte}"
        )
        resultats.append(resultat)      # ajoute le passage à la liste
    return "\n".join(resultats)         # regroupe tous les passages dans un seul texte

def creer_agent():
    modele = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")  # initialise le modele utilisé par l'agent
    agent = create_agent(   
        model=modele,
        tools=[lister_documents, rechercher_documents, calculatrice],
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
- Si le nom du PDF est indiqué, utilise directement rechercher_documents.
- Réponds à partir des passages retrouvés.
- Cite les noms des documents et les pages.
4. QUESTION SUR LES DOCUMENTS DISPONIBLES
- Utilise lister_documents pour identifier les PDF disponibles.
5. QUESTION COMBINANT PLUSIEURS BESOINS
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
