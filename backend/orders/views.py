import json
import os
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


ORDERS = {}


def extract_openai_text(response_body):
    choices = response_body.get("choices", [])
    if not choices:
        raise RuntimeError("LLM response did not include choices.")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, list):
        text = "\n".join(item.get("text", "") for item in content if isinstance(item, dict)).strip()
    else:
        text = str(content).strip()

    if not text:
        raise RuntimeError("LLM response did not include text output.")
    return text


def build_care_plan_prompt(data):
    patient_name = f"{data.get('patient_first_name', '').strip()} {data.get('patient_last_name', '').strip()}".strip()

    return f"""Generate a concise specialty pharmacy care plan using the patient and order information below.

Required sections:
1. Problem list / Drug therapy problems
2. Goals
3. Pharmacist interventions / plan
4. Monitoring plan

Keep the tone professional and practical for a pharmacist. Do not invent lab values or facts that are not provided.

Patient information:
- Name: {patient_name or "Not provided"}
- MRN: {data.get("patient_mrn", "Not provided")}
- Referring provider: {data.get("referring_provider", "Not provided")}
- Referring provider NPI: {data.get("referring_provider_npi", "Not provided")}
- Primary diagnosis: {data.get("primary_diagnosis", "Not provided")}
- Additional diagnoses: {data.get("additional_diagnoses", "Not provided")}
- Medication name: {data.get("medication_name", "Not provided")}
- Medication history: {data.get("medication_history", "Not provided")}
- Patient records: {data.get("patient_records", "Not provided")}
"""


def build_care_plan(data):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    api_url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You generate specialty pharmacy care plans for pharmacist review.",
            },
            {
                "role": "user",
                "content": build_care_plan_prompt(data),
            },
        ],
        "max_tokens": 1200,
    }

    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8")
        try:
            error_json = json.loads(error_body)
            message = error_json.get("error", {}).get("message", "LLM API request failed.")
        except json.JSONDecodeError:
            message = "LLM API request failed."
        raise RuntimeError(message) from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("Could not connect to LLM API.") from exc

    return extract_openai_text(response_body)


@csrf_exempt
def create_order(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed."}, status=405)

    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "status": "processing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": data,
        "care_plan": "",
        "error_message": "",
    }
    ORDERS[order_id] = order

    try:
        order["care_plan"] = build_care_plan(data)
        order["status"] = "completed"
    except Exception as exc:
        order["status"] = "failed"
        order["care_plan"] = ""
        order["error_message"] = str(exc)

    return JsonResponse(order, status=201)


def get_order(request, order_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET is allowed."}, status=405)

    order = ORDERS.get(order_id)
    if not order:
        raise Http404("Order not found")

    return JsonResponse(order)


def download_care_plan(request, order_id):
    if request.method != "GET":
        return JsonResponse({"error": "Only GET is allowed."}, status=405)

    order = ORDERS.get(order_id)
    if not order:
        raise Http404("Order not found")

    if order["status"] != "completed":
        return JsonResponse({"error": "Care plan is not completed yet."}, status=400)

    filename = f"care_plan_{order_id}.txt"
    response = HttpResponse(order["care_plan"], content_type="text/plain; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Content-Type"] = "text/plain; charset=utf-8"
    return response
