import json
import time
import uuid
from datetime import datetime, timezone

from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt


ORDERS = {}


def build_care_plan(data):
    time.sleep(2)

    patient_name = f"{data.get('patient_first_name', '').strip()} {data.get('patient_last_name', '').strip()}".strip()
    medication = data.get("medication_name", "the prescribed medication")
    primary_diagnosis = data.get("primary_diagnosis", "the primary diagnosis")
    patient_records = data.get("patient_records", "")
    medication_history = data.get("medication_history", "")

    return f"""Care Plan

Patient: {patient_name or "Unknown patient"}
Medication: {medication}
Primary Diagnosis: {primary_diagnosis}

Problem list / Drug therapy problems
- Patient requires a medication-specific care plan for {medication}.
- Monitor therapy response related to {primary_diagnosis}.
- Review medication history for adherence issues, duplicate therapy, and safety concerns.

Goals
- Support safe and effective use of {medication}.
- Improve or stabilize symptoms related to {primary_diagnosis}.
- Reduce avoidable adverse events through monitoring and patient education.

Pharmacist interventions / plan
- Review patient records and current medication history.
- Confirm medication instructions, expected benefits, and common side effects with the patient.
- Coordinate with the referring provider if clinical information is incomplete.
- Document care plan completion for pharmacy workflow and reporting.

Monitoring plan
- Track patient response after therapy starts.
- Monitor for medication side effects and adherence concerns.
- Follow up based on provider instructions and pharmacy protocol.

Source notes
- Medication history: {medication_history or "Not provided"}
- Patient records summary: {patient_records or "Not provided"}
"""


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
    }
    ORDERS[order_id] = order

    try:
        order["care_plan"] = build_care_plan(data)
        order["status"] = "completed"
    except Exception:
        order["status"] = "failed"
        order["care_plan"] = ""

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
