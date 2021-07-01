__all__ = (
    "PaginationError",
    "CannotSendMessages",
    "CannotReadMessageHistory",
    "CannotEmbedLinks",
    "CannotAddReactions",
    "CannotUseExternalEmojis",
)


class PaginationError(Exception):

    pass


class CannotSendMessages(PaginationError):
    def __init__(self):
        super().__init__("Bot cannot send messages in this channel.")


class CannotReadMessageHistory(PaginationError):
    def __init__(self):
        super().__init__("Bot cannot read message history in this channel.")


class CannotEmbedLinks(PaginationError):
    def __init__(self):
        super().__init__("Bot cannot embed links in this channel.")


class CannotAddReactions(PaginationError):
    def __init__(self):
        super().__init__("Bot cannot add reactions in this channel.")


class CannotUseExternalEmojis(PaginationError):
    def __init__(self):
        super().__init__("Bot cannot use external emojis in this channel.")
