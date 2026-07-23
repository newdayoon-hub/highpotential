import streamlit as st

# =========================================================
# 1. 페이지 설정
# =========================================================
st.set_page_config(
    page_title="청소년 우울증 경로 시뮬레이터",
    page_icon="🧠",
    layout="wide",
)

# =========================================================
# 2. 경로 데이터
# =========================================================
FACTORS = [
    {
        "name": "스트레스",
        "description": "학업, 대인관계, 수면 부족 등으로 인한 스트레스 정도",
    },
    {
        "name": "HPA축 과활성화",
        "description": "스트레스 반응을 조절하는 HPA축이 과도하게 활성화된 정도",
    },
    {
        "name": "코르티솔 증가",
        "description": "스트레스 호르몬인 코르티솔이 증가한 정도",
    },
    {
        "name": "해마 등의 신경생성 감소",
        "description": "해마 등에서 새로운 신경세포 생성이 감소한 정도",
    },
    {
        "name": "감정 조절 기능 저하",
        "description": "부정적인 감정과 스트레스를 조절하는 기능이 저하된 정도",
    },
]

PATH_WEIGHTS = [2.3, 3.4, 4.5, 0.7, 1.5]

PATH_NAMES = [
    "스트레스 → HPA축 과활성화",
    "HPA축 과활성화 → 코르티솔 증가",
    "코르티솔 증가 → 해마 등의 신경생성 감소",
    "해마 등의 신경생성 감소 → 감정 조절 기능 저하",
    "감정 조절 기능 저하 → 우울증",
]

# =========================================================
# 3. 치료 데이터
# =========================================================
TREATMENTS = {
    "약물 치료": {
        "icon": "💊",
        "examples": [
            "전문의의 진단에 따른 항우울제 치료",
            "불안 또는 수면 증상에 대한 보조적 약물 치료",
            "부작용과 증상 변화를 확인하기 위한 정기적 관찰",
        ],
        "effect": 0.18,
    },
    "행동 치료": {
        "icon": "🏃",
        "examples": [
            "규칙적인 수면 습관 형성",
            "신체 활동과 일상 활동 증가",
            "회피 행동을 줄이고 단계적으로 활동을 늘리는 훈련",
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

# =========================================================
# 4. 기본값과 세션 상태
# =========================================================
DEFAULT_VALUES = [30, 20, 20, 20, 20]

for index, default_value in enumerate(DEFAULT_VALUES):
    key = f"factor_slider_{index}"

    if key not in st.session_state:
        st.session_state[key] = default_value

if "opened_treatment" not in st.session_state:
    st.session_state.opened_treatment = None

if "selected_treatments" not in st.session_state:
    st.session_state.selected_treatments = {}

if "treatment_details" not in st.session_state:
    st.session_state.treatment_details = {}

# =========================================================
# 5. CSS
# =========================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }

    .subtitle {
        color: #5f6775;
        font-size: 1rem;
        margin-bottom: 1.4rem;
        line-height: 1.6;
    }

    .stage-card {
        min-height: 205px;
        padding: 16px 10px;
        border: 1px solid #d9dee8;
        border-radius: 18px;
        background: linear-gradient(145deg, #ffffff, #f7f9fc);
        text-align: center;
        box-shadow: 0 5px 14px rgba(40, 54, 90, 0.07);
        overflow: hidden;
    }

    .depression-card {
        min-height: 205px;
        padding: 16px 10px;
        border: 2px solid #5366b4;
        border-radius: 18px;
        background: linear-gradient(145deg, #f5f7ff, #ffffff);
        text-align: center;
        box-shadow: 0 5px 16px rgba(70, 85, 160, 0.15);
        overflow: hidden;
    }

    .stage-number {
        display: inline-block;
        padding: 4px 10px;
        margin-bottom: 12px;
        border-radius: 20px;
        background-color: #eef1f8;
        color: #49536b;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .stage-name {
        min-height: 72px;
        font-size: 0.96rem;
        font-weight: 800;
        color: #202735;
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        word-break: keep-all;
        overflow-wrap: break-word;
        line-height: 1.45;
        padding: 0 4px;
    }

    .stage-value {
        margin-top: 12px;
        font-size: 1.55rem;
        font-weight: 800;
        color: #4d5ca6;
    }

    .weight-label {
        text-align: center;
        margin-top: 8px;
        font-size: 0.77rem;
        color: #626b7d;
        font-weight: 700;
        word-break: keep-all;
        line-height: 1.4;
    }

    .auto-label {
        display: inline-block;
        margin-top: 10px;
        padding: 4px 9px;
        border-radius: 10px;
        background-color: #e9edff;
        color: #4558a5;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .small-description {
        margin-top: 10px;
        color: #687184;
        font-size: 0.74rem;
        line-height: 1.45;
        text-align: center;
        word-break: keep-all;
        overflow-wrap: break-word;
    }

    .arrow-box {
        text-align: center;
        margin-top: 70px;
        font-size: 2rem;
        color: #7b8498;
        font-weight: 800;
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

    @media (max-width: 900px) {
        .stage-name {
            font-size: 0.85rem;
        }

        .stage-value {
            font-size: 1.35rem;
        }

        .small-description {
            font-size: 0.68rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 6. HTML 카드 함수
# =========================================================
def make_factor_card(
    factor_number: int,
    factor_name: str,
    value: int,
    weight: float,
) -> str:
    return (
        f'<div class="stage-card">'
        f'<div class="stage-number">요인 {factor_number}</div>'
        f'<div class="stage-name">{factor_name}</div>'
        f'<div class="stage-value">{value}</div>'
        f'<div class="weight-label">가중치 {weight:.1f}/5.0</div>'
        f'</div>'
    )


def make_depression_card(score: float) -> str:
    return (
        f'<div class="depression-card">'
        f'<div class="stage-number">종속변인</div>'
        f'<div class="stage-name">우울감 지표</div>'
        f'<div class="stage-value">{score:.1f}</div>'
        f'<div class="auto-label">자동 계산</div>'
        f'<div class="small-description">'
        f'앞의 다섯 요인과 가중치를 바탕으로 계산됨'
        f'</div>'
        f'</div>'
    )


def make_arrow(weight: float) -> str:
    return (
        f'<div class="arrow-box">→</div>'
        f'<div class="weight-label">가중치 {weight:.1f}</div>'
    )

# =========================================================
# 7. 계산 함수
# =========================================================
def calculate_depression_score(
    factor_values: list[int],
) -> tuple[float, list[float]]:
    weighted_values = []

    for value, weight in zip(factor_values, PATH_WEIGHTS):
        weighted_value = value * weight
        weighted_values.append(weighted_value)

    maximum_weighted_value = 100 * sum(PATH_WEIGHTS)
    current_weighted_value = sum(weighted_values)

    depression_score = (
        current_weighted_value / maximum_weighted_value
    ) * 100

    contributions = [
        weighted_value / maximum_weighted_value * 100
        for weighted_value in weighted_values
    ]

    depression_score = min(max(depression_score, 0), 100)

    return depression_score, contributions


def calculate_treated_score(score: float) -> tuple[float, float]:
    remaining_ratio = 1.0

    for treatment_name in st.session_state.selected_treatments.values():
        effect = TREATMENTS[treatment_name]["effect"]
        remaining_ratio *= 1 - effect

    treated_score = score * remaining_ratio
    reduction = score - treated_score

    return max(treated_score, 0), max(reduction, 0)


def get_score_level(score: float) -> tuple[str, str]:
    if score < 25:
        return "낮은 수준", "result-low"

    if score < 50:
        return "주의 수준", "result-mid"

    if score < 75:
        return "높은 수준", "result-high"

    return "매우 높은 수준", "result-high"


def reset_app():
    for index, default_value in enumerate(DEFAULT_VALUES):
        st.session_state[f"factor_slider_{index}"] = default_value

    st.session_state.opened_treatment = None
    st.session_state.selected_treatments = {}
    st.session_state.treatment_details = {}

# =========================================================
# 8. 제목과 설명
# =========================================================
st.markdown(
    '<div class="main-title">🧠 청소년 우울증 경로 시뮬레이터</div>',
    unsafe_allow_html=True,
)

st.markdown(
    (
        '<div class="subtitle">'
        '스트레스가 생물학적·심리적 단계를 거쳐 우울 증상으로 '
        '이어지는 과정을 조절하고, 단계별 치료 방법을 선택하는 '
        '교육용 시뮬레이터입니다.'
        '</div>'
    ),
    unsafe_allow_html=True,
)

st.info(
    "우울증은 사용자가 직접 조절하는 요인이 아니라, "
    "앞의 다섯 요인과 가중치를 바탕으로 자동 계산되는 종속변인입니다."
)

# =========================================================
# 9. 사이드바 슬라이더
# =========================================================
with st.sidebar:
    st.header("⚙️ 요인 조절")

    st.write(
        "다섯 요인의 정도를 조절하면 우울감 지표가 자동으로 변합니다."
    )

    factor_values = []

    for index, factor in enumerate(FACTORS):
        value = st.slider(
            label=f"{index + 1}. {factor['name']}",
            min_value=0,
            max_value=100,
            step=1,
            key=f"factor_slider_{index}",
            help=(
                f"{factor['description']} "
                f"· 가중치 {PATH_WEIGHTS[index]:.1f}/5.0"
            ),
        )

        factor_values.append(value)

        st.caption(
            f"적용 가중치: {PATH_WEIGHTS[index]:.1f}/5.0"
        )

    st.divider()

    st.button(
        "모든 값 초기화",
        use_container_width=True,
        on_click=reset_app,
    )

# =========================================================
# 10. 우울감 지표 계산
# =========================================================
depression_score, contributions = calculate_depression_score(
    factor_values
)

treated_score, reduction = calculate_treated_score(
    depression_score
)

score_label, score_class = get_score_level(
    depression_score
)

treated_label, treated_class = get_score_level(
    treated_score
)

# =========================================================
# 11. 메인 우울증 경로
# =========================================================
st.subheader("1. 메인 우울증 경로")

column_sizes = []

for index in range(6):
    column_sizes.append(2.35)

    if index < 5:
        column_sizes.append(1.0)

path_columns = st.columns(
    column_sizes,
    gap="small",
)

column_index = 0

for factor_index, factor in enumerate(FACTORS):
    with path_columns[column_index]:
        st.markdown(
            make_factor_card(
                factor_number=factor_index + 1,
                factor_name=factor["name"],
                value=factor_values[factor_index],
                weight=PATH_WEIGHTS[factor_index],
            ),
            unsafe_allow_html=True,
        )

    column_index += 1

    with path_columns[column_index]:
        st.markdown(
            make_arrow(PATH_WEIGHTS[factor_index]),
            unsafe_allow_html=True,
        )

        if st.button(
            f"치료 {factor_index + 1}",
            key=f"open_treatment_{factor_index}",
            help=f"{PATH_NAMES[factor_index]} 경로의 치료 선택",
        ):
            if (
                st.session_state.opened_treatment
                == factor_index
            ):
                st.session_state.opened_treatment = None
            else:
                st.session_state.opened_treatment = factor_index

            st.rerun()

        chosen_treatment = (
            st.session_state.selected_treatments.get(
                factor_index
            )
        )

        if chosen_treatment:
            icon = TREATMENTS[chosen_treatment]["icon"]
            st.caption(
                f"{icon} {chosen_treatment}"
            )

    column_index += 1

with path_columns[column_index]:
    st.markdown(
        make_depression_card(depression_score),
        unsafe_allow_html=True,
    )

# =========================================================
# 12. 치료 선택
# =========================================================
opened_treatment = st.session_state.opened_treatment

if opened_treatment is not None:
    st.divider()

    st.subheader(
        f"2. 치료 선택: {PATH_NAMES[opened_treatment]}"
    )

    st.write(
        "이 경로에 적용할 치료 분야를 선택하세요."
    )

    treatment_columns = st.columns(3)

    for treatment_index, (
        treatment_name,
        treatment_data,
    ) in enumerate(TREATMENTS.items()):

        with treatment_columns[treatment_index]:
            st.markdown(
                f"### {treatment_data['icon']} "
                f"{treatment_name}"
            )

            for example in treatment_data["examples"]:
                st.write(f"· {example}")

            is_selected = (
                st.session_state.selected_treatments.get(
                    opened_treatment
                )
                == treatment_name
            )

            button_text = (
                "선택됨 ✓"
                if is_selected
                else f"{treatment_name} 선택"
            )

            if st.button(
                button_text,
                key=(
                    f"select_{opened_treatment}_"
                    f"{treatment_name}"
                ),
                type=(
                    "primary"
                    if is_selected
                    else "secondary"
                ),
                use_container_width=True,
            ):
                st.session_state.selected_treatments[
                    opened_treatment
                ] = treatment_name

                st.session_state.opened_treatment = None
                st.rerun()

    if (
        opened_treatment
        in st.session_state.selected_treatments
    ):
        if st.button(
            "이 단계의 치료 선택 해제",
            key=f"remove_{opened_treatment}",
        ):
            del st.session_state.selected_treatments[
                opened_treatment
            ]

            st.session_state.opened_treatment = None
            st.rerun()

# =========================================================
# 13. 우울감 지표 결과
# =========================================================
st.divider()
st.subheader("3. 우울감 지표")

result_columns = st.columns(3)

with result_columns[0]:
    st.metric(
        label="치료 적용 전 지표",
        value=f"{depression_score:.1f} / 100",
    )

with result_columns[1]:
    st.metric(
        label="치료 적용 후 예상 지표",
        value=f"{treated_score:.1f} / 100",
        delta=f"-{reduction:.1f}",
        delta_color="inverse",
    )

with result_columns[2]:
    st.metric(
        label="선택된 치료 단계",
        value=(
            f"{len(st.session_state.selected_treatments)}개"
        ),
    )

st.progress(
    min(max(depression_score / 100, 0), 1)
)

st.markdown(
    (
        f'현재 치료 적용 전 지표는 '
        f'<span class="{score_class}">{score_label}</span>이며, '
        f'선택한 치료를 임시 모형에 적용한 예상 지표는 '
        f'<span class="{treated_class}">{treated_label}</span>입니다.'
    ),
    unsafe_allow_html=True,
)

# =========================================================
# 14. 요인별 기여도
# =========================================================
st.subheader("4. 요인별 우울감 지표 기여도")

for index, contribution in enumerate(contributions):
    left, middle, right = st.columns(
        [4, 2, 2]
    )

    with left:
        st.write(
            f"**{index + 1}. {FACTORS[index]['name']}**"
        )

        st.progress(
            min(max(contribution / 100, 0), 1)
        )

    with middle:
        st.write(
            f"가중치: "
            f"**{PATH_WEIGHTS[index]:.1f}/5.0**"
        )

    with right:
        st.write(
            f"기여 점수: "
            f"**{contribution:.1f}점**"
        )

    st.caption(
        f"슬라이더 값 {factor_values[index]} × "
        f"가중치 {PATH_WEIGHTS[index]:.1f}"
    )

# =========================================================
# 15. 선택한 치료 계획
# =========================================================
st.subheader("5. 선택한 치료 계획")

if not st.session_state.selected_treatments:
    st.warning(
        "아직 선택된 치료가 없습니다. "
        "경로 사이의 치료 버튼을 눌러 치료 분야를 선택하세요."
    )

else:
    for path_index in sorted(
        st.session_state.selected_treatments
    ):
        treatment_name = (
            st.session_state.selected_treatments[
                path_index
            ]
        )

        treatment_data = TREATMENTS[
            treatment_name
        ]

        with st.expander(
            (
                f"{path_index + 1}단계 · "
                f"{PATH_NAMES[path_index]} "
                f"→ {treatment_data['icon']} "
                f"{treatment_name}"
            ),
            expanded=True,
        ):
            st.write(
                f"**선택한 치료 분야:** "
                f"{treatment_name}"
            )

            st.write("**치료 예시**")

            for example in treatment_data["examples"]:
                st.write(f"- {example}")

            detail = st.text_area(
                "구체적인 치료 방법 또는 연구 근거",
                value=(
                    st.session_state
                    .treatment_details
                    .get(path_index, "")
                ),
                placeholder=(
                    "예: 스트레스 관리 교육과 "
                    "규칙적인 수면 습관 형성을 실시한다."
                ),
                key=f"detail_{path_index}",
            )

            st.session_state.treatment_details[
                path_index
            ] = detail

# =========================================================
# 16. 계산 방식 설명
# =========================================================
with st.expander(
    "우울감 지표 계산 방식 보기"
):
    st.markdown(
        """
        #### 계산 원리

        우울감 지표는 사용자가 직접 설정하지 않고,
        앞의 다섯 요인과 각 요인의 가중치를 이용해 계산합니다.

        ```text
        요인별 영향 = 슬라이더 값 × 가중치

        우울감 지표
        = 모든 요인의 영향을 합한 값
        ÷ 가능한 최대 영향
        × 100
        ```

        같은 크기로 슬라이더를 움직여도 가중치가 큰 요인은
        우울감 지표를 더 크게 변화시킵니다.

        예를 들어 가중치가 4.5인 코르티솔 관련 요인은
        가중치가 0.7인 신경생성 관련 요인보다
        우울감 지표에 더 큰 영향을 줍니다.
        """
    )

st.divider()

st.caption(
    "주의: 이 앱의 가중치와 치료 효과는 초안 제작을 위한 임시 값이다. "
    "실제 청소년 우울증은 유전, 사회관계, 수면, 신체 건강, 생활환경 등 "
    "다양한 요인의 영향을 받으며, 이 앱은 실제 진단을 목적으로 하지 않는다."
)
