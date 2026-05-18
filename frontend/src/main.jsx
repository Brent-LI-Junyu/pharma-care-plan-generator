import React, { useState } from "react";
import { createRoot } from "react-dom/client";
import { Download, FileText, Search, Send } from "lucide-react";
import "./styles.css";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const initialForm = {
  patient_first_name: "Alex",
  patient_last_name: "Brown",
  patient_mrn: "123456",
  referring_provider: "Dr. Jane Smith",
  referring_provider_npi: "1234567890",
  primary_diagnosis: "G70.00",
  additional_diagnoses: "I10, K21.9",
  medication_name: "IVIG",
  medication_history: "Pyridostigmine 60 mg PO q6h PRN; Prednisone 10 mg PO daily",
  patient_records:
    "Patient has progressive proximal muscle weakness and ptosis. Neurology recommends IVIG for rapid symptomatic control.",
};

function App() {
  const [form, setForm] = useState(initialForm);
  const [order, setOrder] = useState(null);
  const [searchId, setSearchId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function submitOrder(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setOrder(null);

    try {
      const response = await fetch(`${API_BASE}/api/orders/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to create order.");
      }

      setOrder(data);
      setSearchId(data.id);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function searchOrder() {
    if (!searchId.trim()) return;

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_BASE}/api/orders/${searchId.trim()}/`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Order not found.");
      }

      setOrder(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function downloadCarePlan() {
    if (!order?.id) return;
    window.location.href = `${API_BASE}/api/orders/${order.id}/download/`;
  }

  return (
    <main className="app-shell">
      <section className="workspace">
        <form className="panel form-panel" onSubmit={submitOrder}>
          <div className="section-heading">
            <FileText size={22} aria-hidden="true" />
            <div>
              <h1>Care Plan Generator</h1>
              <p>Day 2 MVP: submit an order and generate a care plan synchronously.</p>
            </div>
          </div>

          <div className="grid two">
            <label>
              First name
              <input name="patient_first_name" value={form.patient_first_name} onChange={updateField} />
            </label>
            <label>
              Last name
              <input name="patient_last_name" value={form.patient_last_name} onChange={updateField} />
            </label>
          </div>

          <div className="grid two">
            <label>
              MRN
              <input name="patient_mrn" value={form.patient_mrn} onChange={updateField} />
            </label>
            <label>
              Medication
              <input name="medication_name" value={form.medication_name} onChange={updateField} />
            </label>
          </div>

          <div className="grid two">
            <label>
              Provider
              <input name="referring_provider" value={form.referring_provider} onChange={updateField} />
            </label>
            <label>
              Provider NPI
              <input name="referring_provider_npi" value={form.referring_provider_npi} onChange={updateField} />
            </label>
          </div>

          <div className="grid two">
            <label>
              Primary diagnosis
              <input name="primary_diagnosis" value={form.primary_diagnosis} onChange={updateField} />
            </label>
            <label>
              Additional diagnoses
              <input name="additional_diagnoses" value={form.additional_diagnoses} onChange={updateField} />
            </label>
          </div>

          <label>
            Medication history
            <textarea name="medication_history" rows="3" value={form.medication_history} onChange={updateField} />
          </label>

          <label>
            Patient records
            <textarea name="patient_records" rows="5" value={form.patient_records} onChange={updateField} />
          </label>

          <button className="primary-button" type="submit" disabled={loading}>
            <Send size={18} aria-hidden="true" />
            {loading ? "Generating..." : "Generate Care Plan"}
          </button>
        </form>

        <section className="panel result-panel">
          <div className="search-row">
            <input
              value={searchId}
              onChange={(event) => setSearchId(event.target.value)}
              placeholder="Order ID"
              aria-label="Order ID"
            />
            <button type="button" onClick={searchOrder} disabled={loading || !searchId.trim()} title="Search order">
              <Search size={18} aria-hidden="true" />
            </button>
          </div>

          {error && <div className="alert">{error}</div>}

          {!order && !error && (
            <div className="empty-state">
              <FileText size={32} aria-hidden="true" />
              <p>Submit an order to see the generated care plan.</p>
            </div>
          )}

          {order && (
            <div className="order-result">
              <div className="result-header">
                <div>
                  <span className={`status ${order.status}`}>{order.status}</span>
                  <h2>Order {order.id}</h2>
                </div>
                <button type="button" onClick={downloadCarePlan} disabled={order.status !== "completed"} title="Download care plan">
                  <Download size={18} aria-hidden="true" />
                </button>
              </div>

              {order.status === "completed" ? (
                <pre>{order.care_plan}</pre>
              ) : (
                <p className="muted">Care plan is not completed yet.</p>
              )}
            </div>
          )}
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
