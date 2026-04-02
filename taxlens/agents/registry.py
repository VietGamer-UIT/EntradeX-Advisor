"""Registered agents — workflows with programmatic intelligence and RAG integration."""

from __future__ import annotations

from typing import Any
import pandas as pd

from taxlens.agents.base import AgentResult, AuditAgent, record_agent_audit
from taxlens.rag.pipeline import build_index_from_knowledge_dir, query_with_citations


class BankReconciliationAgent(AuditAgent):
    name = "BankReconciliation"

    def run(self, context: dict[str, Any]) -> AgentResult:
        # Context expects {"bank_rows": [...], "ledger_rows": [...]}
        bank_rows = context.get("bank_rows", [])
        ledger_rows = context.get("ledger_rows", [])

        steps = [
            "Step 1: Ingest bank statement lines and GL records.",
        ]

        if not bank_rows or not ledger_rows:
            steps.append("Step 2: Missing data. Cannot perform reconciliation.")
            result = AgentResult(
                agent_name=self.name,
                steps=steps,
                structured_output={"matches": [], "unmatched_bank": bank_rows, "unmatched_ledger": ledger_rows},
                confidence=0.0,
                requires_human_review=True,
            )
            record_agent_audit(self.name, result, input_summary={"bank_count": len(bank_rows), "ledger_count": len(ledger_rows)})
            return result

        steps.append("Step 2: Match to GL by exact amount.")
        
        df_bank = pd.DataFrame(bank_rows)
        df_ledger = pd.DataFrame(ledger_rows)

        # Normalize amount columns if possible
        if 'amount' not in df_bank.columns and len(df_bank.columns) > 0:
            df_bank['amount'] = df_bank.get('so_tien', df_bank.iloc[:, -1])
        if 'amount' not in df_ledger.columns and len(df_ledger.columns) > 0:
            df_ledger['amount'] = df_ledger.get('so_tien', df_ledger.iloc[:, -1])

        # Convert amounts to float for matching
        df_bank['amount_num'] = pd.to_numeric(df_bank.get('amount', 0), errors='coerce').fillna(0)
        df_ledger['amount_num'] = pd.to_numeric(df_ledger.get('amount', 0), errors='coerce').fillna(0)

        matches = []
        unmatched_ledger = []
        
        # Simple greedy matching by amount
        used_bank_idx = set()
        for idx_l, row_l in df_ledger.iterrows():
            matched = False
            for idx_b, row_b in df_bank.iterrows():
                if idx_b in used_bank_idx:
                    continue
                if abs(row_l['amount_num'] - row_b['amount_num']) < 0.01:
                    matches.append({
                        "ledger": row_l.to_dict(),
                        "bank": row_b.to_dict()
                    })
                    used_bank_idx.add(idx_b)
                    matched = True
                    break
            if not matched:
                unmatched_ledger.append(row_l.to_dict())

        unmatched_bank = [row.to_dict() for i, row in df_bank.iterrows() if i not in used_bank_idx]

        steps.append(f"Step 3: Found {len(matches)} matches. Unmatched Bank: {len(unmatched_bank)}, Unmatched Ledger: {len(unmatched_ledger)}.")
        
        confidence = len(matches) / max(len(ledger_rows), 1)

        result = AgentResult(
            agent_name=self.name,
            steps=steps,
            structured_output={
                "matches": matches, 
                "unmatched_bank": unmatched_bank,
                "unmatched_ledger": unmatched_ledger
            },
            confidence=round(confidence, 2),
            requires_human_review=True,
        )
        record_agent_audit(self.name, result, input_summary={"keys": list(context.keys())})
        return result


class TransferPricingAgent(AuditAgent):
    name = "TransferPricingAnalysis"

    def run(self, context: dict[str, Any]) -> AgentResult:
        tx_data = context.get("tx", [])
        
        steps = [
            "Step 1: Load related-party transaction list.",
        ]
        
        if not tx_data:
            steps.append("Step 2: No transaction data provided.")
            result = AgentResult(
                agent_name=self.name,
                steps=steps,
                structured_output={"flagged_tx": [], "message": "No data to analyze."},
                confidence=0.0,
                requires_human_review=False,
            )
            return result
            
        df = pd.DataFrame(tx_data)
        steps.append("Step 2: Benchmark margins using Inter-Quartile Range (IQR) bounds.")
        
        # Assume 'margin' or 'price' column exists
        col_to_check = 'margin' if 'margin' in df.columns else ('price' if 'price' in df.columns else None)
        
        if not col_to_check:
             steps.append("Step 3: Missing 'margin' or 'price' column for analysis. Skipping.")
             result = AgentResult(
                agent_name=self.name,
                steps=steps,
                structured_output={"flagged_tx": tx_data, "message": "Columns missing."},
                confidence=0.2,
                requires_human_review=True,
             )
             return result
             
        df['num_val'] = pd.to_numeric(df[col_to_check], errors='coerce').fillna(0)
        q1 = df['num_val'].quantile(0.25)
        q3 = df['num_val'].quantile(0.75)
        iqr = q3 - q1
        lower_bound = float(q1 - 1.5 * iqr)
        upper_bound = float(q3 + 1.5 * iqr)
        
        df['outlier'] = (df['num_val'] < lower_bound) | (df['num_val'] > upper_bound)
        flagged = df[df['outlier']].drop(columns=['num_val', 'outlier']).to_dict(orient='records')
        
        steps.append(f"Step 3: Ranked by deviation. Found {len(flagged)} outlier transactions outside arm's length range [{lower_bound:.2f}, {upper_bound:.2f}].")

        result = AgentResult(
            agent_name=self.name,
            steps=steps,
            structured_output={"flagged_tx": flagged, "bounds": {"lower": lower_bound, "upper": upper_bound}},
            confidence=0.85,
            requires_human_review=True,
        )
        record_agent_audit(self.name, result, input_summary={"tx_count": len(tx_data)})
        return result


class AuditReportDraftAgent(AuditAgent):
    name = "AuditReportDrafting"
    
    def __init__(self, index: Any | None = None) -> None:
        self._index = index

    def _ensure_index(self) -> Any:
        if self._index is None:
            try:
                self._index = build_index_from_knowledge_dir()
            except (RuntimeError, FileNotFoundError):
                pass
        return self._index

    def run(self, context: dict[str, Any]) -> AgentResult:
        sections = context.get("sections", [])
        
        steps = [
            "Step 1: Aggregate findings from risk engine and agents.",
            "Step 2: Automatically generate draft observations."
        ]
        
        drafts = []
        idx = self._ensure_index()
        citations_all = []
        
        for section in sections:
            topic = section.get("topic", "General Audit")
            notes = section.get("notes", "")
            
            draft_text = f"DRAFT OBSERVATION [{topic}]: Based on preliminary findings, {notes}. Human edits required."
            
            # If we have RAG index successfully loaded, enrich it.
            if idx is not None:
                steps.append(f"Querying knowledge base for legal wording on: {topic}...")
                try:
                    query = f"Provide standard audit disclosure wording focusing on: {topic} and the fact that {notes}. Limit strictly to local tax/IFRS guidelines."
                    cited = query_with_citations(idx, query)
                    if not cited.insufficient_legal_basis:
                        draft_text += f"\n\nSuggested Disclosures:\n{cited.text}"
                        citations_all.extend(cited.citations)
                except Exception as exc:
                     steps.append(f"Warning: RAG unavailable for {topic} - {exc}")
                     
            drafts.append({
                "topic": topic,
                "text": draft_text
            })

        steps.append("Step 3: Emit draft sections marked DRAFT — human edits required.")
        
        citations_all = list(set(citations_all))
        
        result = AgentResult(
            agent_name=self.name,
            steps=steps,
            structured_output={"draft_sections": drafts},
            confidence=0.7,
            requires_human_review=True,
            citations=citations_all
        )
        record_agent_audit(self.name, result, input_summary={"sections_count": len(sections)})
        return result
