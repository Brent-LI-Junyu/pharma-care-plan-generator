# Care Plan Generator Design Doc

## 1. Problem Statement

A specialty pharmacy needs a tool to automatically generate care plans based on patient clinical information. Today, pharmacists manually review patient records and write care plans, which takes around 20-40 minutes per patient. Because the pharmacy is short-staffed and care plans are required for compliance and reimbursement, this manual process creates a backlog.

The goal of this system is to let healthcare staff enter patient and order information through a web form, generate a care plan using an LLM, and download the generated care plan for use in the pharmacy workflow.

## 2. Users

The primary users are healthcare staff at CVS or a specialty pharmacy. Patients do not directly use this system.

Initial user assumptions:

- Medical assistants or healthcare staff enter patient, provider, diagnosis, medication, and patient record information.
- Pharmacists may review or use the generated care plan.
- The generated care plan can be downloaded or printed for patient-facing or internal workflow use.

## 3. MVP Scope

The MVP should support:

- A web form for entering patient, provider, diagnosis, medication, medication history, and patient record information.
- Input validation for required fields and known formats.
- Duplicate patient and duplicate order detection.
- Provider uniqueness validation.
- LLM-based care plan generation.
- Care plan download as a text file.
- Basic export for pharma reporting.

## 4. Non-Goals

The first version will not focus on:

- Full user authentication and role-based permissions.
- Advanced PDF parsing.
- Manual pharmacist editing workflow.
- Complex audit log system.
- Production AWS deployment.
- Real-time notification or WebSocket updates.
- Advanced monitoring dashboards.

These may be added in later iterations.

## 5. Core Workflow

1. A healthcare staff member opens the web form.
2. The user enters patient, provider, diagnosis, medication, and patient record information.
3. The system validates required fields and field formats.
4. The system checks for duplicate patients, duplicate orders, and provider conflicts.
5. If there is an error, the system blocks submission and asks the user to fix the issue.
6. If there is a warning, the system shows the warning and allows the user to confirm and continue.
7. The system calls an LLM to generate the care plan.
8. The generated care plan is saved and made available for download.
9. The order and care plan data can be exported for reporting.

## 6. Data Model

Initial core entities:

### Patient

Represents a patient receiving medication therapy.

Fields:

- first_name
- last_name
- date_of_birth
- mrn
- primary_diagnosis
- additional_diagnoses
- medication_history
- patient_records

### Provider

Represents the referring provider.

Fields:

- name
- npi

Provider uniqueness is based on NPI.

### Order

Represents a medication order for a patient.

Fields:

- patient
- provider
- medication_name
- order_date
- status

One patient can have many orders. One order belongs to one patient and one provider.

### CarePlan

Represents the generated care plan for an order.

Fields:

- order
- content
- generated_at
- status
- error_message

One care plan corresponds to one order.

## 7. API Design

Initial API endpoints:

### POST /api/orders

Creates a new order and generates a care plan.

Request includes:

- patient information
- provider information
- diagnosis information
- medication information
- patient records

Response includes:

- order id
- care plan id
- care plan content or generation status
- errors or warnings if applicable

### GET /api/care-plans/{id}

Returns a generated care plan.

Response includes:

- care plan id
- order id
- content
- status

### GET /api/reports/export

Exports order and care plan data for reporting.

Response:

- CSV or downloadable report file

## 8. Validation and Duplicate Rules

Validation errors block submission.

Examples:

- Missing required fields.
- NPI is not a 10-digit number.
- MRN is not in the expected format.
- ICD-10 code is not in the expected format.
- NPI already exists with a different provider name.

Warnings do not always block submission. The user may confirm and continue.

Duplicate and warning rules:

- Same patient + same medication + same day = ERROR.
- Same patient + same medication + different day = WARNING.
- Same MRN + different name or DOB = WARNING.
- Same name + same DOB + different MRN = WARNING.
- Same NPI + different provider name = ERROR.

## 9. Care Plan Output

The generated care plan must include:

- Problem list / Drug therapy problems
- Goals
- Pharmacist interventions / plan
- Monitoring plan and lab schedule

For MVP, the care plan can be downloaded as a text file.

## 10. Risks and Future Improvements

Risks:

- LLM output may be incomplete, inconsistent, or clinically inaccurate.
- LLM API calls may fail or time out.
- Patient records may include PHI and require careful handling.
- Duplicate detection may produce false positives or false negatives.
- Reporting requirements may change based on pharma or Medicare needs.

Future improvements:

- Async background processing with Celery and Redis.
- Real-time status updates using polling or WebSocket.
- Better error handling and retry logic.
- Adapter pattern for multiple order data sources.
- Dockerized local development.
- AWS deployment with SQS, Lambda, RDS, and S3.
- Monitoring with Prometheus and Grafana.
