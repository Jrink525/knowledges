        # Delete existing chunks for this document
        self.vs.delete(filter={"doc_id": doc_id})
