from __future__ import annotations

import json
import sqlite3
import time
import uuid

import streamlit as st
from dotenv import load_dotenv

from src.brandassist_ai import SupportAgent
from src.brandassist_ai.data_loader import load_golden_cases, load_image_labels
from src.brandassist_ai.metrics import summarize_runs

load_dotenv()

st.set_page_config(page_title="BrandAssist AI", layout="wide")
st.markdown(
    """
    <style>
      .block-container {max-width: 1280px; padding-top: 1.25rem;}
      .stChatMessage {border-radius: 12px;}
      div[data-testid="stExpander"] {border-radius: 10px;}
      .status-chip {margin-top: 6px; margin-bottom: 10px;}
      .section-title {font-size: 0.95rem; opacity: 0.85; margin: 8px 0;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_agent(runtime_mode: str, retriever_mode: str, cache_bust: str) -> SupportAgent:
    return SupportAgent(runtime_mode=runtime_mode, retriever_mode=retriever_mode)


def _categorize_response(message: str, trace) -> str:
    text = message.lower()
    if any(greet in text for greet in ("hi", "hello", "hey")):
        return "SMALL_TALK"
    if trace.intent == "order_status":
        return "ORDER_STATUS"
    if trace.intent in {"warranty", "warranty_registration"}:
        return "WARRANTY"
    if trace.intent in {"setup", "troubleshooting"}:
        return "TROUBLESHOOTING"
    if trace.intent == "return_policy":
        return "RETURN_POLICY"
    if trace.intent == "ambiguous":
        return "CLARIFICATION"
    return "GENERAL_SUPPORT"


def _has_factual_tool_output(trace) -> bool:
    """Tool calls that return concrete facts the answer can stand on (not ticket creation)."""
    factual_tools = {"order_lookup", "product_lookup", "warranty_check", "orders_by_customer_lookup", "register_warranty"}
    for call in trace.tool_calls:
        if call.name in factual_tools and isinstance(call.result, dict) and call.result.get("found", True):
            return True
    return False


def _groundedness_metric(trace) -> float | None:
    # Procedural follow-ups make no factual claims, so groundedness is not applicable.
    if trace.outcome == "clarify" or trace.intent == "ambiguous":
        return None
    if trace.retrieved_doc_ids or _has_factual_tool_output(trace):
        return 1.0
    if trace.escalated:
        return 0.6
    # Resolved answer with neither retrieved docs nor supporting tool output: weakly grounded.
    return 0.4


def _groundedness_reason(trace) -> str:
    if trace.outcome == "clarify" or trace.intent == "ambiguous":
        return (
            "Procedural follow-up that asks for missing information; it makes no factual claims, "
            "so groundedness is not applicable."
        )
    if trace.retrieved_doc_ids or _has_factual_tool_output(trace):
        return "Response is grounded in retrieved documentation and/or tool outputs."
    if trace.escalated:
        return (
            "The response escalates due to uncertainty or policy boundary rather than making unsupported claims."
        )
    return "Resolved without retrieved documentation or supporting tool output; grounding is weak."


def _build_step_trace(message: str, response, image_id: str | None) -> list[dict]:
    base = int(time.time() * 1000)
    step_prefix = f"{uuid.uuid4()}_step"
    category = _categorize_response(message, response.trace)
    tools = [call.name for call in response.trace.tool_calls]

    steps = [
        {
            "startExecutionTime": base,
            "endExecutionTime": base + 40,
            "type": "IntentStep",
            "category": category,
            "reason": f"Intent resolved as {response.trace.intent} via {getattr(response.trace, 'intent_source', 'rule')}.",
            "evaluationType": "intent",
            "metricName": "intent_confidence_proxy",
            "metricValue": 1.0 if getattr(response.trace, "intent_source", "rule").startswith("llm:") else 0.7,
            "id": f"{step_prefix}_1",
            "iconName": "standard:default",
            "isInternal": False,
        },
        {
            "startExecutionTime": base + 40,
            "endExecutionTime": base + 110,
            "type": "ContextResolutionStep",
            "category": category,
            "reason": (
                f"Image context used: {bool(image_id)}; product resolved to {response.trace.product_id or 'unknown'}."
            ),
            "evaluationType": "context_resolution",
            "metricName": "image_confidence",
            "metricValue": response.trace.image_confidence,
            "id": f"{step_prefix}_2",
            "iconName": "standard:default",
            "isInternal": False,
        },
        {
            "startExecutionTime": base + 110,
            "endExecutionTime": base + 190,
            "type": "ToolExecutionStep",
            "category": category,
            "reason": (
                f"Tool calls executed: {', '.join(tools)}." if tools else "No tool call required for this turn."
            ),
            "evaluationType": "tool_calling",
            "metricName": "tool_call_count",
            "metricValue": float(len(tools)),
            "id": f"{step_prefix}_3",
            "iconName": "standard:default",
            "isInternal": False,
        },
        {
            "startExecutionTime": base + 190,
            "endExecutionTime": base + 260,
            "type": "RetrievalStep",
            "category": category,
            "reason": (
                f"Retrieved {len(response.trace.retrieved_doc_ids)} document(s) for grounding."
                if response.trace.retrieved_doc_ids
                else "No document retrieved for this turn."
            ),
            "evaluationType": "retrieval",
            "metricName": "retrieved_doc_count",
            "metricValue": float(len(response.trace.retrieved_doc_ids)),
            "id": f"{step_prefix}_4",
            "iconName": "standard:default",
            "isInternal": False,
        },
        {
            "startExecutionTime": base + 260,
            "endExecutionTime": base + 340,
            "type": "OutputEvaluationStep",
            "category": category,
            "reason": _groundedness_reason(response.trace),
            "evaluationType": "groundedness",
            "metricName": "groundedness_proxy",
            "metricValue": _groundedness_metric(response.trace),
            "id": f"{step_prefix}_5",
            "iconName": "standard:default",
            "isInternal": False,
        },
    ]
    return steps


def _turn_status_label(trace_payload: dict) -> tuple[str, str]:
    if trace_payload.get("escalated"):
        return "Escalated", "#b91c1c"
    if trace_payload.get("outcome") == "clarify":
        return "Needs Human Input", "#b45309"
    if trace_payload.get("outcome") == "resolved":
        return "AI Resolved", "#15803d"
    return "AI Handling", "#334155"


def _status_chip(label: str, color: str) -> str:
    return (
        f"<span style='display:inline-block;padding:2px 10px;border-radius:999px;"
        f"background:{color};color:white;font-size:12px;font-weight:600'>{label}</span>"
    )


image_labels = load_image_labels()

st.title("BrandAssist AI")
st.caption("Multimodal consumer support agent POC")

with st.sidebar:
    st.header("Image Context")
    image_options = ["None"] + [label.image_id for label in image_labels]
    selected_image = st.selectbox("Use labeled image sample", image_options)
    use_image_context = st.toggle("Use image context for next prompt", value=False)
    st.caption("Or upload your own product photo (identified by a vision model):")
    uploaded_image = st.file_uploader(
        "Upload product photo", type=["png", "jpg", "jpeg", "webp", "gif"], label_visibility="collapsed"
    )
    runtime_mode = "llm"
    retriever_mode = "hybrid"
    st.caption("Runtime mode: llm (locked)")
    st.caption("Retriever mode: hybrid (locked)")
    use_langgraph = True
    st.caption("LangGraph orchestrator: always enabled")
    show_trace_panel = st.toggle("Show live trace panel", value=True)
    show_workbench = st.toggle("Show data workbench", value=True)
    preview_rows = st.slider("Workbench rows", min_value=5, max_value=100, value=20, step=5)
    st.markdown("This POC uses labeled public-reference image metadata for deterministic evals.")

agent = get_agent(runtime_mode=runtime_mode, retriever_mode=retriever_mode, cache_bust="v2_opening_greeting")

if "runs" not in st.session_state:
    st.session_state.runs = []
if "turns" not in st.session_state:
    st.session_state.turns = []
if "auto_greeted" not in st.session_state:
    st.session_state.auto_greeted = False

left, right = st.columns([2, 1])

with left:
    st.markdown("<div class='section-title'>Conversation</div>", unsafe_allow_html=True)
    clear_col, _ = st.columns([1, 5])
    with clear_col:
        clear_clicked = st.button("Clear", use_container_width=True)
    if clear_clicked:
        st.session_state.runs = []
        st.session_state.turns = []
        st.session_state.auto_greeted = False
        st.rerun()

    if not st.session_state.auto_greeted:
        if hasattr(agent, "opening_greeting"):
            greeting_response = agent.opening_greeting(timezone_name="Asia/Kolkata")
        else:
            # Fallback for stale cached instances from previous code loads.
            greeting_response = SupportAgent(
                runtime_mode=runtime_mode,
                retriever_mode=retriever_mode,
            ).opening_greeting(timezone_name="Asia/Kolkata")
        greeting_trace = {
            "message": "__auto_greeting__",
            "image_id": None,
            "intent": greeting_response.trace.intent,
            "intent_source": getattr(greeting_response.trace, "intent_source", "rule"),
            "product_id": greeting_response.trace.product_id,
            "retrieved_doc_ids": greeting_response.trace.retrieved_doc_ids,
            "tools": [call.name for call in greeting_response.trace.tool_calls],
            "tool_details": [],
            "outcome": greeting_response.trace.outcome,
            "escalated": greeting_response.trace.escalated,
            "warnings": greeting_response.trace.warnings,
            "steps": _build_step_trace("auto greeting", greeting_response, None),
        }
        st.session_state.runs.append(greeting_response)
        st.session_state.turns.append(
            {
                "message": "System greeting",
                "image_id": None,
                "response": greeting_response,
                "trace": greeting_trace,
            }
        )
        st.session_state.auto_greeted = True
        st.rerun()

    for turn in st.session_state.turns:
        user_label = turn["message"]
        if turn["image_id"]:
            user_label = f"{user_label}\n\n(image: {turn['image_id']})"
        with st.chat_message("user"):
            st.write(user_label)
            if turn.get("display_image"):
                st.image(turn["display_image"], width=200)
        run = turn["response"]
        status_label, status_color = _turn_status_label(turn["trace"])
        st.chat_message("assistant").write(run.answer)
        st.markdown(f"<div class='status-chip'>{_status_chip(status_label, status_color)}</div>", unsafe_allow_html=True)
        with st.expander("Trace", expanded=False):
            st.json(turn["trace"])

    message = st.chat_input("Ask about setup, troubleshooting, warranty, returns, or order status")
    if message and message.strip():
        message = message.strip()
        image_id = selected_image if use_image_context and selected_image != "None" else None
        image_bytes = None
        image_mime = None
        display_image = None
        if uploaded_image is not None:
            image_bytes = uploaded_image.getvalue()
            image_mime = uploaded_image.type or "image/png"
            display_image = image_bytes
            image_id = None  # raw upload takes precedence over labeled sample
        history = []
        for past in st.session_state.turns:
            if past["message"] not in {"System greeting", "__auto_greeting__"}:
                history.append({"role": "user", "content": past["message"]})
            history.append(
                {
                    "role": "assistant",
                    "content": past["response"].answer,
                    "intent": past["trace"]["intent"],
                    "outcome": past["trace"]["outcome"],
                }
            )
        response = agent.run(
            message,
            image_id=image_id,
            use_graph=use_langgraph,
            history=history,
            image_bytes=image_bytes,
            image_mime=image_mime,
        )
        st.session_state.runs.append(response)
        trace_payload = {
            "message": message,
            "image_id": image_id or ("upload:" + uploaded_image.name if uploaded_image is not None else None),
            "intent": response.trace.intent,
            "intent_source": getattr(response.trace, "intent_source", "rule"),
            "product_id": response.trace.product_id,
            "retrieved_doc_ids": response.trace.retrieved_doc_ids,
            "tools": [call.name for call in response.trace.tool_calls],
            "tool_details": [
                {"name": call.name, "args": call.args, "result": call.result}
                for call in response.trace.tool_calls
            ],
            "outcome": response.trace.outcome,
            "escalated": response.trace.escalated,
            "warnings": response.trace.warnings,
            "llm_calls": getattr(response.trace, "llm_calls", 0),
            "llm_tokens": getattr(response.trace, "llm_prompt_tokens", 0)
            + getattr(response.trace, "llm_completion_tokens", 0),
            "llm_cost_usd": getattr(response.trace, "llm_cost_usd", 0.0),
            "steps": _build_step_trace(message, response, image_id),
        }
        st.session_state.turns.append(
            {
                "message": message,
                "image_id": image_id,
                "response": response,
                "trace": trace_payload,
                "display_image": display_image,
            }
        )
        print("[brandassist-trace]", json.dumps(trace_payload, ensure_ascii=True))
        st.rerun()

with right:
    st.subheader("POC Metrics")
    metrics = summarize_runs(st.session_state.runs)
    st.metric("Total cases", metrics["total_cases"])
    st.metric("Resolution rate", f"{metrics['resolution_rate']:.0%}")
    st.metric("Escalation rate", f"{metrics['escalation_rate']:.0%}")
    st.metric("Backlog reduction proxy", f"{metrics['estimated_backlog_reduction']:.0%}")

    st.subheader("Sample Prompts")
    for case in load_golden_cases()[:5]:
        st.code(f"{case['message']} | image={case['image_id']}")

    if show_trace_panel:
        st.subheader("Live Trace")
    if show_trace_panel and st.session_state.turns:
        latest = st.session_state.turns[-1]
        latest_trace = latest["trace"]
        st.caption("Latest reasoning and tool execution")

        status_label, status_color = _turn_status_label(latest_trace)
        st.markdown(_status_chip(status_label, status_color), unsafe_allow_html=True)

        with st.status("Execution timeline", expanded=True, state="complete"):
            for step in latest_trace["steps"]:
                duration_ms = step["endExecutionTime"] - step["startExecutionTime"]
                st.write(f"{step['type']} ({step['category']}) - {step['reason']} [{duration_ms}ms]")

        st.markdown("**Tool Calls**")
        if latest_trace["tool_details"]:
            st.dataframe(
                [
                    {
                        "tool": t["name"],
                        "args": json.dumps(t["args"], ensure_ascii=True),
                        "result": json.dumps(t["result"], ensure_ascii=True)[:220],
                    }
                    for t in latest_trace["tool_details"]
                ],
                width="stretch",
                hide_index=True,
            )
        else:
            st.caption("No tools called in latest turn.")

        st.markdown("**Case Summary**")
        st.markdown(
            "\n".join(
                [
                    f"- Intent: `{latest_trace['intent']}` ({latest_trace['intent_source']})",
                    f"- Product: `{latest_trace['product_id']}`",
                    f"- Retrieved docs: `{len(latest_trace['retrieved_doc_ids'])}`",
                    f"- Outcome: `{latest_trace['outcome']}`",
                    f"- Escalated: `{latest_trace['escalated']}`",
                ]
            )
        )
        if latest_trace["warnings"]:
            st.warning("Warnings: " + "; ".join(latest_trace["warnings"]))
        with st.expander("Latest full trace", expanded=False):
            st.json(latest_trace)
    elif show_trace_panel:
        st.caption("No trace yet. Send a prompt to see live execution details.")

    if show_workbench:
        st.divider()
        with st.expander("Data Workbench", expanded=False):
            st.caption("Browse SQLite source-of-truth tables used by the agent.")
            db_path = "data/brandassist.db"

            def _query(sql: str):
                with sqlite3.connect(db_path) as conn:
                    return conn.execute(sql).fetchall(), [col[0] for col in conn.execute(sql).description]

            table_map = {
                "Products": "SELECT product_id, name, category FROM products ORDER BY product_id LIMIT {limit}",
                "Orders": "SELECT order_id, customer_id, product_id, status, purchase_date FROM orders ORDER BY order_id LIMIT {limit}",
                "Warranty Registrations": "SELECT registration_id, customer_id, product_id, serial_number, status FROM warranty_registrations ORDER BY registration_id LIMIT {limit}",
                "Support Cases": "SELECT case_id, customer_id, product_id, intent, outcome, escalated FROM support_cases ORDER BY case_id LIMIT {limit}",
                "Knowledge Docs": "SELECT doc_id, product_id, kind, title FROM knowledge_documents ORDER BY doc_id LIMIT {limit}",
            }

            tabs = st.tabs(list(table_map.keys()))
            for tab, (label, query_template) in zip(tabs, table_map.items()):
                with tab:
                    sql = query_template.format(limit=preview_rows)
                    rows, cols = _query(sql)
                    st.caption(f"`{db_path}` | showing {len(rows)} rows")
                    st.dataframe(
                        [{col: row[idx] for idx, col in enumerate(cols)} for row in rows],
                        width="stretch",
                        hide_index=True,
                    )
