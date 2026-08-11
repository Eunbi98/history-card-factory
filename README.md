# history-card-factory

한능검 기출 개념을 `문제 → 문제를 보며 5초 카운트다운 → 정답 → 핵심 해설 → 오답 함정 또는 사건 흐름 → 기억 장면 → 기억법 → 오늘의 정리` 구조의 1080×1920 Shorts로 렌더하는 전용 프로젝트입니다.

## 기본 원칙

- `remotion/src/HistoryCardVideo.tsx`는 마스터 템플릿입니다. 영상마다 직접 수정하지 않습니다.
- 영상별 내용은 `data/cards/*.json`에서만 관리합니다.
- 영상 상단에는 EP 번호를 표시하지 않습니다.
- 기억장면 이미지는 9:16 세로형, 텍스트 없는 이미지 사용을 기본으로 합니다.
- 기억법의 강조 단어는 카드 JSON의 `mnemonicParts`에서 지정합니다.
- 문제·해설·오답 텍스트는 화면 가독성을 우선하며, 긴 원문은 보존하되 `questionShort`, `explanationShort`, `wrongTrapsShort`가 있으면 영상에서는 짧은 버전을 우선 표시합니다.
- 글이 길어졌다고 폰트를 과도하게 줄이지 않습니다. `문장 압축 → 자연스러운 줄바꿈 → 핵심어 강조 → 마지막에만 소폭 폰트 축소` 순서로 처리합니다.
- 사건의 흐름·시간 순서·전후 관계가 핵심인 문제는 일반 오답 목록 대신 연표형 정리를 우선합니다.
- 연표형은 화면 중앙 세로축을 기준으로 사건을 좌우 교차 배치하며, 학습 대상 사건은 강조합니다.
- 연표형 해설에서는 문제의 ①②③④⑤ 보기 번호를 반복하지 않고, 학습에 필요한 사건명·연도·핵심 내용만 표시합니다.

## 문제 유형별 해설 레이아웃

- 일반 선택형 → 오답 함정
- 사건·순서형 → 중앙축 좌우 교차 연표
- 인과관계형 → 원인 → 사건 → 결과
- 시대 구분형 → 시대별 핵심 정리
- 인물·단체 비교형 → 핵심 활동 비교
- 숫자 중심형 → 숫자 리듬 기억법

### 연표형 카드 데이터 예시

```json
{
  "explanationLayout": "timeline",
  "timelineTitle": "민주화 운동의 흐름",
  "timelineItems": [
    {
      "year": "1979",
      "title": "부마 민주 항쟁",
      "detail": "부산·마산 · 유신 체제에 저항"
    },
    {
      "year": "1980",
      "title": "5·18 민주화 운동",
      "detail": "광주 · 신군부에 저항"
    },
    {
      "year": "1987",
      "title": "6월 민주 항쟁",
      "detail": "호헌 철폐 · 민주 헌법 쟁취",
      "accent": true
    }
  ]
}
```

`explanationLayout`이 `timeline`이면 오답 함정 위치에는 일반 보기형 목록 대신 마스터 템플릿의 중앙축 좌우 교차 연표를 사용합니다.

## 설치

```powershell
npm run install:remotion
npm run setup:tts
```

## 한 번에 영상 만들기

예: K002 강감찬

```powershell
npm run make -- K002
```

자동 처리:

1. `data/cards/K002_*.json` 검색
2. 카드 검증
3. `remotion/src/card.json`에 현재 카드 선택
4. 핵심 해설 TTS 생성
5. Remotion 렌더
6. `output/`에 MP4 저장

강감찬은 단축 명령도 사용할 수 있습니다.

```powershell
npm run make:k002
```

## 프리뷰만 보기

```powershell
python scripts/make.py K002 --skip-tts --preview
```

또는 K002 단축 명령:

```powershell
npm run preview:k002
```

## 기억장면 이미지

카드 JSON의 `image`가 예를 들어 아래와 같다면:

```json
"image": "images/K002_memory.png"
```

실제 파일 위치는 다음과 같습니다.

```text
remotion/public/images/K002_memory.png
```

`npm run make`는 이미지가 없으면 렌더를 중단하고 필요한 경로를 알려줍니다.

## 카드 데이터 핵심 필드

```json
{
  "id": "K002",
  "title": "강감찬과 귀주대첩",
  "sourceExam": "기출 개념 참고",
  "question": "다음 중 강감찬과 관련된 전투는?",
  "questionShort": "강감찬과 관련된 전투는?",
  "choices": ["..."],
  "correctChoice": 2,
  "answer": "귀주대첩",
  "explanation": "...",
  "explanationShort": "강감찬 → 귀주대첩 → 거란 격퇴",
  "wrongTraps": [["① ...", "..."]],
  "wrongTrapsShort": [["서희", "강동 6주"]],
  "image": "images/K002_memory.png",
  "memoryHeadline": "...",
  "mnemonicParts": [
    {"text": "귀", "accent": true},
    {"text": "주 ..."}
  ],
  "recapTitle": "강감찬",
  "recapResult": "귀주대첩 승리",
  "recapDetail": "1019년, 거란군을 크게 격파"
}
```

## 앞으로의 제작 흐름

1. 기출 분석에서 다음 카드 선정
2. 문제 유형에 맞는 해설 레이아웃 결정
3. 카드 JSON 작성
4. ChatGPT에서 9:16 기억장면 이미지 생성
5. 이미지를 `remotion/public/images/`에 저장
6. `npm run make -- K00X`
7. 완성 MP4 확인 후 업로드

템플릿 자체의 문제가 발견될 때만 `HistoryCardVideo.tsx`를 수정합니다.
