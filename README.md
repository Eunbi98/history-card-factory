# history-card-factory

한능검 기억카드 데이터를 `퀴즈 → 생각할 시간 → 정답 → 핵심 해설 → AI 기억장면 → 기억법 한 줄` 구조의 1080×1920 Shorts로 렌더하는 전용 프로젝트입니다.

## 첫 카드

- K001 을지문덕과 살수대첩
- 32초 / 30fps / 1080×1920

## 설치

```powershell
cd history-card-factory
npm run install:remotion
npm run setup:tts
```

## 첫 영상 실행

```powershell
npm run tts
npm run preview
```

Remotion Studio에서 `HistoryCard`를 확인한 뒤:

```powershell
npm run render
```

출력:

```text
remotion/output/K001_euljimundeok.mp4
```

## 재사용한 기존 설계

- Remotion 4.0.504 기반 세로 영상
- 1080×1920 Composition
- Noto Sans KR
- JSON 데이터 중심 구성
- edge-tts 기반 한국어 TTS
- 효과음 + TTS + 자막/텍스트 레이어 분리

기존 웹 이미지 수집, 주제 추천, 비교형 A/B 로직은 가져오지 않습니다.

## 다음 자동화

1. Notion `한능검 기억카드 Master DB`에서 카드 선택
2. 카드 JSON 생성
3. AI 기억장면 생성
4. TTS 생성
5. Remotion 렌더
6. 제작 완료 상태를 Notion에 반영
