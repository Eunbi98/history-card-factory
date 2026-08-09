# history-card-factory

한능검 기출 개념을 `문제 → 문제를 보며 5초 카운트다운 → 정답 → 3초 핵심 해설 → 오답 함정 → 기억 장면 → 기억법 → 오늘의 정리` 구조의 1080×1920 Shorts로 렌더하는 전용 프로젝트입니다.

## 기본 원칙

- `remotion/src/HistoryCardVideo.tsx`는 마스터 템플릿입니다. 영상마다 직접 수정하지 않습니다.
- 영상별 내용은 `data/cards/*.json`에서만 관리합니다.
- 영상 상단에는 EP 번호를 표시하지 않습니다.
- 기억장면 이미지는 9:16 세로형, 텍스트 없는 이미지 사용을 기본으로 합니다.
- 기억법의 강조 단어는 카드 JSON의 `mnemonicParts`에서 지정합니다.

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
  "choices": ["..."],
  "correctChoice": 2,
  "answer": "귀주대첩",
  "explanation": "...",
  "wrongTraps": [["① ...", "..."]],
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
2. 카드 JSON 작성
3. ChatGPT에서 9:16 기억장면 이미지 생성
4. 이미지를 `remotion/public/images/`에 저장
5. `npm run make -- K00X`
6. 완성 MP4 확인 후 업로드

템플릿 자체의 문제가 발견될 때만 `HistoryCardVideo.tsx`를 수정합니다.
