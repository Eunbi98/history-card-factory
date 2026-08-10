import '@fontsource/noto-sans-kr/500.css';
import '@fontsource/noto-sans-kr/700.css';
import '@fontsource/noto-sans-kr/900.css';

import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame} from 'remotion';
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

const KOREAN_WRAP: React.CSSProperties = {
  wordBreak: 'keep-all',
  overflowWrap: 'break-word',
};

type WrongTrap = [string, string];
type MnemonicPart = {text: string; accent?: boolean};
type Card = {
  id: string;
  title: string;
  period?: string;
  sourceExam?: string;
  question: string;
  choices: string[];
  correctChoice: number;
  answer: string;
  explanation: string;
  examLink?: string;
  wrongTraps?: WrongTrap[];
  image: string;
  memoryHeadline?: string;
  memoryTip?: string;
  mnemonicParts?: MnemonicPart[];
  mnemonicSublineParts?: MnemonicPart[];
  recapTitle?: string;
  recapResult?: string;
  recapDetail?: string;
};

const current = card as Card;

const Header: React.FC<{section?: string}> = ({section = '기억 장면'}) => (
  <>
    <div style={{position:'absolute',top:HEADER_TOP,left:SIDE,right:RIGHT_UI,display:'flex',alignItems:'center',gap:18,zIndex:20,fontFamily:FONT,...KOREAN_WRAP}}>
      <span style={{fontSize:24,fontWeight:900,color:ORANGE}}>{current.sourceExam || '기출 개념 참고'}</span>
      <span style={{width:125,height:5,borderRadius:99,background:ORANGE}} />
    </div>
    <div style={{position:'absolute',top:118,left:SIDE,zIndex:20,fontFamily:FONT,fontSize:22,fontWeight:800,color:MUTED,...KOREAN_WRAP}}>{section}</div>
  </>
);

const Stage: React.FC<{children:React.ReactNode;section?:string}> = ({children,section}) => (
  <AbsoluteFill style={{background:BG,color:WHITE,fontFamily:FONT,...KOREAN_WRAP}}>
    <Header section={section} />
    <div style={{position:'absolute',top:CONTENT_TOP,bottom:CONTENT_BOTTOM,left:SIDE,right:RIGHT_UI,display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center',textAlign:'center'}}>
      <div style={{width:'100%',maxWidth:760,margin:'0 auto'}}>{children}</div>
    </div>
  </AbsoluteFill>
);

const renderParts = (parts?: MnemonicPart[]) => (parts || []).map((part,index) => (
  <React.Fragment key={`${part.text}-${index}`}><span style={{color:part.accent ? ORANGE : undefined}}>{part.text}</span></React.Fragment>
));

const ChoiceList: React.FC<{highlight?:number}> = ({highlight}) => (
  <div style={{marginTop:40,display:'grid',gap:14,width:'100%'}}>
    {current.choices.map((text,index) => {
      const selected = highlight === index + 1;
      return (
        <div key={`${index}-${text}`} style={{border:`2px solid ${selected ? ORANGE : '#555A60'}`,background:selected ? ORANGE : 'rgba(255,255,255,.015)',borderRadius:16,padding:'16px 22px',display:'grid',gridTemplateColumns:'48px 1fr',alignItems:'center',fontSize:25,lineHeight:1.4,fontWeight:800,textAlign:'left',boxShadow:selected ? '0 0 24px rgba(255,138,0,.18)' : 'none',...KOREAN_WRAP}}>
          <span style={{color:selected ? WHITE : ORANGE,fontWeight:900}}>{index + 1}</span><span>{text}</span>
        </div>
      );
    })}
  </div>
);

const Question = () => {
  const frame = useCurrentFrame();
  const countdownStart = 2 * FPS;
  const elapsed = Math.max(0, frame - countdownStart);
  const active = frame >= countdownStart;
  const secondsLeft = Math.max(1, 5 - Math.floor(elapsed / FPS));
  const progress = (elapsed % FPS) / FPS;
  const compactQuestion = current.question.replace(/\s/g, '').length <= 18;
  return (
    <Stage section="문제">
      <div style={{position:'relative',width:'100%',paddingTop:active ? 112 : 0}}>
        {active ? (
          <div style={{position:'absolute',top:0,left:'50%',transform:'translateX(-50%)',width:86,height:86,borderRadius:'50%',background:`conic-gradient(${ORANGE} ${360 * (1-progress)}deg, #303338 0deg)`,padding:5,boxShadow:'0 0 20px rgba(255,138,0,.20)',zIndex:5}}>
            <div style={{width:'100%',height:'100%',borderRadius:'50%',background:BG,display:'grid',placeItems:'center',fontSize:35,fontWeight:900,color:WHITE}}>{secondsLeft}</div>
          </div>
        ) : null}
        <div style={{fontSize:22,fontWeight:900,color:active ? YELLOW : ORANGE,marginBottom:18}}>{active ? `${secondsLeft}초 안에 골라보세요` : '5초 안에 골라보세요'}</div>
        <div style={{fontSize:compactQuestion ? 44 : 46,lineHeight:1.34,fontWeight:900,letterSpacing:-2.1,padding:'0 8px',whiteSpace:compactQuestion ? 'nowrap' : 'normal',...KOREAN_WRAP}}><span style={{color:ORANGE}}>Q. </span>{current.question}</div>
        <ChoiceList />
        {active ? <Audio src={staticFile('sounds/countdown.wav')} volume={1} /> : null}
      </div>
    </Stage>
  );
};

const Answer = () => (
  <Stage section="정답 공개">
    <div style={{fontSize:56,fontWeight:900,color:YELLOW}}>정답!</div>
    <div style={{marginTop:28,fontSize:39,lineHeight:1.45,fontWeight:900}}>{current.correctChoice}번 보기입니다.</div>
    <ChoiceList highlight={current.correctChoice} />
    <Audio src={staticFile('sounds/correct.wav')} volume={1} />
  </Stage>
);

const Explanation = () => (
  <Stage section="핵심 해설">
    <div style={{fontSize:52,fontWeight:900,color:GREEN}}>핵심 해설</div>
    <div style={{marginTop:46,fontSize:40,lineHeight:1.62,fontWeight:800,letterSpacing:-1.2,...KOREAN_WRAP}}>{current.explanation}</div>
    {current.examLink ? <div style={{marginTop:42,fontSize:27,lineHeight:1.55,color:'#E6E6E2',fontWeight:700,...KOREAN_WRAP}}>{current.examLink}</div> : null}
    <Audio src={staticFile(`tts/${current.id}/explanation.mp3`)} volume={1} />
  </Stage>
);

const Wrong = () => (
  <Stage section="오답 함정">
    <div style={{fontSize:52,fontWeight:900,color:RED}}>오답 함정</div>
    <div style={{marginTop:42,display:'grid',gridTemplateColumns:'1fr 1fr',gap:22,width:'100%'}}>
      {(current.wrongTraps || []).map(([title,description]) => (
        <div key={title} style={{minHeight:190,padding:'26px 24px',border:'1px solid #45494D',borderRadius:18,background:'rgba(255,255,255,.025)',display:'flex',flexDirection:'column',justifyContent:'center',...KOREAN_WRAP}}>
          <div style={{fontSize:27,fontWeight:900}}>{title}</div><div style={{marginTop:16,fontSize:23,lineHeight:1.5,color:'#E4E4E1',fontWeight:700}}>{description}</div>
        </div>
      ))}
    </div>
  </Stage>
);

const MemoryImage = () => (
  <AbsoluteFill style={{background:BG,color:WHITE,fontFamily:FONT,overflow:'hidden',...KOREAN_WRAP}}>
    <Img src={staticFile(current.image)} style={{position:'absolute',inset:0,width:'100%',height:'100%',objectFit:'cover',objectPosition:'50% 50%'}} />
    <AbsoluteFill style={{background:'linear-gradient(180deg,rgba(0,0,0,.24) 0%,rgba(0,0,0,.02) 36%,rgba(0,0,0,.04) 58%,rgba(0,0,0,.82) 100%)',zIndex:2}} />
    <Header section="기억 장면" />
    <div style={{position:'absolute',left:SIDE,right:RIGHT_UI,bottom:285,zIndex:10,textAlign:'center'}}>
      <div style={{maxWidth:760,margin:'0 auto'}}>
        <div style={{fontSize:20,fontWeight:900,color:YELLOW}}>기억용 연상 · 역사적 사실과 구분</div>
        <div style={{marginTop:14,fontSize:43,lineHeight:1.35,fontWeight:900,...KOREAN_WRAP}}>{current.memoryHeadline || current.memoryTip || current.title}</div>
      </div>
    </div>
  </AbsoluteFill>
);

const Mnemonic = () => (
  <Stage section="기억법">
    <div style={{fontSize:54,fontWeight:900,color:GREEN}}>기억법</div>
    <div style={{marginTop:50,fontSize:46,lineHeight:1.58,fontWeight:900,...KOREAN_WRAP}}>{current.mnemonicParts?.length ? renderParts(current.mnemonicParts) : current.memoryTip}</div>
    {current.mnemonicSublineParts?.length ? <div style={{marginTop:38,fontSize:29,lineHeight:1.62,color:'#E2E2DE',fontWeight:800,...KOREAN_WRAP}}>{renderParts(current.mnemonicSublineParts)}</div> : null}
  </Stage>
);

const Recap = () => (
  <Stage section="오늘의 정리">
    <div style={{fontSize:54,fontWeight:900,color:YELLOW}}>오늘의 정리</div>
    <div style={{marginTop:48,border:'2px solid #665A49',borderRadius:22,padding:'42px 36px',fontSize:43,lineHeight:1.55,fontWeight:900,...KOREAN_WRAP}}>
      {current.recapTitle || current.title}<br /><span style={{color:ORANGE,fontSize:50}}>↓</span><br /><span style={{color:'#FFD98A'}}>{current.recapResult || current.answer}</span>
    </div>
    {current.recapDetail ? <div style={{marginTop:38,fontSize:29,lineHeight:1.6,fontWeight:700,...KOREAN_WRAP}}>{current.recapDetail}</div> : null}
  </Stage>
);

const CTA = () => (
  <Stage section="다음 문제">
    <div style={{fontSize:50,lineHeight:1.55,fontWeight:900,...KOREAN_WRAP}}>역사 공부,<br />매일 <span style={{color:ORANGE}}>1분</span>이면 충분!</div>
    <div style={{margin:'50px auto 0',width:'82%',borderTop:'2px solid #6B655F',paddingTop:30,fontSize:27,fontWeight:800}}>좋아요　 댓글　 저장</div>
    <div style={{marginTop:60,fontSize:32,lineHeight:1.55,fontWeight:800,...KOREAN_WRAP}}>다음 기억 장면에서<br />또 만나요!</div>
  </Stage>
);

export const HistoryCardVideo: React.FC = () => (
  <AbsoluteFill style={{background:BG}}>
    <Sequence from={0*FPS} durationInFrames={7*FPS}><Question /></Sequence>
    <Sequence from={7*FPS} durationInFrames={3*FPS}><Answer /></Sequence>
    <Sequence from={10*FPS} durationInFrames={3*FPS}><Explanation /></Sequence>
    <Sequence from={13*FPS} durationInFrames={4*FPS}><Wrong /></Sequence>
    <Sequence from={17*FPS} durationInFrames={6*FPS}><MemoryImage /></Sequence>
    <Sequence from={23*FPS} durationInFrames={3*FPS}><Mnemonic /></Sequence>
    <Sequence from={26*FPS} durationInFrames={4*FPS}><Recap /></Sequence>
    <Sequence from={30*FPS} durationInFrames={3*FPS}><CTA /></Sequence>
  </AbsoluteFill>
);
