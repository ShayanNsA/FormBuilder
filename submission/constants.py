

class QuestionType:
    TEXT = "text"
    TEXTAREA = "textarea"
    NUMBER = "number"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"

    TEXT_TYPES = frozenset({TEXT, TEXTAREA})
    NUMBER_TYPES = frozenset({NUMBER})
    SINGLE_CHOICE_TYPES = frozenset({SELECT, RADIO})
    MULTI_CHOICE_TYPES = frozenset({CHECKBOX})


class ProcessType:
    LINEAR = "linear"
    FREE = "free"

