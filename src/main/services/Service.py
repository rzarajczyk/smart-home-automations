class Service:
    def accepts_prefixes(self) -> list[str]:
        return []

    def on_message(self, topic, payload):
        pass
