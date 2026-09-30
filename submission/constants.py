
from django.db import models
from django.utils.translation import gettext_lazy as _


class QuestionType(models.TextChoices):
    TEXT = "text",_("متن کوتاه")
    TEXTAREA = "textarea",_("پاراگراف")
    NUMBER = "number",_("عدد")
    SELECT = "select",_("لیست کشویی")
    RADIO = "radio",_("تک گزینه ای")
    CHECKBOX = "checkbox",_("چند گزینه ای")

class QuestionCategory:
    TEXT_TYPES = frozenset({QuestionType.TEXT, QuestionType.TEXTAREA})
    NUMBER_TYPES = frozenset({QuestionType.NUMBER})
    SINGLE_CHOICE_TYPES = frozenset({QuestionType.SELECT, QuestionType.RADIO})
    MULTI_CHOICE_TYPES = frozenset({QuestionType.CHECKBOX})
    
    NEEDS_OPTIONS = frozenset({QuestionType.SELECT, QuestionType.RADIO, QuestionType.CHECKBOX})




class ProcessType(models.TextChoices):
    LINEAR = "linear",_("ترتیبی ")
    FREE = "free",_("آزاد")

