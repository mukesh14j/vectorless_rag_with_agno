import os
import re
import json
import pickle
import hashlib

from rank_bm25 import BM25Okapi

from chunker import chunk_text
from document_loader import load_document


class VectorlessRAG:

    def __init__(self):

        self.documents = {}
        self.indexes = {}
        self.file_hash_map = {}

        self.index_dir = "indexes"

        os.makedirs(
            self.index_dir,
            exist_ok=True
        )

        self.load_existing_indexes()

    def tokenize(self, text):

        text = text.lower()

        text = re.sub(
            r"[^a-zA-Z0-9\s]",
            " ",
            text
        )

        return text.split()

    def generate_hash(self, file_path):

        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:

            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    def load_existing_indexes(self):

        print("LOADING INDEXES...")

        for folder in os.listdir(
            self.index_dir
        ):

            folder_path = os.path.join(
                self.index_dir,
                folder
            )

            if not os.path.isdir(folder_path):
                continue

            try:

                metadata_path = os.path.join(
                    folder_path,
                    "metadata.json"
                )

                bm25_path = os.path.join(
                    folder_path,
                    "bm25.pkl"
                )

                chunks_path = os.path.join(
                    folder_path,
                    "chunks.pkl"
                )

                with open(
                    metadata_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    metadata = json.load(f)

                with open(
                    bm25_path,
                    "rb"
                ) as f:

                    bm25 = pickle.load(f)

                with open(
                    chunks_path,
                    "rb"
                ) as f:

                    chunks = pickle.load(f)

                document_id = metadata[
                    "document_id"
                ]

                file_hash = metadata[
                    "file_hash"
                ]

                self.indexes[
                    document_id
                ] = bm25

                self.documents[
                    document_id
                ] = chunks

                self.file_hash_map[
                    file_hash
                ] = document_id

                print(
                    f"LOADED: {document_id}"
                )

            except Exception as e:

                print(
                    f"FAILED TO LOAD "
                    f"{folder}: {e}"
                )

    def ingest(self, file_path):

        filename = os.path.basename(
            file_path
        )

        document_id = filename

        file_hash = self.generate_hash(
            file_path
        )

        doc_index_dir = os.path.join(
            self.index_dir,
            document_id
        )

        metadata_path = os.path.join(
            doc_index_dir,
            "metadata.json"
        )

        # Existing file check
        if os.path.exists(metadata_path):

            with open(
                metadata_path,
                "r",
                encoding="utf-8"
            ) as f:

                metadata = json.load(f)

            existing_hash = metadata.get(
                "file_hash"
            )

            # SAME CONTENT
            if existing_hash == file_hash:

                print(
                    "SAME FILE CONTENT - "
                    "REUSING EXISTING BM25"
                )

                return document_id

            # CONTENT CHANGED
            else:

                print(
                    "FILE CONTENT CHANGED - "
                    "REBUILDING BM25"
                )

                # Remove old memory cache
                if document_id in self.documents:
                    del self.documents[
                        document_id
                    ]

                if document_id in self.indexes:
                    del self.indexes[
                        document_id
                    ]

        else:

            print(
                "NEW FILE - CREATING BM25"
            )

        # Load document
        text = load_document(file_path)

        # Create chunks
        chunks = chunk_text(
            text,
            chunk_size=300,
            overlap=50
        )

        # Tokenize
        tokenized_chunks = [
            self.tokenize(chunk)
            for chunk in chunks
        ]

        # Create BM25
        bm25 = BM25Okapi(
            tokenized_chunks
        )

        # Store in memory
        self.documents[
            document_id
        ] = chunks

        self.indexes[
            document_id
        ] = bm25

        self.file_hash_map[
            file_hash
        ] = document_id

        # Create directory
        os.makedirs(
            doc_index_dir,
            exist_ok=True
        )

        # Save metadata
        metadata = {
            "document_id": document_id,
            "file_hash": file_hash,
            "filename": filename
        }

        with open(
            metadata_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metadata,
                f,
                indent=2
            )

        # Save chunks
        with open(
            os.path.join(
                doc_index_dir,
                "chunks.pkl"
            ),
            "wb"
        ) as f:

            pickle.dump(chunks, f)

        # Save BM25
        with open(
            os.path.join(
                doc_index_dir,
                "bm25.pkl"
            ),
            "wb"
        ) as f:

            pickle.dump(bm25, f)

        print(
            f"INDEX SAVED: {document_id}"
        )

        return document_id

    def retrieve(
        self,
        document_id,
        query,
        top_k=2
    ):

        if document_id not in self.indexes:

            raise Exception(
                "Document not found"
            )

        bm25 = self.indexes[
            document_id
        ]

        chunks = self.documents[
            document_id
        ]

        tokenized_query = self.tokenize(
            query
        )

        scores = bm25.get_scores(
            tokenized_query
        )

        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]