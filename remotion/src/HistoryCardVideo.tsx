import '@fontsource/noto-sans-kr/500.css';
import '@fontsource/noto-sans-kr/700.css';
import '@fontsource/noto-sans-kr/900.css';

import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import card from './card.json';

const FPS = 30;
const ORANGE = '#FF8A00';
const YELLOW = '#FFD52A';
const GREEN = '#7ED957';
const RED = '#FF5A49';
const WHITE = '#F7F7F5';
const MUTED = '#BDBDB8';
const BG = '#050607';
const FONT = '"Noto Sans KR", Pretendard, system-ui, sans-serif';

const HEADER_TOP = 72;
const CONTENT_TOP = 185;
const CONTENT_BOTTOM = 285;
const SIDE = 92;
const RIGHT_UI = 170;

const Header: React.FC<{section?: string}> = ({section = '기억 장면'}) => (
  <>
    <div
      style={{
        position: 'absolute',
        top: HEADER_TOP,
        left: SIDE,
        right: RIGHT_UI,
        display: 'flex',
        alignItems: 'center',
        gap: 18,
        zIndex: 20,
        fontFamily: FONT,
      }}
    >
      <span style={{fontSize: 24, fontWeight: 900, color: ORANGE}}>
        제77회 기본 · 기출 개념 참고
      </span>
      <span
        style={{
          width: 125,
          height: 5,
          borderRadius: 99,
          background: ORANGE,
        }}
      />
    </div>

    <div
      style={{
        position: 'absolute',
        top: 118,
        left: SIDE,
        zIndex: 20,
        fontFamily: FONT,
        fontSize: 22,
        fontWeight: 800,
        color: MUTED,
      }}
    >
      EP001 · {section}
    </div>
  </>
);

const Stage: React.FC<{
  children: React.ReactNode;
  section?: string;
}> = ({children, section}) => (
  <AbsoluteFill style={{background: BG, color: WHITE, fontFamily: FONT}}>
    <Header section={section} />

    <div
      style={{
        position: 'absolute',
        top: CONTENT_TOP,
        bottom: CONTENT_BOTTOM,
        left: SIDE,
        right: RIGHT_UI,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 760,
          margin: '0 auto',
        }}
      >
        {children}
      </div>
    </div>
  </AbsoluteFill>
);

const choices = [
  '귀주대첩에서 승리하였다',
  '살수에서 수나라 대군을 격파하였다',
  '안시성에서 당군을 물리쳤다',
  '한산도 대첩에서 승리하였다',
  '황산벌에서 신라군을 격파하였다',
];

const ChoiceList: React.FC<{highlight?: number}> = ({highlight}) => (
  <div style={{marginTop: 40, display: 'grid', gap: 14, width: '100%'}}>
    {choices.map((text, index) => {
      const selected = highlight === index + 1;

      return (
        <div
          key={text}
          style={{
            border: `2px solid ${selected ? ORANGE : '#555A60'}`,
            background: selected ? ORANGE : 'rgba(255,255,255,.015)',
            borderRadius: 16,
            padding: '16px 22px',
            display: 'grid',
            gridTemplateColumns: '48px 1fr',
            alignItems: 'center',
            fontSize: 25,
            lineHeight: 1.4,
            fontWeight: 800,
            textAlign: 'left',
            boxShadow: selected ? '0 0 24px rgba(255,138,0,.18)' : 'none',
          }}
        >
          <span
            style={{
              color: selected ? WHITE : ORANGE,
              fontWeight: 900,
            }}
          >
            {index + 1}
          </span>
          <span>{text}</span>
        </div>
      );
    })}
  </div>
);

const Question = () => {
  const frame = useCurrentFrame();

  const countdownStart = 2 * FPS;
  const elapsed = Math.max(0, frame - countdownStart);
  const countdownActive = frame >= countdownStart;
  const secondsLeft = Math.max(1, 5 - Math.floor(elapsed / FPS));
  const secondProgress = (elapsed % FPS) / FPS;

  return (
    <Stage section="문제">
      <div style={{position: 'relative', width: '100%'}}>
        <div
          style={{
            fontSize: 22,
            fontWeight: 900,
            color: countdownActive ? YELLOW : ORANGE,
            marginBottom: 16,
          }}
        >
          {countdownActive
            ? `${secondsLeft}초 안에 골라보세요`
            : '5초 안에 골라보세요'}
        </div>

        <div
          style={{
            fontSize: 50,
            lineHeight: 1.34,
            fontWeight: 900,
            letterSpacing: -2.2,
          }}
        >
          <span style={{color: ORANGE}}>Q. </span>
          다음 중 을지문덕의
          <br />
          활동으로 옳은 것은?
        </div>

        <ChoiceList />

        {countdownActive ? (
          <div
            style={{
              position: 'absolute',
              right: -18,
              top: -6,
              width: 82,
              height: 82,
              borderRadius: '50%',
              background: `conic-gradient(${ORANGE} ${
                360 * (1 - secondProgress)
              }deg, #303338 0deg)`,
              padding: 5,
              boxShadow: '0 0 18px rgba(255,138,0,.18)',
            }}
          >
            <div
              style={{
                width: '100%',
                height: '100%',
                borderRadius: '50%',
                background: BG,
                display: 'grid',
                placeItems: 'center',
                fontSize: 34,
                fontWeight: 900,
                color: WHITE,
              }}
            >
              {secondsLeft}
            </div>
          </div>
        ) : null}

        {countdownActive ? (
          <Audio src={staticFile('sounds/countdown.wav')} volume={1} />
        ) : null}
      </div>
    </Stage>
  );
};

const Answer = () => (
  <Stage section="정답 공개">
    <div style={{fontSize: 56, fontWeight: 900, color: YELLOW}}>정답!</div>

    <div
      style={{
        marginTop: 28,
        fontSize: 39,
        lineHeight: 1.45,
        fontWeight: 900,
      }}
    >
      2번 보기입니다.
    </div>

    <ChoiceList highlight={2} />

    <Audio src={staticFile('sounds/correct.wav')} volume={1} />
  </Stage>
);

const Explanation = () => (
  <Stage section="핵심 해설">
    <div style={{fontSize: 52, fontWeight: 900, color: GREEN}}>
      핵심 해설
    </div>

    <div
      style={{
        marginTop: 46,
        fontSize: 38,
        lineHeight: 1.62,
        fontWeight: 800,
        letterSpacing: -1.4,
      }}
    >
      을지문덕은 살수에서
      <br />
      수나라 대군을 기습하여
      <br />
      <span style={{color: YELLOW}}>대승</span>을 거두었습니다.
    </div>

    <div
      style={{
        marginTop: 42,
        fontSize: 27,
        lineHeight: 1.55,
        color: '#E6E6E2',
        fontWeight: 700,
      }}
    >
      612년 · 을지문덕 · 살수대첩 · 수나라
    </div>

    <Audio src={staticFile('tts/K001/explanation.mp3')} volume={1} />
  </Stage>
);

const Wrong = () => (
  <Stage section="오답 함정">
    <div style={{fontSize: 52, fontWeight: 900, color: RED}}>
      오답 함정
    </div>

    <div
      style={{
        marginTop: 42,
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 22,
        width: '100%',
      }}
    >
      {[
        ['① 귀주대첩', '강감찬 · 거란'],
        ['③ 안시성 전투', '양만춘 · 당'],
        ['④ 한산도 대첩', '이순신 · 왜군'],
        ['⑤ 황산벌 전투', '계백 · 신라'],
      ].map(([title, description]) => (
        <div
          key={title}
          style={{
            minHeight: 190,
            padding: '26px 24px',
            border: '1px solid #45494D',
            borderRadius: 18,
            background: 'rgba(255,255,255,.025)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}
        >
          <div style={{fontSize: 27, fontWeight: 900}}>{title}</div>
          <div
            style={{
              marginTop: 16,
              fontSize: 23,
              lineHeight: 1.5,
              color: '#E4E4E1',
              fontWeight: 700,
            }}
          >
            {description}
          </div>
        </div>
      ))}
    </div>
  </Stage>
);

const MemoryImage = () => (
  <AbsoluteFill style={{background: BG, color: WHITE, fontFamily: FONT}}>
    <Img
      src={staticFile(card.image)}
      style={{
        position: 'absolute',
        inset: 0,
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        objectPosition: 'center center',
      }}
    />

    <AbsoluteFill
      style={{
        background:
          'linear-gradient(180deg,rgba(0,0,0,.20) 0%,rgba(0,0,0,.02) 46%,rgba(0,0,0,.86) 100%)',
      }}
    />

    <Header section="기억 장면" />

    <div
      style={{
        position: 'absolute',
        left: SIDE,
        right: RIGHT_UI,
        bottom: 300,
        zIndex: 10,
        textAlign: 'center',
      }}
    >
      <div style={{maxWidth: 760, margin: '0 auto'}}>
        <div style={{fontSize: 21, fontWeight: 900, color: YELLOW}}>
          기억용 연상 · 역사적 사실과 구분
        </div>

        <div
          style={{
            marginTop: 16,
            fontSize: 47,
            lineHeight: 1.34,
            fontWeight: 900,
          }}
        >
          살수의 <span style={{color: ORANGE}}>물</span>과
          <br />
          을지문덕의 승리를 연결
        </div>
      </div>
    </div>
  </AbsoluteFill>
);

const Mnemonic = () => (
  <Stage section="기억법">
    <div style={{fontSize: 54, fontWeight: 900, color: GREEN}}>기억법</div>

    <div
      style={{
        marginTop: 50,
        fontSize: 44,
        lineHeight: 1.58,
        fontWeight: 900,
      }}
    >
      “살수의 <span style={{color: YELLOW}}>물</span>에 담가,
      <br />
      을지문덕은 <span style={{color: YELLOW}}>수</span>를 이겼다!”
    </div>

    <div
      style={{
        marginTop: 42,
        fontSize: 28,
        lineHeight: 1.62,
        color: '#E2E2DE',
        fontWeight: 700,
      }}
    >
      살수 → 물 → 수나라 → 을지문덕
    </div>
  </Stage>
);

const Recap = () => (
  <Stage section="오늘의 정리">
    <div style={{fontSize: 54, fontWeight: 900, color: YELLOW}}>
      오늘의 정리
    </div>

    <div
      style={{
        marginTop: 48,
        border: '2px solid #665A49',
        borderRadius: 22,
        padding: '42px 36px',
        fontSize: 43,
        lineHeight: 1.55,
        fontWeight: 900,
      }}
    >
      을지문덕
      <br />
      <span style={{color: ORANGE, fontSize: 50}}>↓</span>
      <br />
      <span style={{color: '#FFD98A'}}>살수대첩 승리</span>
    </div>

    <div
      style={{
        marginTop: 38,
        fontSize: 29,
        lineHeight: 1.6,
        fontWeight: 700,
      }}
    >
      612년, 수나라 대군을 격파
    </div>
  </Stage>
);

const CTA = () => (
  <Stage section="다음 문제">
    <div style={{fontSize: 50, lineHeight: 1.55, fontWeight: 900}}>
      역사 공부,
      <br />
      매일 <span style={{color: ORANGE}}>1분</span>이면 충분!
    </div>

    <div
      style={{
        margin: '50px auto 0',
        width: '82%',
        borderTop: '2px solid #6B655F',
        paddingTop: 30,
        fontSize: 27,
        fontWeight: 800,
      }}
    >
      좋아요　 댓글　 저장
    </div>

    <div
      style={{
        marginTop: 60,
        fontSize: 32,
        lineHeight: 1.55,
        fontWeight: 800,
      }}
    >
      다음 기억 장면에서
      <br />
      또 만나요!
    </div>
  </Stage>
);

export const HistoryCardVideo: React.FC = () => (
  <AbsoluteFill style={{background: BG}}>
    <Sequence from={0 * FPS} durationInFrames={7 * FPS}>
      <Question />
    </Sequence>

    <Sequence from={7 * FPS} durationInFrames={3 * FPS}>
      <Answer />
    </Sequence>

    <Sequence from={10 * FPS} durationInFrames={3 * FPS}>
      <Explanation />
    </Sequence>

    <Sequence from={13 * FPS} durationInFrames={4 * FPS}>
      <Wrong />
    </Sequence>

    <Sequence from={17 * FPS} durationInFrames={6 * FPS}>
      <MemoryImage />
    </Sequence>

    <Sequence from={23 * FPS} durationInFrames={3 * FPS}>
      <Mnemonic />
    </Sequence>

    <Sequence from={26 * FPS} durationInFrames={4 * FPS}>
      <Recap />
    </Sequence>

    <Sequence from={30 * FPS} durationInFrames={3 * FPS}>
      <CTA />
    </Sequence>
  </AbsoluteFill>
);
