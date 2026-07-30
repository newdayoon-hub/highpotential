# HPA축–염증–우울 경로 시뮬레이터

## 파일
- `app.py`: Streamlit 앱 전체 코드
- `requirements.txt`: Streamlit Cloud 설치 패키지

## 실행 방법
터미널에서 두 파일이 있는 폴더로 이동한 뒤 실행합니다.

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 배포
1. GitHub 저장소에 `app.py`와 `requirements.txt`를 업로드합니다.
2. Streamlit Community Cloud에서 저장소와 `app.py`를 선택합니다.
3. Deploy를 누릅니다.

엑셀의 가중치는 코드 내부에 반영되어 있으므로 배포 시 엑셀 파일을 함께 올리지 않아도 됩니다.

## 계산 원리
슬라이더를 움직이면 변경량에 해당 경로의 가중치를 곱해 다음 단계로 전달합니다.

예를 들어 GR 저항성이 20 증가하면:
- 항염증작용 저하 변화량 = 20 × 0.325
- 사이토카인 변화량 = 앞 변화량 × 0.297
- 우울 증상 변화량 = 앞 변화량 × 0.465

치료 가중치가 0 이하인 선택지는 비활성화됩니다.

> 이 앱은 연구 경로를 보여주기 위한 교육용 모형이며 진단·처방 도구가 아닙니다.
