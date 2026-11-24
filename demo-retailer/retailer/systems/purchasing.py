"""Purchasing, version 1: suppliers, purchase orders, goods received and supplier invoices."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "purchasing"
TITLE = "Purchasing"
LINE = "Suppliers, purchase orders, goods received and supplier invoices, with the matches saved on the invoices."

INVOICE_FIELDS = ("invoice_number, supplier_id, supplier_name, invoice_date, due_date, po_number (the purchase order number printed on "
                  "the invoice), status (received, queried or approved), net, tax, total and currency")


class MatchLine(BaseModel):
    field: Literal["price", "quantity", "item", "not_on_order", "not_received"] = Field(
        ..., description="What was compared on this line: price, quantity, item, not_on_order (the invoice line is not on the order) "
                         "or not_received (the invoice asks for more than was received).")
    item: str = Field(..., min_length=1, description="The item as the invoice names it, for example Pizza flour, 25 kg bag.")
    invoice_says: str = Field(..., description="What the invoice says for this field, for example 46.00 per bag.")
    order_says: str = Field(..., description="What the purchase order says for this field, for example 44.50 per bag. Write none if the "
                                              "item is not on the order.")
    received: str = Field("", description="What the goods receipts say was received, for example 600 bags. Leave empty if it does not apply.")
    mark: Literal["agrees", "price_differs", "quantity_differs", "not_on_order", "not_received"] = Field(
        ..., description="The result for this line.")
    net_difference: float = Field(0.0, description="The difference in net amount in US dollars: what the invoice charges above what the "
                                                   "order and the goods received support. 0 when the line agrees.")


class InvoiceMatch(BaseModel):
    lines: list[MatchLine] = Field(..., min_length=1, description="One entry for each comparison that was made.")
    proposed_next_step: Literal["ready_for_approval", "query_the_supplier", "refer_to_the_buyer"] = Field(
        ..., description="What the drafter proposes for the whole invoice. ready_for_approval: everything agrees. "
                         "query_the_supplier: the invoice charges for something the order or the receipts do not support. "
                         "refer_to_the_buyer: the buyer must decide. A person decides.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ApproveBody(BaseModel):
    approved_by: str = Field(..., min_length=1, description="The person who approves the invoice for payment. Free text.")
    note: str = Field("", description="Optional note kept with the approval.")


class QueryBody(BaseModel):
    raised_by: str = Field(..., min_length=1, description="The person who raises the query. Free text.")
    message: str = Field(..., min_length=1, description="The message to the supplier, in plain sentences.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds suppliers, purchase orders, goods receipts and supplier invoices. Saving a match "
                                  "is a draft. Approving an invoice for payment and raising a query change a record.")
    st = ctx.store
    d = lambda: st.data

    def supplier_or_404(i):
        s = d()["suppliers"].get(i)
        if not s:
            raise not_found("supplier", i, "Use list_suppliers to find supplier ids.")
        return s

    def po_or_404(i):
        p = d()["purchase_orders"].get(i)
        if not p:
            raise not_found("purchase order", i, "Use list_purchase_orders to find purchase order numbers.")
        return p

    def invoice_or_404(i):
        x = d()["supplier_invoices"].get(i)
        if not x:
            raise not_found("supplier invoice", i, "Use list_supplier_invoices to find invoice numbers.")
        return x

    inv_p = Path(..., description="Invoice number, for example INV-77102.")

    @reg(app, "get", "/suppliers", "list_suppliers", "List suppliers",
         "List the suppliers: supplier_id, name, supplies, town, contact_name, contact_email, payment_terms_days and currency.")
    def list_suppliers():
        return listing(sorted(d()["suppliers"].values(), key=lambda s: s["supplier_id"]))

    @reg(app, "get", "/suppliers/{supplier_id}", "get_supplier", "Get one supplier",
         "Read one supplier: supplier_id, name, supplies, town, contact, payment terms, and the numbers of its purchase orders "
         "(purchase_orders) and supplier invoices (invoices). Find the id with list_suppliers, for example SUP-301.")
    def get_supplier(supplier_id: str = Path(..., description="Supplier id, for example SUP-301.")):
        s = supplier_or_404(supplier_id)
        return {**s, "purchase_orders": sorted(p["po_number"] for p in d()["purchase_orders"].values() if p["supplier_id"] == supplier_id),
                "invoices": sorted(i["invoice_number"] for i in d()["supplier_invoices"].values() if i["supplier_id"] == supplier_id)}

    @reg(app, "get", "/purchase-orders", "list_purchase_orders", "List purchase orders",
         "List purchase orders, sorted by number. Each row has po_number, supplier_id, supplier_name, order_date, buyer, status "
         "(part_received or received) and net_total. Filters are optional: supplier_id and status. Read the lines with "
         "get_purchase_order.")
    def list_purchase_orders(supplier_id: str | None = Query(None, description="Only orders of this supplier, for example SUP-301."),
                             status: Literal["part_received", "received"] | None = Query(None, description="Only orders with this status.")):
        keys = ("po_number", "supplier_id", "supplier_name", "order_date", "buyer", "status", "net_total", "currency")
        rows = [{k: p[k] for k in keys} for p in d()["purchase_orders"].values()
                if (not supplier_id or p["supplier_id"] == supplier_id) and (not status or p["status"] == status)]
        return listing(sorted(rows, key=lambda p: p["po_number"]))

    @reg(app, "get", "/purchase-orders/{po_number}", "get_purchase_order", "Get one purchase order",
         "Read one purchase order: po_number, supplier, order_date, buyer (the buyer's name), status, net_total and lines. Each "
         "line has line_no, item, unit, quantity_ordered, unit_price in US dollars, quantity_received (so far) and the buyer. "
         "Also goods_receipt_ids and invoice_numbers that refer to this order. Find the number with list_purchase_orders or "
         "from the po_number printed on an invoice.")
    def get_purchase_order(po_number: str = Path(..., description="Purchase order number, for example PO-450112.")):
        p = po_or_404(po_number)
        return {**p, "goods_receipt_ids": sorted(r["receipt_id"] for r in d()["goods_receipts"].values() if r["po_number"] == po_number),
                "invoice_numbers": sorted(i["invoice_number"] for i in d()["supplier_invoices"].values() if i["po_number"] == po_number)}

    @reg(app, "get", "/goods-receipts", "list_goods_receipts", "List goods receipts",
         "List goods receipts, sorted by id: receipt_id, po_number, supplier, received_on, received_by, delivery_note and lines "
         "(line_no, item, unit, quantity_received). The filter po_number gives only the receipts for that order. An unknown "
         "po_number is refused with 404.")
    def list_goods_receipts(po_number: str | None = Query(None, description="Only receipts for this purchase order, for example PO-450158.")):
        if po_number:
            po_or_404(po_number)
        rows = [r for r in d()["goods_receipts"].values() if not po_number or r["po_number"] == po_number]
        return listing(sorted(rows, key=lambda r: r["receipt_id"]))

    @reg(app, "get", "/invoices", "list_supplier_invoices", "List supplier invoices",
         f"List supplier invoices, oldest first. Each row has {INVOICE_FIELDS}. Filters are optional: status "
         "(received, queried or approved) and supplier_id. Read the lines and the text with get_supplier_invoice.")
    def list_supplier_invoices(status: Literal["received", "queried", "approved"] | None = Query(None, description="Only invoices with this status."),
                               supplier_id: str | None = Query(None, description="Only invoices of this supplier, for example SUP-302.")):
        keys = ("invoice_number", "supplier_id", "supplier_name", "invoice_date", "due_date", "po_number", "status", "net", "tax",
                "total", "currency")
        rows = [{k: i[k] for k in keys} for i in d()["supplier_invoices"].values()
                if (not status or i["status"] == status) and (not supplier_id or i["supplier_id"] == supplier_id)]
        return listing(sorted(rows, key=lambda i: (i["invoice_date"], i["invoice_number"])))

    @reg(app, "get", "/invoices/{invoice_number}", "get_supplier_invoice", "Get one supplier invoice",
         f"Read one supplier invoice: {INVOICE_FIELDS}; lines (line_no, item, unit, quantity, unit_price, amount); text (the invoice "
         "as printed, in plain text); matches (every saved match, each a version); query (the message to the supplier, if one was "
         "raised) and approved_by. Compare it with get_purchase_order for the po_number and with list_goods_receipts.")
    def get_supplier_invoice(invoice_number: str = inv_p):
        return invoice_or_404(invoice_number)

    @reg(app, "post", "/invoices/{invoice_number}/match", "save_invoice_match", "Save the match of an invoice (draft)",
         "Save the result of matching one invoice with its purchase order and goods receipts, as a draft. It changes no status. "
         "Each call is kept as a new version with who wrote it and when. Send lines (each with field, item, invoice_says, "
         "order_says, received, mark and net_difference), a proposed_next_step for the whole invoice, an optional summary and "
         "drafted_by. A person decides what happens next. Returns the saved version.")
    def save_invoice_match(body: InvoiceMatch, invoice_number: str = inv_p):
        inv = invoice_or_404(invoice_number)
        payload = {"lines": [x.model_dump() for x in body.lines], "proposed_next_step": body.proposed_next_step,
                   "summary": body.summary}
        v = st.add_draft(inv, "matches", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "invoice_status": inv["status"]}

    @reg(app, "post", "/invoices/{invoice_number}/approve", "approve_invoice_for_payment", "Approve an invoice for payment (change)",
         "Approve one invoice for payment. This is a change: the status becomes approved. Needs approved_by. Refused with 409 until "
         "a match has been saved for the invoice with save_invoice_match, and when the invoice is already approved.")
    def approve_invoice_for_payment(body: ApproveBody, invoice_number: str = inv_p):
        inv = invoice_or_404(invoice_number)
        with st.lock:
            if inv["status"] == "approved":
                raise conflict(f"Invoice {invoice_number} is already approved by {inv['approved_by']}. Nothing was changed.")
            if not inv["matches"]:
                raise conflict(f"No match is saved for invoice {invoice_number}. Nothing was changed. Use save_invoice_match first.")
            inv.update(status="approved", approved_by=body.approved_by, approved_at=now_iso(), approval_note=body.note)
            st.save()
        return {"applied": True, "kind": "change", "status": "approved", "invoice": inv}

    @reg(app, "post", "/invoices/{invoice_number}/query", "raise_invoice_query", "Raise a query with the supplier (change)",
         "Raise a query with the supplier about one invoice. This is a change: the status becomes queried. Needs raised_by and "
         "the message to the supplier. Refused with 409 when the invoice is already queried or already approved.")
    def raise_invoice_query(body: QueryBody, invoice_number: str = inv_p):
        inv = invoice_or_404(invoice_number)
        with st.lock:
            if inv["status"] == "queried":
                raise conflict(f"Invoice {invoice_number} is already queried. Nothing was changed.")
            if inv["status"] == "approved":
                raise conflict(f"Invoice {invoice_number} is already approved. Nothing was changed.")
            inv["status"] = "queried"
            inv["query"] = {"raised_by": body.raised_by, "raised_at": now_iso(), "message": body.message,
                            "to": d()["suppliers"][inv["supplier_id"]]["contact_email"]}
            st.save()
        return {"applied": True, "kind": "change", "status": "queried", "invoice": inv}

    return app
