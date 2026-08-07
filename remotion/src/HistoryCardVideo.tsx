import '@fontsource/noto-sans-kr/500.css';
import '@fontsource/noto-sans-kr/700.css';
import '@fontsource/noto-sans-kr/900.css';

import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import card from './card.json';

const FPS = 30;

const C = {
  bg: '#090B0E',
  bg2: '#12161B',
  text: '#F7F7F5',
  muted: '#B8B8B2',
  accent: '#FF7A00',
  accentSoft: '#FFB15A',
  line: 'rgba(255,255,255,0.14)',
  panel: 'rgba(18,22,27,0.82)',
};

const FONT = '"Noto Sans KR", Pretendard, system-ui, sans-serif';

const Background: React.FC<{
  image?: string;
  imageOpacity?: number;
  darken?: number;
}> = ({image, imageOpacity = 0.24, darken = 0.7}) => {
  const frame = useCurrentFrame();
  const drift = interpolate(frame, [0, 240], [1.02, 1.08], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: C.bg}}>
      {image ? (
        <Img
          src={staticFile(image)}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: imageOpacity,
            filter: 'grayscale(24%) contrast(112%) saturate(82%)',
            transform: `scale(${drift})`,
          }}
        />
      ) : null}

      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, rgba(7,9,12,${Math.min(0.94, darken + 0.04)}) 0%, rgba(9,11,14,${darken}) 50%, rgba(5,7,9,0.97) 100%)`,
        }}
      />

      <AbsoluteFill
        style={{
          background:
            'radial-gradient(circle at 14% 16%, rgba(255,122,0,0.12), transparent 24%), radial-gradient(circle at 82% 76%, rgba(255,122,0,0.06), transparent 26%)',
        }}
      />

      <AbsoluteFill
        style={{
          opacity: 0.28,
          backgroundImage:
            'radial-gradient(rgba(255,255,255,0.14) 0.75px, transparent 0.75px)',
          backgroundSize: '17px 17px',
          maskImage:
            'linear-gradient(180deg, transparent 0%, rgba(0,0,0,0.7) 24%, rgba(0,0,0,0.18) 72%, transparent 100%)',
        }}
      />

      <div
        style={{
          position: 'absolute',
          left: -140,
          bottom: 210,
          width: 620,
          height: 115,
          transform: 'rotate(-7deg)',
          background:
            'linear-gradient(90deg, transparent, rgba(255,122,0,0.13) 26%, rgba(255,122,0,0.05) 70%, transparent)',
          filter: 'blur(10px)',
        }}
      />
    </AbsoluteFill>
  );
};

const PageFrame: React.FC<{
  children: React.ReactNode;
  image?: string;
  imageOpacity?: number;
  darken?: number;
  topTag?: string;
}> = ({children, image, imageOpacity, darken, topTag}) => (
  <AbsoluteFill
    style={{
      color: C.text,
      fontFamily: FONT,
      padding: '118px 72px 126px',
    }}
  >
    <Background image={image} imageOpacity={imageOpacity} darken={darken} />

    <div
      style={{
        position: 'absolute',
        top: 72,
        left: 72,
        right: 72,
        height: 1,
        background: C.line,
      }}
    />

    {topTag ? (
      <div
        style={{
          position: 'absolute',
          top: 86,
          left: 72,
          padding: '11px 20px 12px',
          border: `1px solid rgba(255,122,0,0.42)`,
          borderRadius: 999,
          color: C.accentSoft,
          background: 'rgba(8,10,13,0.72)',
          fontWeight: 700,
          fontSize: 25,
          letterSpacing: -0.8,
        }}
      >
        {topTag}
      </div>
    ) : null}

    <div style={{position: 'relative', zIndex: 2, width: '100%', height: '100%'}}>
      {children}
    </div>
  </AbsoluteFill>
);

const AccentLine: React.FC<{width?: number}> = ({width = 110}) => (
  <div
    style={{
      width,
      height: 8,
      marginTop: 30,
      borderRadius: 999,
      background: C.accent,
      boxShadow: '0 0 22px rgba(255,122,0,0.34)',
    }}
  />
);

const SectionTitle: React.FC<{icon: string; children: React.ReactNode}> = ({
  icon,
  children,
}) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: 18,
      color: C.accent,
      fontSize: 34,
      fontWeight: 900,
      letterSpacing: -1.2,
      marginBottom: 44,
    }}
  >
    <span style={{fontSize: 38}}>{icon}</span>
    <span>{children}</span>
  </div>
);

const Question = () => (
  <PageFrame image={card.image} imageOpacity={0.16} darken={0.82} topTag="기억카드 #001 · 고구려">
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      <div style={{fontSize: 92, fontWeight: 900, color: C.accent, lineHeight: 1}}>Q.</div>
      <div
        style={{
          marginTop: 38,
          maxWidth: 900,
          fontSize: 72,
          lineHeight: 1.28,
          fontWeight: 900,
          letterSpacing: -3.6,
          textShadow: '0 5px 24px rgba(0,0,0,0.55)',
        }}
      >
        {card.question}
      </div>
      <AccentLine />
      <div
        style={{
          marginTop: 46,
          fontSize: 27,
          color: C.muted,
          fontWeight: 500,
          letterSpacing: -0.8,
        }}
      >
        정답을 떠올린 뒤 다음 화면에서 확인하세요.
      </div>
    </div>
  </PageFrame>
);

const Think = () => {
  const frame = useCurrentFrame();
  const sec = Math.max(1, 4 - Math.floor(frame / FPS));
  const progress = 1 - (frame % FPS) / FPS;
  const scale = interpolate(frame % FPS, [0, 15, 29], [0.97, 1.035, 0.97]);

  return (
    <PageFrame image={card.image} imageOpacity={0.08} darken={0.9} topTag="생각할 시간">
      <div
        style={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <div
          style={{
            color: C.accentSoft,
            fontSize: 43,
            fontWeight: 800,
            marginBottom: 60,
            letterSpacing: -1.8,
          }}
        >
          잠깐, 먼저 떠올려 보세요
        </div>

        <div
          style={{
            width: 430,
            height: 430,
            borderRadius: '50%',
            display: 'grid',
            placeItems: 'center',
            transform: `scale(${scale})`,
            background: `conic-gradient(${C.accent} ${progress * 360}deg, rgba(255,255,255,0.09) 0deg)`,
            padding: 12,
            boxShadow: '0 0 70px rgba(255,122,0,0.14)',
          }}
        >
          <div
            style={{
              width: '100%',
              height: '100%',
              borderRadius: '50%',
              display: 'grid',
              placeItems: 'center',
              background: 'rgba(9,11,14,0.96)',
              border: '1px solid rgba(255,255,255,0.08)',
            }}
          >
            <span style={{fontSize: 205, fontWeight: 900, letterSpacing: -8}}>{sec}</span>
          </div>
        </div>

        <div style={{marginTop: 64, fontSize: 29, color: C.muted}}>을지문덕과 연결되는 전투는?</div>
        <Audio src={staticFile('sounds/countdown.wav')} volume={0.75} />
      </div>
    </PageFrame>
  );
};

const Answer = () => (
  <PageFrame image={card.image} imageOpacity={0.14} darken={0.88} topTag="정답 공개">
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      <div style={{fontSize: 33, color: C.muted, fontWeight: 700}}>정답은</div>
      <div
        style={{
          marginTop: 22,
          fontSize: 112,
          lineHeight: 1.05,
          fontWeight: 900,
          color: C.accent,
          letterSpacing: -6,
          textShadow: '0 8px 34px rgba(0,0,0,0.5)',
        }}
      >
        {card.answer}
      </div>
      <AccentLine width={165} />
      <div style={{marginTop: 42, fontSize: 42, lineHeight: 1.45, fontWeight: 700}}>
        612년 <span style={{color: C.accent}}>살수대첩</span>
      </div>
      <div style={{marginTop: 18, fontSize: 29, color: C.muted}}>고구려가 수나라 대군을 크게 격파</div>
      <Audio src={staticFile('sounds/correct.wav')} volume={0.82} />
    </div>
  </PageFrame>
);

const Explanation = () => (
  <PageFrame image={card.image} imageOpacity={0.18} darken={0.88} topTag="시험 포인트">
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      <SectionTitle icon="▣">핵심 해설</SectionTitle>

      <div style={{fontSize: 47, lineHeight: 1.62, fontWeight: 700, letterSpacing: -2.2}}>
        을지문덕은 <span style={{color: C.accent}}>612년 살수</span>에서
        <br />
        수나라 군대를 크게 격파했습니다.
      </div>

      <div
        style={{
          marginTop: 56,
          padding: '29px 32px 30px',
          borderRadius: 22,
          background: C.panel,
          border: '1px solid rgba(255,255,255,0.10)',
          boxShadow: '0 22px 60px rgba(0,0,0,0.2)',
        }}
      >
        <div style={{fontSize: 24, color: C.accentSoft, fontWeight: 800, marginBottom: 12}}>시험 연결</div>
        <div style={{fontSize: 34, fontWeight: 800}}>을지문덕 ↔ 살수대첩 ↔ 수나라</div>
      </div>

      <Audio src={staticFile('tts/K001/explanation.mp3')} volume={1} />
    </div>
  </PageFrame>
);

const Memory = () => (
  <PageFrame topTag="기억용 이미지">
    <div
      style={{
        position: 'absolute',
        inset: '118px 0 0',
        overflow: 'hidden',
      }}
    >
      <Img
        src={staticFile(card.image)}
        style={{width: '100%', height: '100%', objectFit: 'cover'}}
      />
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(180deg, rgba(5,7,9,0.12) 20%, rgba(5,7,9,0.42) 58%, rgba(5,7,9,0.94) 100%)',
        }}
      />
    </div>

    <div
      style={{
        position: 'absolute',
        left: 72,
        right: 72,
        bottom: 145,
        zIndex: 4,
      }}
    >
      <div style={{fontSize: 24, fontWeight: 800, color: C.accentSoft, marginBottom: 16}}>연상 장면 · 역사적 사실과 구분</div>
      <div style={{fontSize: 49, lineHeight: 1.42, fontWeight: 900, letterSpacing: -2.4}}>
        살수의 <span style={{color: C.accent}}>물</span>을 보고
        <br />
        을지문덕의 승리를 떠올리기
      </div>
    </div>
  </PageFrame>
);

const Tip = () => (
  <PageFrame image={card.image} imageOpacity={0.1} darken={0.92} topTag="기억법 한 줄">
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      <div style={{fontSize: 42, color: C.accent, fontWeight: 900}}>★ 마지막으로 이것만</div>
      <div
        style={{
          marginTop: 58,
          fontSize: 70,
          lineHeight: 1.34,
          fontWeight: 900,
          letterSpacing: -3.8,
        }}
      >
        살수대첩
        <br />
        <span style={{color: C.accent}}>→ 을지문덕</span>
        <br />
        → 수나라 격파
      </div>
      <AccentLine width={210} />
      <div style={{marginTop: 42, fontSize: 27, color: C.muted}}>연상은 기억을 돕는 장치, 시험 답은 역사적 사실로.</div>
    </div>
  </PageFrame>
);

export const HistoryCardVideo: React.FC = () => (
  <AbsoluteFill style={{backgroundColor: C.bg}}>
    <Sequence from={0 * FPS} durationInFrames={4 * FPS}>
      <Question />
    </Sequence>
    <Sequence from={4 * FPS} durationInFrames={4 * FPS}>
      <Think />
    </Sequence>
    <Sequence from={8 * FPS} durationInFrames={3 * FPS}>
      <Answer />
    </Sequence>
    <Sequence from={11 * FPS} durationInFrames={9 * FPS}>
      <Explanation />
    </Sequence>
    <Sequence from={20 * FPS} durationInFrames={8 * FPS}>
      <Memory />
    </Sequence>
    <Sequence from={28 * FPS} durationInFrames={4 * FPS}>
      <Tip />
    </Sequence>
  </AbsoluteFill>
);
