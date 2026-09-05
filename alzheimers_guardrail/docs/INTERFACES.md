### ACTION OUTPUT (Gopika/Adithya → GSK)
{ "action": "SEND_DOCUMENT|DELETE_FILE|CANCEL_APPT|TRANSFER", 
  "target": { "recipient": "string", 
              "document_id": "string (optional)", 
              "amount": "number (for TRANSFER)" } }

### RISK OUTPUT (GSK → Gopika)
{ "score": 0.0-1.0, 
  "level": "LOW|MEDIUM|HIGH", 
  "factors": { "financial_impact": 0.0-1.0, 
               "data_sensitivity": 0.0-1.0, 
               "irreversibility": 0.0-1.0, 
               "external_recipient": 0.0-1.0, 
               "destructive_operation": 0.0-1.0, 
               "context_dependency": 0.0-1.0 }, 
  "triggers_context_gate": boolean }

### POLICY OUTPUT (GSK → Yazeen)
{ "requiredContext": ["recipient","document","previous_request"], 
  "allowedSources": ["messages","calendar","files"], 
  "maxContextItems": 3 }

### CONTEXT OUTPUT (Yazeen → Adithya)
{ "explanation": "string", 
  "privacy_log": { 
    "used": ["string"], 
    "not_used": ["string"] 
  } }