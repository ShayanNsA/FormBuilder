from decimal import Decimal, InvalidOperation
from django.db import IntegrityError, transaction
from django.db.models import Min
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from form.models import Question
from process.models import ProcessStep
from .constants import ProcessType, QuestionCategory
from .models import Answer, ExecutionStatus, FormSubmission, ProcessExecution


MAX_NUMBER = Decimal("1e14")
NUMBER_STEP = Decimal("0.000001")


def get_client_ip(request):
    return request.META.get("REMOTE_ADDR")


def _is_empty(value):
    if value is None:
        return True
    if isinstance(value, str):
        return not value.strip()
    if isinstance(value, (list, tuple)):
        return len(value) == 0
    return False


def _question_options(question):
    options = question.question_options
    return options if isinstance(options, list) else []


def _normalize_text(value):
    if not isinstance(value, str):
        raise ValueError("مقدار باید متن باشد.")
    return {"value_text": value.strip()}


def _normalize_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("مقدار باید عدد باشد.")
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError("مقدار باید عدد باشد.")
    if not number.is_finite():
        raise ValueError("مقدار باید عدد باشد.")
    if abs(number) >= MAX_NUMBER:
        raise ValueError("عدد وارد شده بیش از حد بزرگ است.")
    return {"value_number": number.quantize(NUMBER_STEP)}


def _normalize_single_choice(question, value):
    if not isinstance(value, str) or value not in _question_options(question):
        raise ValueError("گزینه انتخاب شده معتبر نیست.")
    return {"value_json": value}


def _normalize_multi_choice(question, value):
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ValueError("مقدار باید لیستی از گزینه‌ها باشد.")
    options = _question_options(question)
    if any(v not in options for v in value):
        raise ValueError("یکی از گزینه‌های انتخاب شده معتبر نیست.")
    return {"value_json": list(dict.fromkeys(value))}


def normalize_value(question, value):
    qtype = question.question_type
    if qtype in QuestionCategory.TEXT_TYPES:
        return _normalize_text(value)
    if qtype in QuestionCategory.NUMBER_TYPES:
        return _normalize_number(value)
    if qtype in QuestionCategory.SINGLE_CHOICE_TYPES:
        return _normalize_single_choice(question, value)
    if qtype in QuestionCategory.MULTI_CHOICE_TYPES:
        return _normalize_multi_choice(question, value)
    raise ValueError("نوع این سوال پشتیبانی نمی‌شود.")


def validate_answers(form, answers):
    questions = {q.id: q for q in Question.objects.filter(form=form)}
    errors = {}
    prepared = {}
    seen = set()

    for item in answers:
        question_id = item["question"]
        question = questions.get(question_id)
        if question is None:
            errors[str(question_id)] = "این سوال متعلق به این فرم نیست."
            continue
        if question_id in seen:
            errors[str(question_id)] = "برای این سوال بیش از یک پاسخ ارسال شده است."
            continue
        seen.add(question_id)

        if _is_empty(item["value"]):
            continue
        try:
            prepared[question_id] = (question, normalize_value(question, item["value"]))
        except ValueError as e:
            errors[str(question_id)] = str(e)

    for question in questions.values():
        key = str(question.id)
        if question.is_required and question.id not in prepared and key not in errors:
            errors[key] = "پاسخ به این سوال الزامی است."

    if errors:
        raise ValidationError({"answers": errors})
    return list(prepared.values())


def start_execution(*, process, user):
    first_order = ProcessStep.objects.filter(process=process).aggregate(
        first=Min("step_order")
    )["first"]
    if first_order is None:
        raise ValidationError({"process": "این فرایند هیچ مرحله‌ای ندارد."})
    try:
        with transaction.atomic():
            return ProcessExecution.objects.create(
                process=process,
                user=user,
                current_step_order=first_order,
            )
    except IntegrityError:
        raise ValidationError(
            {"process": "شما یک اجرای فعال برای این فرایند دارید."}
        )


def _check_execution_step(execution, form):
    if execution.status != ExecutionStatus.IN_PROGRESS:
        raise ValidationError({"process_execution": "این اجرا قبلاً تکمیل شده است."})

    step = ProcessStep.objects.filter(process_id=execution.process_id, form=form).first()
    if step is None:
        raise ValidationError({"form": "این فرم جزو مراحل این فرایند نیست."})

    is_linear = execution.process.process_type == ProcessType.LINEAR
    if is_linear and step.step_order != execution.current_step_order:
        raise ValidationError(
            {"form": "ابتدا باید مرحله جاری فرایند را تکمیل کنید."}
        )

    if FormSubmission.objects.filter(process_execution=execution, form=form).exists():
        raise ValidationError({"form": "این مرحله قبلاً تکمیل شده است."})
    return step


def _advance_execution(execution, step):
    steps = ProcessStep.objects.filter(process_id=execution.process_id)
    required_forms = set(steps.values_list("form_id", flat=True))
    done_forms = set(
        FormSubmission.objects.filter(process_execution=execution).values_list(
            "form_id", flat=True
        )
    )

    if required_forms <= done_forms:
        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = timezone.now()
        execution.save(update_fields=["status", "completed_at"])
        return

    if execution.process.process_type == ProcessType.LINEAR:
        next_order = steps.filter(step_order__gt=step.step_order).aggregate(
            next=Min("step_order")
        )["next"]
        execution.current_step_order = next_order
        execution.save(update_fields=["current_step_order"])


def create_submission(*, form, user, ip, prepared_answers, execution=None):
    with transaction.atomic():
        step = None
        if execution is not None:
            execution = (
                ProcessExecution.objects.select_for_update(of=("self",))
                .select_related("process")
                .get(pk=execution.pk)
            )
            step = _check_execution_step(execution, form)

        submission = FormSubmission.objects.create(
            form=form,
            process_execution=execution,
            user=user,
            submitter_ip=ip,
        )
        Answer.objects.bulk_create(
            [
                Answer(form_submission=submission, question=question, **fields) for question, fields in prepared_answers
            ]
        )

        if execution is not None:
            _advance_execution(execution, step)
    return submission

