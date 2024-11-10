# Instances of this class represent one of the queries
# in the "config/sample_queries.txt" file.
# Chris Joakim, Microsoft


class SampleQuery:

    def __init__(self):
        self.data = dict()
        self.data["name"] = ""
        self.text_lines = list()

    def set_name(self, name) -> None:
        self.data["name"] = str(name).strip()

    def append_to_text(self, text) -> None:
        self.text_lines.append(text)

    def get_data(self) -> dict:
        self.data["text"] = "\n".join(self.text_lines)
        return self.data

    def is_valid(self) -> bool:
        if len(self.data["name"]) < 4:
            return False
        if len(self.text_lines) < 1:
            return False
        return True
