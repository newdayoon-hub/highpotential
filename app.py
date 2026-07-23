import streamlit as st

# ---------------------------------------------------------
# 페이지 기본 설정
# ---------------------------------------------------------
st.set_page_config(
    page_title="청소년 우울증 경로 시뮬레이터",
    page_icon="🧠",
    layout="wide",
)

# ---------------------------------------------------------
# 앱 데이터
# ---------------------------------------------------------
STAGES = [
    {
        "name": "스트레스",
        "short": "스트레스",
        "description": "학업, 대인관계, 수면 부족 등으로 인한 스트레스 수준",
    },
    {
        "name": "HPA축 과활성화",
        "short": "HPA축",
        "description": "스트레스 반응을 조절하는 HPA축의 활성화 정도",
    },
    {
        "name": "코르티솔 증가",
        "short": "코르티솔",
        "description": "스트레스 호르몬인 코르티솔의 증가 정도",
    },
    {
        "name": "해마 등의 신경생성 감소",
        "short": "신경생성 감소",
        "description": "해마 등에서 새로운 신경세포가 생성되는 기능의 저하 정도",
    },
    {
        "name": "감정 조절 기능 저하",
        "short": "감정 조절 저하",
        "description": "부정적 감정과 스트레스를 조절하는 기능의 저하 정도",
    },
    {
        "name": "우울증",
        "short": "우울 증상",
        "description": "우울감, 흥미 저하 등 우울 증상의 정도",
    },
]

# 사용자가 지정한 5개 경로 가중치
PATH_WEIGHTS = [2.3, 3.4, 4.5, 0.7, 1.5]

PATH_NAMES = [
    "스트레스 → HPA축 과활성화",
    "HPA축 과활성화 → 코르티솔 증가",
    "코르티솔 증가 → 신경생성 감소",
    "신경생성 감소 → 감정 조절 기능 저하",
    "감정 조절 기능 저하 → 우울증",
]

TREATMENTS = {
    "약물 치료": {
        "icon": "💊",
        "examples": [
            "항우울제",
            "불안 및 수면 증상에 대한 보조적 약물",
            "전문의의 진단과 경과 관찰",
        ],
        "effect": 0.18,
    },
    "행동 치료": {
        "icon": "🏃",
        "examples": [
            "수면 습관 조절",
            "규칙적인 신체 활동",
            "생활 일정과 활동량 관리",
        ],
        "effect": 0.12,
    },
    "심리 치료": {
        "icon": "💬",
        "examples": [
            "인지행동치료",
            "대인관계치료",
            "스트레스 대처 및 감정 조절 훈련",
        ],
        "effect": 0.15,
    },
}

# ---------------------------------------------------------
# 세션 상태 초기화
# ---------------------------------------------------------
if "opened_treatment" not in st.session_state:
    st.session_state.opened_treatment = None

if "selected_treatments" not in st.session_state:
    st.session_state.selected_treatments = {}

if "treatment_details" not in st.session_state:
    st.session_state.treatment_details = {}

if "slider_values" not in st.session_state:
    st.session_state.slider_values = {
        f"stage_{index}": 30 if index == 0 else 20
        for index in range(len(STAGES))
    }

# ---------------------------------------------------------
# 스타일
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.15rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }

    .subtitle {
        color: #5f6775;
        font-size: 1rem;
        margin-bottom: 1.4rem;
    }

    .stage-card {
        min-height: 155px;
        padding: 16px 12px;
        border: 1px solid #d9dee8;
        border-radius: 16px;
        background: linear-gradient(145deg, #ffffff, #f7f9fc);
        text-align: center;
        box-shadow: 0 4px 13px rgba(40, 54, 90, 0.06);
    }

    .stage-number {
        display: inline-block;
        padding: 3px 9px;
        margin-bottom: 8px;
        border-radius: 20px;
        background-color: #eef1f8;
        color: #49536b;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .stage-name {
        min-height: 47px;
        font-size: 1.02rem;
        font-weight: 800;
        color: #202735;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .stage-value {
        margin-top: 10px;
        font-size: 1.4rem;
        font-weight: 800;
        color: #4d5ca6;
    }

    .arrow-box {
        text-align: center;
        margin-top: 70px;
        font-size: 1.8rem;
        color: #7b8498;
        font-weight: 800;
    }

    .weight-label {
        text-align: center;
        margin-top: 4px;
        font-size: 0.77rem;
        color: #626b7d;
        font-weight: 700;
    }

    .metric-card {
        padding: 20px;
        border-radius: 17px;
        border: 1px solid #dfe3eb;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(35, 42, 60, 0.05);
    }

    .result-low {
        color: #287a49;
        font-weight: 800;
    }

    .result-mid {
        color: #ad6a00;
        font-weight: 800;
    }

    .result-high {
        color: #b43a45;
        font-weight: 800;
    }

    div.stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
    }

    [data-testid="stMetricValue"] {
        font-weight: 800;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 계산 함수
# ---------------------------------------------------------
def calculate_depression_score(stage_values: list[int]) -> tuple[float, list[float]]:
    """
    각 경로의 앞 단계와 뒤 단계 활성도를 평균한 뒤,
    해당 경로 가중치를 곱해 전체 우울감 지표를 계산한다.

    반환값:
    - 0~100 범위의 전체 지표
    - 각 경로가 전체 지표에 기여한 점수
    """
    contributions = []

    for index, weight in enumerate(PATH_WEIGHTS):
        previous_stage = stage_values[index] / 100
        next_stage = stage_values[index + 1] / 100

        # 두 단계가 함께 활성화될수록 경로의 영향이 커지도록 계산
        pathway_activity = (previous_stage + next_stage) / 2

        contribution = pathway_activity * weight
        contributions.append(contribution)

    maximum_score = sum(PATH_WEIGHTS)
    raw_score = sum(contributions)

    depression_score = (raw_score / maximum_score) * 100
    return min(max(depression_score, 0), 100), contributions


def calculate_treatment_reduction(score: float) -> tuple[float, float]:
    """
    선택된 치료법의 효과를 합산하여 예상 치료 후 지표를 계산한다.

    초안용 단순 모형이며 실제 임상 효과를 의미하지 않는다.
    """
    remaining_ratio = 1.0

    for treatment_name in st.session_state.selected_treatments.values():
        if treatment_name in TREATMENTS:
            treatment_effect = TREATMENTS[treatment_name]["effect"]
            remaining_ratio *= 1 - treatment_effect

    treated_score = score * remaining_ratio
    reduction = score - treated_score

    return max(treated_score, 0), max(reduction, 0)


def get_score_message(score: float) -> tuple[str, str]:
    if score < 25:
        return "낮은 수준", "result-low"
    if score < 50:
        return "주의 수준", "result-mid"
    if score < 75:
        return "높은 수준", "result-high"
    return "매우 높은 수준", "result-high"


# ---------------------------------------------------------
# 헤더
# ---------------------------------------------------------
st.markdown(
    '<div class="main-title">🧠 청소년 우울증 경로 시뮬레이터</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
        스트레스가 생물학적·심리적 단계를 거쳐 우울 증상으로 이어지는 과정을
        조절하고, 단계별 치료 방법을 선택해 보는 교육용 시뮬레이터입니다.
    </div>
    """,
    unsafe_allow_html=True,
)

st.info(
    "이 앱은 탐구 및 시각화를 위한 단순 모형입니다. "
    "표시되는 수치와 치료 효과는 실제 진단이나 치료 결과를 의미하지 않습니다."
)

# ---------------------------------------------------------
# 사이드바
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 시뮬레이션 설정")

    st.write("각 요인의 활성도를 조절하세요.")

    stage_values = []

    for index, stage in enumerate(STAGES):
        if index == 0:
            weight_text = "초기 입력 요인"
        else:
            weight_text = f"연결 가중치: {PATH_WEIGHTS[index - 1]:.1f}/5.0"

        value = st.slider(
            label=f"{index + 1}. {stage['name']}",
            min_value=0,
            max_value=100,
            value=st.session_state.slider_values[f"stage_{index}"],
            step=1,
            help=f"{stage['description']} · {weight_text}",
            key=f"slider_{index}",
        )

        st.session_state.slider_values[f"stage_{index}"] = value
        stage_values.append(value)

    st.divider()

    if st.button("모든 값 초기화", use_container_width=True):
        for index in range(len(STAGES)):
            st.session_state.slider_values[f"stage_{index}"] = (
                30 if index == 0 else 20
            )

        st.session_state.selected_treatments = {}
        st.session_state.treatment_details = {}
        st.session_state.opened_treatment = None
        st.rerun()

# ---------------------------------------------------------
# 우울증 경로 시각화
# ---------------------------------------------------------
st.subheader("1. 메인 우울증 경로")

# 6개 단계 + 5개 연결 영역
column_sizes = []

for index in range(len(STAGES)):
    column_sizes.append(2.2)

    if index < len(PATH_WEIGHTS):
        column_sizes.append(1.05)

path_columns = st.columns(column_sizes, gap="small")

column_index = 0

for stage_index, stage in enumerate(STAGES):
    with path_columns[column_index]:
        if stage_index == 0:
            weight_info = "초기 스트레스 입력"
        else:
            weight_info = (
                f"이전 경로 가중치 "
                f"{PATH_WEIGHTS[stage_index - 1]:.1f}/5.0"
            )

        st.markdown(
            f"""
            <div class="stage-card">
                <div class="stage-number">단계 {stage_index + 1}</div>
                <div class="stage-name">{stage["name"]}</div>
                <div class="stage-value">{stage_values[stage_index]}</div>
                <div class="weight-label">{weight_info}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    column_index += 1

    if stage_index < len(PATH_WEIGHTS):
        with path_columns[column_index]:
            st.markdown(
                f"""
                <div class="arrow-box">→</div>
                <div class="weight-label">
                    가중치 {PATH_WEIGHTS[stage_index]:.1f}
                </div>
                """,
                unsafe_allow_html=True,
            )

            treatment_button_label = f"치료 {stage_index + 1}"

            if st.button(
                treatment_button_label,
                key=f"open_treatment_{stage_index}",
                help=f"{PATH_NAMES[stage_index]} 사이의 치료법 선택",
            ):
                if st.session_state.opened_treatment == stage_index:
                    st.session_state.opened_treatment = None
                else:
                    st.session_state.opened_treatment = stage_index

                st.rerun()

            chosen = st.session_state.selected_treatments.get(stage_index)

            if chosen:
                treatment_icon = TREATMENTS[chosen]["icon"]
                st.caption(f"{treatment_icon} {chosen}")

        column_index += 1

# ---------------------------------------------------------
# 치료 선택 패널
# ---------------------------------------------------------
opened_treatment = st.session_state.opened_treatment

if opened_treatment is not None:
    st.divider()
    st.subheader(
        f"2. 치료 선택: {PATH_NAMES[opened_treatment]}"
    )

    st.write(
        "이 경로에 적용할 치료 분야를 선택하세요. "
        "같은 치료 분야라도 단계에 따라 구체적인 치료 방법은 달라질 수 있습니다."
    )

    treatment_columns = st.columns(3)

    for treatment_index, (treatment_name, treatment_data) in enumerate(
        TREATMENTS.items()
    ):
        with treatment_columns[treatment_index]:
            st.markdown(
                f"### {treatment_data['icon']} {treatment_name}"
            )

            for example in treatment_data["examples"]:
                st.write(f"· {example}")

            already_selected = (
                st.session_state.selected_treatments.get(opened_treatment)
                == treatment_name
            )

            button_label = (
                "선택됨 ✓" if already_selected else f"{treatment_name} 선택"
            )

            if st.button(
                button_label,
                key=f"select_{opened_treatment}_{treatment_name}",
                use_container_width=True,
                type="primary" if already_selected else "secondary",
            ):
                st.session_state.selected_treatments[
                    opened_treatment
                ] = treatment_name

                st.session_state.opened_treatment = None
                st.rerun()

    if opened_treatment in st.session_state.selected_treatments:
        if st.button(
            "이 단계의 치료 선택 해제",
            key=f"remove_treatment_{opened_treatment}",
        ):
            del st.session_state.selected_treatments[opened_treatment]
            st.session_state.opened_treatment = None
            st.rerun()

# ---------------------------------------------------------
# 결과 계산
# ---------------------------------------------------------
depression_score, contributions = calculate_depression_score(stage_values)
treated_score, reduction = calculate_treatment_reduction(depression_score)

score_label, score_class = get_score_message(depression_score)
treated_label, treated_class = get_score_message(treated_score)

st.divider()
st.subheader("3. 우울감 지표")

metric_columns = st.columns([1, 1, 1])

with metric_columns[0]:
    st.metric(
        label="치료 적용 전 지표",
        value=f"{depression_score:.1f} / 100",
    )

with metric_columns[1]:
    st.metric(
        label="치료 적용 후 예상 지표",
        value=f"{treated_score:.1f} / 100",
        delta=f"-{reduction:.1f}",
        delta_color="inverse",
    )

with metric_columns[2]:
    st.metric(
        label="선택된 치료 단계",
        value=f"{len(st.session_state.selected_treatments)}개",
    )

st.progress(depression_score / 100)

st.markdown(
    f"""
    현재 치료 적용 전 지표는
    <span class="{score_class}">{score_label}</span>이며,
    선택한 치료를 단순 모형에 적용한 예상 지표는
    <span class="{treated_class}">{treated_label}</span>입니다.
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 경로별 영향 분석
# ---------------------------------------------------------
st.subheader("4. 경로별 우울감 지표 기여도")

maximum_weighted_score = sum(PATH_WEIGHTS)

for index, contribution in enumerate(contributions):
    contribution_score = contribution / maximum_weighted_score * 100
    activity = (stage_values[index] + stage_values[index + 1]) / 2

    left, middle, right = st.columns([4, 2, 2])

    with left:
        st.write(f"**{index + 1}. {PATH_NAMES[index]}**")
        st.progress(min(contribution_score / 100, 1.0))

    with middle:
        st.write(f"가중치: **{PATH_WEIGHTS[index]:.1f}/5.0**")

    with right:
        st.write(f"기여도: **{contribution_score:.1f}점**")

    st.caption(
        f"두 단계의 평균 활성도 {activity:.1f} × "
        f"가중치 {PATH_WEIGHTS[index]:.1f}"
    )

# ---------------------------------------------------------
# 선택된 치료 요약
# ---------------------------------------------------------
st.subheader("5. 단계별 치료 계획")

if not st.session_state.selected_treatments:
    st.warning(
        "아직 선택된 치료가 없습니다. "
        "경로 사이의 치료 버튼을 눌러 치료 분야를 선택하세요."
    )
else:
    for path_index in sorted(st.session_state.selected_treatments):
        treatment_name = st.session_state.selected_treatments[path_index]
        treatment_data = TREATMENTS[treatment_name]

        with st.expander(
            f"{path_index + 1}단계 · {PATH_NAMES[path_index]} "
            f"→ {treatment_data['icon']} {treatment_name}",
            expanded=True,
        ):
            st.write(
                f"**선택한 치료 분야:** {treatment_name}"
            )

            st.write("**치료 예시**")

            for example in treatment_data["examples"]:
                st.write(f"- {example}")

            detail_key = f"detail_{path_index}"

            detail = st.text_area(
                "구체적인 치료 방법 또는 근거",
                value=st.session_state.treatment_details.get(
                    path_index, ""
                ),
                placeholder=(
                    "예: 스트레스 관리 교육을 실시하고 "
                    "수면 시간을 일정하게 유지한다."
                ),
                key=detail_key,
            )

            st.session_state.treatment_details[path_index] = detail

# ---------------------------------------------------------
# 계산 방식 설명
# ---------------------------------------------------------
with st.expander("지표 계산 방식 보기"):
    st.markdown(
        """
        #### 기본 계산 원리

        각 경로에서는 앞 단계와 뒤 단계 슬라이더 값의 평균을 구한 후,
        해당 경로의 가중치를 곱합니다.

        ```
        경로 활성도 = (앞 단계 값 + 뒤 단계 값) ÷ 2
        경로 영향 = 경로 활성도 × 가중치
        ```

        모든 경로의 영향을 더한 뒤 가능한 최댓값과 비교하여
        0~100 범위로 환산합니다.

        따라서 동일한 크기로 슬라이더를 높여도 가중치가 큰 경로일수록
        전체 우울감 지표가 더 크게 증가합니다.

        예를 들어 코르티솔 증가에서 신경생성 감소로 이어지는
        3단계 경로의 가중치는 4.5이므로, 가중치가 0.7인
        4단계 경로보다 지표에 더 큰 영향을 줍니다.
        """
    )

st.divider()

st.caption(
    "주의: 실제 청소년 우울증은 유전, 환경, 사회관계, 수면, "
    "신체 건강 등 다양한 요인의 상호작용으로 나타난다. "
    "본 앱의 가중치와 치료 감소율은 앱 구조를 시험하기 위한 임시 값이다."
)
