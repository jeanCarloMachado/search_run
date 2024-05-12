from python_search.search.entries_loader import EntriesLoader
import tqdm
import os


class SemanticSearch:

    def __init__(self, entries: dict = None, number_entries_to_return=None):
        self.setup()
        if entries:
            self.entries = EntriesLoader.convert_to_list_of_entries(entries)
        else:
            self.entries = EntriesLoader.load_all_entries()

        self.number_entries_to_return = (
            number_entries_to_return if number_entries_to_return else 15
        )

    def setup(self):
        self.get_chroma_instance()
        try:
            self.collection = self.client.get_collection("entries")
        except:
            print("Collection not found")
            self.collection = self.setup_entries()

    def get_chroma_instance(self):
        import chromadb
        self.chroma_path = os.environ["HOME"] + "/.chroma_python_search.db"
        self.client = chromadb.PersistentClient(path=self.chroma_path)
        return self.client


    def setup_entries(self):
        collection = self.client.get_or_create_collection("entries")

        for entry in tqdm.tqdm(self.entries):
            collection.upsert(
                documents=[
                    entry.key + " " + entry.get_content_str() + entry.get_type_str()
                ],
                ids=[entry.key],
            )

        return collection

    def search(self, query: str):
        if not query:
            query = ""
        results = self.collection.query(
            query_texts=[query], n_results=self.number_entries_to_return
        )["ids"][0]
        return results


if __name__ == "__main__":
    import fire

    fire.Fire(SemanticSearch)
