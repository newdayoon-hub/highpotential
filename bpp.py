import time
from dataclasses import dataclass
from typing import Dict, List

import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="HPA축–염증–우울 경로 시뮬레이터",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────
# 1. 연구 자료에서 가져온 값
# ─────────────────────────────────────────────────────────────
NODES = [
    "만성스트레스",
    "HPA축 활성화",
    "코르티솔 증가",
    "GR 저항성",
    "항염증작용 저하",
    "염증반응 증가\n(사이토카인)",
    "우울 증상",
]

# 각 화살표의 대표 경로 가중치
PATH_WEIGHTS = [0.360, 0.360, 0.325, 0.325, 0.297, 0.465]

PATH_LABELS = [
    "① 만성스트레스 → HPA축 활성화",
    "② HPA축 활성화 → 코르티솔 증가",
    "③ 코르티솔 증가 → GR 저항성",
    "④ GR 저항성 → 항염증작용 저하",
    "⑤ 항염증작용 저하 → 염증반응 증가(사이토카인)",
    "⑥ 염증반응 증가(사이토카인) → 우울 증상",
]

# 치료 가중치(Wapp 최종)
TREATMENT_WEIGHTS: List[Dict[str, float]] = [
    {"심리": 0.11935625, "행동": 0.0, "약물": 0.0},
    {"심리": 0.11935625, "행동": 0.3555138889, "약물": 0.1204125},
    {"심리": 0.1675, "행동": -0.09, "약물": 0.1145625},
    {"심리": 0.1675, "행동": 0.0, "약물": 0.1145625},
    {"심리": 0.21, "행동": 0.0, "약물": 0.08165625},
    {"심리": 0.3558673469, "행동": 0.3621796875, "약물": 0.2296672984},
]

# 엑셀의 약물치료_세부 시트 중 양의 최종 가중치를 가진 약물만 표시
DRUG_INFO: Dict[int, List[Dict[str, object]]] = {
    0: [],
    1: [
        {
            "name": "메티라폰(metyrapone) + 표준 항우울제",
            "weight": 0.22425,
            "note": "코르티솔 합성 경로를 조절하는 접근이다. 첨부 자료에서는 후속 연구의 재현성 한계도 함께 제시되어 있다.",
        }
    ],
    2: [
        {
            "name": "SSRI/항우울제 계열",
            "weight": 0.12675,
            "note": "코르티솔–GR 관련 기전 연구에서 제시된 약물군이다.",
        }
    ],
    3: [
        {
            "name": "SSRI/항우울제 계열",
            "weight": 0.12675,
            "note": "GR 저항성과 항염증 조절의 관련 기전을 대상으로 한 연구에서 제시된 약물군이다.",
        }
    ],
    4: [
        {
            "name": "SSRI (fluoxetine/sertraline)",
            "weight": 0.1365,
            "note": "염증 관련 지표와 우울 증상에 대한 기전·보조 근거가 제시된 약물군이다.",
        }
    ],
    5: [
        {
            "name": "플루옥세틴 + CBT 병합치료",
            "weight": 0.418,
            "note": "첨부 자료의 약물 세부 항목 중 가장 큰 양의 가중치다. 약물 단독이 아니라 CBT와의 병합치료다.",
        },
        {
            "name": "케타민 정맥주입 1회",
            "weight": 0.342,
            "note": "빠른 증상 변화 연구에서 제시되지만 실제 사용은 반드시 전문 의료진의 판단이 필요하다.",
        },
        {
            "name": "서트랄린(sertraline, SSRI)",
            "weight": 0.30175,
            "note": "청소년 우울 치료 연구에서 사용되는 대표적 SSRI 중 하나다.",
        },
        {
            "name": "플루옥세틴(fluoxetine, SSRI)",
            "weight": 0.30175,
            "note": "청소년 우울 치료 근거가 비교적 많이 축적된 SSRI다.",
        },
        {
            "name": "둘록세틴(duloxetine, SNRI)",
            "weight": 0.26775,
            "note": "첨부 자료에서 양의 방향 가중치가 산출된 SNRI다.",
        },
        {
            "name": "에스케타민 비강분무 + 항우울제",
            "weight": 0.22425,
            "note": "항우울제와 병용하는 방식으로 제시된 치료다.",
        },
        {
            "name": "셀레콕시브(celecoxib, 항염증 보조)",
            "weight": 0.19175,
            "note": "염증 조절을 목표로 하는 보조 치료 접근이다.",
        },
        {
            "name": "N-아세틸시스테인(NAC, 항산화 보조)",
            "weight": 0.1885,
            "note": "산화 스트레스 조절을 목표로 하는 보조 치료 접근이다.",
        },
        {
            "name": "항-TNF 제제",
            "weight": 0.1825,
            "note": "염증성 사이토카인 경로를 겨냥하지만 일반적인 청소년 우울증 표준치료로 해석해서는 안 된다.",
        },
    ],
}


@dataclass
class TreatmentRecord:
    edge: int
    kind: str
    weight: float
    reduction: float
    drug: str = ""


# ─────────────────────────────────────────────────────────────
# 2. 상태와 계산 함수
# ─────────────────────────────────────────────────────────────
def clamp(value: float) -> float:
    return max(0.0, min(100.0, float(value)))


def depression_emoji(score: float) -> str:
    if score < 15:
        return "😄"
    if score < 30:
        return "🙂"
    if score < 45:
        return "😐"
    if score < 60:
        return "🙁"
    if score < 75:
        return "😟"
    if score < 90:
        return "😢"
    return "😭"


def depression_label(score: float) -> str:
    if score < 20:
        return "매우 낮음"
    if score < 40:
        return "낮음"
    if score < 60:
        return "중간"
    if score < 80:
        return "높음"
    return "매우 높음"


def initialize_state() -> None:
    defaults = [45.0, 16.2, 5.8, 1.9, 0.6, 0.2]
    for i, value in enumerate(defaults):
        st.session_state.setdefault(f"level_{i}", value)
        st.session_state.setdefault(f"widget_{i}", value)

    st.session_state.setdefault("depression", clamp(defaults[-1] * PATH_WEIGHTS[-1]))
    st.session_state.setdefault("active_treatment_edge", None)
    st.session_state.setdefault("treatment_history", [])
    st.session_state.setdefault("last_propagation", None)
    st.session_state.setdefault("show_animation", True)


def recompute_depression() -> None:
    base = st.session_state["level_5"] * PATH_WEIGHTS[5]
    total_reduction = sum(item.reduction for item in st.session_state["treatment_history"])
    st.session_state["depression"] = clamp(base - total_reduction)


def propagate_from(changed_index: int) -> None:
    """변경된 요인의 변화량을 뒤쪽 노드로 순차 전달한다."""
    new_value = float(st.session_state[f"widget_{changed_index}"])
    old_value = float(st.session_state[f"level_{changed_index}"])
    delta = new_value - old_value
    st.session_state[f"level_{changed_index}"] = new_value

    animation_steps = []
    incoming_delta = delta

    for edge in range(changed_index, 5):
        downstream = edge + 1
        downstream_delta = incoming_delta * PATH_WEIGHTS[edge]
        before = float(st.session_state[f"level_{downstream}"])
        after = clamp(before + downstream_delta)

        st.session_state[f"level_{downstream}"] = after
        st.session_state[f"widget_{downstream}"] = after

        animation_steps.append(
            {
                "node": NODES[downstream],
                "before": before,
                "after": after,
                "weight": PATH_WEIGHTS[edge],
            }
        )
        incoming_delta = downstream_delta

    # 사이토카인 변화가 우울 증상으로 전달됨
    before_dep = float(st.session_state["depression"])
    recompute_depression()
    animation_steps.append(
        {
            "node": "우울 증상",
            "before": before_dep,
            "after": st.session_state["depression"],
            "weight": PATH_WEIGHTS[5],
        }
    )
    st.session_state["last_propagation"] = animation_steps


def apply_treatment(edge: int, kind: str, drug_name: str = "") -> None:
    weight = TREATMENT_WEIGHTS[edge][kind]
    if weight <= 0:
        return

    # 가중치를 0~1의 치료 효과 비율로 해석해 해당 경로 이후의 활성도를 낮춤.
    # 너무 큰 단회 감소를 막기 위해 최대 감소량은 현재 우울 점수의 45%로 제한.
    current_dep = float(st.session_state["depression"])
    reduction = min(current_dep * weight, current_dep * 0.45)

    record = TreatmentRecord(
        edge=edge,
        kind=kind,
        weight=weight,
        reduction=reduction,
        drug=drug_name,
    )
    st.session_state["treatment_history"].append(record)

    # 해당 경로의 도착 노드부터 아래쪽 생물학적 요인도 완만하게 감소
    target_node = min(edge + 1, 5)
    biological_reduction = weight * 18.0
    incoming = biological_reduction
    for node_index in range(target_node, 6):
        st.session_state[f"level_{node_index}"] = clamp(
            st.session_state[f"level_{node_index}"] - incoming
        )
        st.session_state[f"widget_{node_index}"] = st.session_state[f"level_{node_index}"]
        if node_index < 5:
            incoming *= PATH_WEIGHTS[node_index]

    recompute_depression()
    st.session_state["active_treatment_edge"] = None


def reset_simulation() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_state()


initialize_state()


# ─────────────────────────────────────────────────────────────
# 3. CSS
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    :root {
        --navy: #071a35;
        --blue: #0b5ea8;
        --cyan: #2aa7d6;
        --ice: #edf7ff;
        --line: #83c8ef;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 8%, rgba(42,167,214,.14), transparent 25%),
            radial-gradient(circle at 90% 18%, rgba(20,93,160,.12), transparent 26%),
            linear-gradient(180deg, #f8fcff 0%, #edf7ff 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061a34 0%, #0a315b 100%);
    }

    [data-testid="stSidebar"] * {
        color: #eef8ff;
    }

    .hero {
        padding: 1.35rem 1.55rem;
        border: 1px solid rgba(45, 150, 210, .25);
        border-radius: 22px;
        background: linear-gradient(120deg, rgba(4,37,76,.97), rgba(10,96,160,.92));
        box-shadow: 0 16px 45px rgba(6, 51, 96, .18);
        color: white;
        margin-bottom: 1rem;
    }

    .hero h1 {
        margin: 0;
        font-size: clamp(1.65rem, 3vw, 2.65rem);
        letter-spacing: -0.04em;
    }

    .hero p {
        margin: .55rem 0 0;
        color: #cfeeff;
        line-height: 1.65;
    }

    .node-card {
        min-height: 166px;
        padding: 1rem;
        border-radius: 18px;
        border: 1px solid rgba(50, 145, 205, .26);
        background: rgba(255,255,255,.86);
        box-shadow: 0 10px 30px rgba(24, 91, 139, .10);
        text-align: center;
        transition: transform .25s ease, box-shadow .25s ease;
    }

    .node-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 36px rgba(24, 91, 139, .16);
    }

    .node-index {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 999px;
        background: #0b5ea8;
        color: white;
        font-weight: 800;
        font-size: .8rem;
    }

    .node-title {
        margin-top: .6rem;
        color: #092a4c;
        font-weight: 800;
        line-height: 1.3;
        min-height: 42px;
    }

    .node-value {
        margin-top: .4rem;
        color: #0b5ea8;
        font-size: 1.85rem;
        font-weight: 900;
    }

    .arrow-box {
        text-align: center;
        color: #0b75bb;
        font-size: 1.65rem;
        font-weight: 900;
        padding-top: 3.2rem;
    }

    .arrow-weight {
        display: block;
        margin-top: -.15rem;
        font-size: .72rem;
        color: #507b9a;
        font-weight: 700;
    }

    .depression-card {
        padding: 1.2rem;
        border-radius: 22px;
        color: white;
        background: linear-gradient(145deg, #0a315b, #0c73b8);
        box-shadow: 0 16px 40px rgba(7, 61, 110, .24);
        text-align: center;
    }

    .emoji {
        font-size: 4.4rem;
        line-height: 1;
        filter: drop-shadow(0 8px 13px rgba(0,0,0,.18));
    }

    .depression-score {
        font-size: 2.6rem;
        font-weight: 900;
        margin-top: .35rem;
    }

    .scientific-note {
        padding: .9rem 1rem;
        border-left: 4px solid #2aa7d6;
        border-radius: 10px;
        background: rgba(229,246,255,.92);
        color: #173c58;
        line-height: 1.55;
    }

    .disabled-note {
        color: #718096;
        font-size: .83rem;
    }

    div[data-testid="stButton"] > button {
        border-radius: 12px;
        font-weight: 750;
        border: 1px solid #8cc9ec;
    }

    div[data-testid="stButton"] > button:hover {
        border-color: #0b5ea8;
        color: #0b5ea8;
    }

    div[data-testid="stButton"] > button:disabled {
        background: #e8edf1 !important;
        color: #9aa8b4 !important;
        border-color: #d2dbe2 !important;
        cursor: not-allowed;
    }

    div[data-testid="stSlider"] [data-baseweb="slider"] {
        margin-top: .3rem;
    }

    .small-source {
        font-size: .78rem;
        color: #5a7387;
        line-height: 1.55;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────
# 4. 사이드바
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 시뮬레이션 설정")
    st.toggle(
        "순차 전파 표시",
        key="show_animation",
        help="슬라이더 변경 뒤 각 후속 요인의 변화 과정을 짧게 표시합니다.",
    )
    st.markdown("---")
    st.markdown("### 계산 방식")
    st.caption(
        "앞 단계의 변화량 × 해당 화살표 가중치를 다음 단계 변화량으로 전달합니다. "
        "치료는 해당 경로 이후의 활성도와 최종 우울 점수를 낮춥니다."
    )
    st.markdown("---")
    if st.button("↺ 전체 초기화", use_container_width=True, type="primary"):
        reset_simulation()
        st.rerun()

    st.markdown("---")
    st.caption(
        "이 앱은 연구 경로를 시각화하기 위한 교육용 모형이며, 실제 진단이나 개인별 치료 결정을 대신하지 않습니다."
    )


# ─────────────────────────────────────────────────────────────
# 5. 헤더
# ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>HPA축–염증–우울 경로 시뮬레이터</h1>
        <p>
            만성 스트레스에서 우울 증상까지 이어지는 생물학적 경로를 조절하고,
            각 단계의 변화가 가중치에 따라 뒤쪽 요인으로 전파되는 과정을 확인합니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# 변경 직후 전파 과정 표시
if st.session_state.get("last_propagation") and st.session_state["show_animation"]:
    animation_area = st.empty()
    for step in st.session_state["last_propagation"]:
        animation_area.info(
            f"전파 중: **{step['node']}** "
            f"{step['before']:.1f} → {step['after']:.1f} "
            f"(가중치 {step['weight']:.3f})"
        )
        time.sleep(0.10)
    animation_area.success("후속 요인과 우울 증상에 변화가 반영되었습니다.")
    time.sleep(0.25)
    animation_area.empty()
st.session_state["last_propagation"] = None


# ─────────────────────────────────────────────────────────────
# 6. 경로 시각화와 슬라이더
# ─────────────────────────────────────────────────────────────
st.subheader("1. 경로 활성도 조절")
st.markdown(
    '<div class="scientific-note">'
    "슬라이더를 움직인 요인의 <b>변화량</b>이 뒤쪽 요인으로 순차 전달됩니다. "
    "예: GR 저항성이 20에서 40으로 증가하면 +20의 변화량이 ④, ⑤, ⑥ 가중치를 거쳐 "
    "항염증작용 저하 → 사이토카인 → 우울 증상에 차례로 반영됩니다."
    "</div>",
    unsafe_allow_html=True,
)

st.write("")

# 6개 조절 노드 + 최종 우울 노드
path_columns = st.columns([1.2, .35, 1.2, .35, 1.2, .35, 1.2], gap="small")
for visual_index in range(3):
    node_index = visual_index
    with path_columns[visual_index * 2]:
        st.markdown(
            f"""
            <div class="node-card">
                <span class="node-index">{node_index + 1}</span>
                <div class="node-title">{NODES[node_index]}</div>
                <div class="node-value">{st.session_state[f'level_{node_index}']:.1f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.slider(
            f"{NODES[node_index]} 강도",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            key=f"widget_{node_index}",
            on_change=propagate_from,
            args=(node_index,),
            label_visibility="collapsed",
        )
    if visual_index < 3:
        with path_columns[visual_index * 2 + 1]:
            st.markdown(
                f'<div class="arrow-box">→<span class="arrow-weight">w={PATH_WEIGHTS[node_index]:.3f}</span></div>',
                unsafe_allow_html=True,
            )

path_columns_2 = st.columns([1.2, .35, 1.2, .35, 1.2, .35, 1.2], gap="small")
for local_index in range(3):
    node_index = local_index + 3
    with path_columns_2[local_index * 2]:
        st.markdown(
            f"""
            <div class="node-card">
                <span class="node-index">{node_index + 1}</span>
                <div class="node-title">{NODES[node_index].replace(chr(10), "<br>")}</div>
                <div class="node-value">{st.session_state[f'level_{node_index}']:.1f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.slider(
            f"{NODES[node_index]} 강도",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
            key=f"widget_{node_index}",
            on_change=propagate_from,
            args=(node_index,),
            label_visibility="collapsed",
        )

    with path_columns_2[local_index * 2 + 1]:
        st.markdown(
            f'<div class="arrow-box">→<span class="arrow-weight">w={PATH_WEIGHTS[node_index]:.3f}</span></div>',
            unsafe_allow_html=True,
        )

with path_columns_2[6]:
    dep = st.session_state["depression"]
    st.markdown(
        f"""
        <div class="depression-card">
            <div class="node-title" style="color:#dff5ff;">우울 증상</div>
            <div class="emoji">{depression_emoji(dep)}</div>
            <div class="depression-score">{dep:.1f}</div>
            <div>{depression_label(dep)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(int(round(dep)), text="다른 요인의 영향을 받아 자동 계산됩니다")


# ─────────────────────────────────────────────────────────────
# 7. 현재 상태 그래프
# ─────────────────────────────────────────────────────────────
st.subheader("2. 현재 요인별 활성도")
chart_values = [st.session_state[f"level_{i}"] for i in range(6)] + [
    st.session_state["depression"]
]
fig = go.Figure(
    go.Scatter(
        x=[name.replace("\n", "<br>") for name in NODES],
        y=chart_values,
        mode="lines+markers",
        line={"width": 4, "color": "#0b6fb3"},
        marker={
            "size": 12,
            "color": chart_values,
            "colorscale": "Blues",
            "showscale": True,
            "colorbar": {"title": "활성도"},
        },
        fill="tozeroy",
        fillcolor="rgba(42,167,214,0.12)",
        hovertemplate="%{x}<br>활성도 %{y:.1f}<extra></extra>",
    )
)
fig.update_layout(
    height=390,
    margin={"l": 25, "r": 25, "t": 25, "b": 25},
    yaxis={"range": [0, 100], "title": "활성도(0~100)", "gridcolor": "#dbeefa"},
    xaxis={"title": ""},
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.70)",
    font={"family": "Arial, Malgun Gothic, sans-serif", "color": "#183c58"},
)
st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# 8. 치료 선택
# ─────────────────────────────────────────────────────────────
st.subheader("3. 경로별 치료 적용")
st.caption(
    "경로를 선택한 뒤 심리·행동·약물 치료 중 하나를 적용합니다. "
    "첨부 자료에서 최종 가중치가 0 이하인 치료는 회색으로 비활성화됩니다."
)

for edge in range(6):
    with st.container(border=True):
        title_col, weight_col, action_col = st.columns([5.2, 1.4, 1.5])
        with title_col:
            st.markdown(f"#### {PATH_LABELS[edge]}")
        with weight_col:
            st.metric("경로 가중치", f"{PATH_WEIGHTS[edge]:.3f}")
        with action_col:
            if st.button(
                "치료 선택",
                key=f"open_treatment_{edge}",
                use_container_width=True,
                type="primary" if st.session_state["active_treatment_edge"] == edge else "secondary",
            ):
                st.session_state["active_treatment_edge"] = (
                    None if st.session_state["active_treatment_edge"] == edge else edge
                )
                st.rerun()

        if st.session_state["active_treatment_edge"] == edge:
            st.markdown("##### 적용할 치료")
            treatment_cols = st.columns(3)

            for col, kind, icon in zip(
                treatment_cols,
                ["심리", "행동", "약물"],
                ["💬", "🏃", "💊"],
            ):
                weight = TREATMENT_WEIGHTS[edge][kind]
                disabled = weight <= 0

                with col:
                    if kind != "약물":
                        clicked = st.button(
                            f"{icon} {kind} 치료\n\n가중치 {weight:.3f}",
                            key=f"apply_{edge}_{kind}",
                            disabled=disabled,
                            use_container_width=True,
                        )
                        if disabled:
                            st.markdown(
                                '<div class="disabled-note">근거 가중치가 0 이하이므로 선택할 수 없습니다.</div>',
                                unsafe_allow_html=True,
                            )
                        elif clicked:
                            apply_treatment(edge, kind)
                            st.rerun()
                    else:
                        drug_options = DRUG_INFO.get(edge, [])
                        drug_disabled = disabled or not drug_options

                        st.markdown(f"**{icon} 약물 치료** · 가중치 {weight:.3f}")
                        if drug_disabled:
                            st.button(
                                "선택 불가",
                                key=f"disabled_drug_{edge}",
                                disabled=True,
                                use_container_width=True,
                            )
                            st.markdown(
                                '<div class="disabled-note">이 경로에서 선택 가능한 양의 약물 근거가 없습니다.</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            selected_drug = st.selectbox(
                                "약물/성분",
                                options=[item["name"] for item in drug_options],
                                key=f"drug_select_{edge}",
                            )
                            selected_info = next(
                                item for item in drug_options if item["name"] == selected_drug
                            )
                            st.info(
                                f"{selected_info['note']}\n\n"
                                f"약물 세부 가중치: {selected_info['weight']:.3f}"
                            )
                            if st.button(
                                "약물 치료 적용",
                                key=f"apply_drug_{edge}",
                                use_container_width=True,
                            ):
                                apply_treatment(edge, "약물", selected_drug)
                                st.rerun()


# ─────────────────────────────────────────────────────────────
# 9. 치료 기록
# ─────────────────────────────────────────────────────────────
st.subheader("4. 적용된 치료 기록")
history: List[TreatmentRecord] = st.session_state["treatment_history"]

if not history:
    st.info("아직 적용한 치료가 없습니다.")
else:
    for number, item in enumerate(reversed(history), start=1):
        detail = f"{item.kind} 치료"
        if item.drug:
            detail += f" · {item.drug}"
        st.success(
            f"{detail} | {PATH_LABELS[item.edge]} | "
            f"치료 가중치 {item.weight:.3f} | 우울 점수 감소 {item.reduction:.2f}"
        )

    if st.button("치료 기록만 모두 취소", use_container_width=False):
        st.session_state["treatment_history"] = []
        recompute_depression()
        st.rerun()


# ─────────────────────────────────────────────────────────────
# 10. 근거 및 해석 안내
# ─────────────────────────────────────────────────────────────
with st.expander("가중치 출처와 해석상 주의점"):
    st.markdown(
        """
        **경로 가중치**

        - ① 만성스트레스 → HPA축 활성화: 0.360
        - ② HPA축 활성화 → 코르티솔 증가: 0.360
        - ③ 코르티솔 증가 → GR 저항성: 0.325
        - ④ GR 저항성 → 항염증작용 저하: 0.325
        - ⑤ 항염증작용 저하 → 사이토카인 증가: 0.297
        - ⑥ 사이토카인 증가 → 우울 증상: 0.465

        ⑤는 개별 화살표를 직접 산출한 값이 아니라, 첨부 자료에서 스트레스와
        염증반응 증가의 전체 관계를 압축해 적용한 근사치다. 따라서 다른 단계보다
        해석에 더 큰 주의가 필요하다.

        **앱 계산 규칙**

        - 슬라이더 변경: `변화량 × 경로 가중치`를 다음 단계에 전달한다.
        - 치료 적용: 치료 가중치에 비례하여 해당 경로 이후 요인과 우울 점수를 낮춘다.
        - 이 규칙은 연구 가중치를 상호작용형 시각화로 바꾸기 위한 모형이며,
          임상적 위험도 계산 공식이나 실제 치료 효과 예측식은 아니다.
        """
    )

st.markdown(
    """
    <div class="small-source">
    자료 반영: 「경로1_HPA축염증통합경로_가중치산출.xlsx」의 경로 대표값과
    「경로1_18칸_전체_치료가중치_웹검색보강.xlsx」의 치료·약물 최종 가중치.
    약물 정보는 교육적 표시이며, 복용 여부와 치료 선택은 의료 전문가가 판단해야 합니다.
    </div>
    """,
    unsafe_allow_html=True,
)
