import csv
import os
import shutil
import sys

import chromadb
from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
# from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from constants import CHROMA_SETTINGS
import get_data_requested


persist_directory = "db"


def remove_existing_vectors():
    folder = os.getcwd() + "\\db\\"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == "__main__":

    # ------------ similarity search --------------- #
    remove_existing_vectors()
    print("existing db cleared !!")

    # getting data into csv file.
    get_data_requested.get_avail_funcs_from_dirs()
    # data list to write
    data_list = get_data_requested.full_main
    get_data_requested.create_write_data_to_csv(data_list, "axdata.csv")
    print("Data successfully writen into CSV file.")

    # Define the columns we want to embed vs which ones we want in metadata
    columns_to_embed = ["Class", "Method", "Doc_string"]
    columns_to_metadata = ["Class", "Method", "Doc_string"]

    # Process the CSV into the embedable content vs the metadata and put it into Document format so that we can chunk it
    # into pieces.
    docs = []
    for root, dirs, files in os.walk("docs"):
        for file in files:
            if file.endswith(".csv"):
                print(f'Reading data from {file} for creating embeddings.')

                with open(os.path.join(root, file), newline="", encoding='utf-8-sig') as csvfile:
                    csv_reader = csv.DictReader(csvfile)
                    for i, row in enumerate(csv_reader):

                        to_metadata = {col: row[col] for col in columns_to_metadata if col in row}

                        values_to_embed = {k: row[k] for k in columns_to_embed if k in row}

                        to_embed = ",".join(f"{k.strip()}: {v.strip()}" for k, v in values_to_embed.items())

                        newDoc = Document(page_content=to_embed, metadata=to_metadata)
                        docs.append(newDoc)

    print('splitting data into small chunks..')
    # Let's split the document using Character splitting.
    splitter = CharacterTextSplitter(separator=";", chunk_size=500, chunk_overlap=0, length_function=len)
    documents = splitter.split_documents(docs)

    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    # create vector store here
    print(f"Creating embeddings. May take some minutes...")
    client = chromadb.PersistentClient(settings=CHROMA_SETTINGS, path="db")
    db = Chroma.from_documents(client=client, documents=documents, embedding=embeddings,
                               persist_directory=persist_directory)
    while True:
        query = input("You: ")
        if query in ["quit", "exit"]:
            break
        else:
            response_steps = []
            doccs = db.similarity_search_with_score(query, k=5)
            out_list = [(doc[0].page_content, doc[1]) for doc in doccs]
            print(f"\nBelow are the closest matches found:")
            res = out_list[0]
            for i, res in enumerate(out_list):
                score = res[1]
                pre_res_list = res[0].split(',', 1)
                class_name = pre_res_list[0].split(': ')[1]
                method_name = pre_res_list[1].split(': ')[1]
                response_steps.append((class_name, method_name, score))
                print(f'\n{i+1}')
                print(' Method: ', method_name, "\n", 'Class: ', class_name, "\n", 'Closet distance: ', score)

