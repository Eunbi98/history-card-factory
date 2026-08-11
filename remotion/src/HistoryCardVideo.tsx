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

type WrongTrap = [string, string, string?];
type MnemonicPart = {text: string; accent?: boolean};
type TimelineItem = {year: string; title: string; detail?: string; accent?: boolean};
type Card = {
  id: string;
  title: string;
  period?: string;
  sourceExam?: string;
  question: string;
  questionShort?: string;
  choices: string[];
  correctChoice: number;
  answer: string;
  explanation: string;
  explanationShort?: string;
  explanationHighlights?: string[];
  explanationLayout?: 'default' | 'timeline';
  timelineTitle?: string;
  timelineItems?: TimelineItem[];
  examLink?: string;
  wrongTraps?: WrongTrap[];
  wrongTrapsShort?: WrongTrap[];
  image: string;
  memoryHeadline?: string;
  memoryTip?: string;
  mnemonicLead?: string;
  mnemonicBodyParts?: MnemonicPart[];
  mnemonicParts?: MnemonicPart[];
  mnemonicSublineParts?: MnemonicPart[];
  recapTitle?: string;
  recapResult?: string;
  recapDetail?: string;
};

const current = card as Card;

const textLength = (text = '') => text.replace(/\s/g, '').length;
const displayQuestion = current.questionShort?.trim() || current.question;
const displayExplanation = current.explanationShort?.trim() || current.explanation;
const displayWrongTraps = current.wrongTrapsShort?.length ? current.wrongTrapsShort : (current.wrongTraps || []);

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

const renderHighlightedText = (text: string, highlights?: string[]) => {
  const keywords = (highlights || []).filter(Boolean).sort((a,b) => b.length - a.length);
  if (!keywords.length) return text;
  const escaped = keywords.map((keyword) => keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
  const regex = new RegExp(`(${escaped.join('|')})`, 'g');
  return text.split(regex).map((part,index) => {
    const highlighted = keywords.includes(part);
    return <React.Fragment key={`${part}-${index}`}><span style={{color:highlighted ? ORANGE : undefined,fontWeight:highlighted ? 900 : undefined}}>{part}</span></React.Fragment>;
  });
};

const ChoiceList: React.FC<{highlight?:number}> = ({highlight}) => (
  <div style={{marginTop:36,display:'grid',gap:13,width:'100%'}}>
    {current.choices.map((text,index) => {
      const selected = highlight === index + 1;
      const choiceLength = textLength(text);
      const choiceFontSize = choiceLength > 34 ? 23 : choiceLength > 24 ? 24 : 25;
      return (
        <div key={`${index}-${text}`} style={{border:`2px solid ${selected ? ORANGE : '#555A60'}`,background:selected ? ORANGE : 'rgba(255,255,255,.015)',borderRadius:16,padding:choiceLength > 34 ? '13px 20px' : '15px 22px',display:'grid',gridTemplateColumns:'48px 1fr',alignItems:'center',fontSize:choiceFontSize,lineHeight:1.38,fontWeight:800,textAlign:'left',boxShadow:selected ? '0 0 24px rgba(255,138,0,.18)' : 'none',...KOREAN_WRAP}}>
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
  const questionLength = textLength(displayQuestion);
  const compactQuestion = questionLength <= 18;
  const questionFontSize = compactQuestion ? 44 : questionLength > 54 ? 38 : questionLength > 40 ? 41 : 44;
  const questionLineHeight = questionLength > 54 ? 1.28 : 1.32;
  return (
    <Stage section="문제">
      <div style={{position:'relative',width:'100%',paddingTop:active ? 112 : 0}}>
        {active ? (
          <div style={{position:'absolute',top:0,left:'50%',transform:'translateX(-50%)',width:86,height:86,borderRadius:'50%',background:`conic-gradient(${ORANGE} ${360 * (1-progress)}deg, #303338 0deg)`,padding:5,boxShadow:'0 0 20px rgba(255,138,0,.20)',zIndex:5}}>
            <div style={{width:'100%',height:'100%',borderRadius:'50%',background:BG,display:'grid',placeItems:'center',fontSize:35,fontWeight:900,color:WHITE}}>{secondsLeft}</div>
          </div>
        ) : null}
        <div style={{fontSize:22,fontWeight:900,color:active ? YELLOW : ORANGE,marginBottom:16}}>{active ? `${secondsLeft}초 안에 골라보세요` : '5초 안에 골라보세요'}</div>
        <div style={{fontSize:questionFontSize,lineHeight:questionLineHeight,fontWeight:900,letterSpacing:-2,padding:'0 8px',whiteSpace:compactQuestion ? 'nowrap' : 'normal',...KOREAN_WRAP}}><span style={{color:ORANGE}}>Q. </span>{displayQuestion}</div>
        <ChoiceList />
        {[0,1,2,3,4].map((index) => (
          <Sequence key={index} from={countdownStart + index * FPS} durationInFrames={Math.round(FPS * 0.45)}>
            <Audio src={staticFile('sounds/countdown.wav')} volume={1} />
          </Sequence>
        ))}
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

const Explanation = () => {
  const explanationLength = textLength(displayExplanation);
  const shortMode = Boolean(current.explanationShort?.trim());
  const explanationFontSize = shortMode ? 44 : explanationLength > 115 ? 34 : explanationLength > 82 ? 37 : 40;
  const explanationLineHeight = shortMode ? 1.5 : explanationLength > 115 ? 1.48 : 1.55;
  return (
    <Stage section="핵심 해설">
      <div style={{fontSize:52,fontWeight:900,color:GREEN}}>핵심 해설</div>
      <div style={{marginTop:shortMode ? 48 : 40,fontSize:explanationFontSize,lineHeight:explanationLineHeight,fontWeight:800,letterSpacing:-1.2,...KOREAN_WRAP}}>{renderHighlightedText(displayExplanation,current.explanationHighlights)}</div>
      {!shortMode && current.examLink ? <div style={{marginTop:32,fontSize:27,lineHeight:1.48,color:'#E6E6E2',fontWeight:800,...KOREAN_WRAP}}>{renderHighlightedText(current.examLink,current.explanationHighlights)}</div> : null}
    </Stage>
  );
};

const CIRCLED_NUMBERS = ['①','②','③','④','⑤','⑥','⑦','⑧','⑨'];

const getTrapChoiceNumber = (title: string): number | null => {
  const circled = CIRCLED_NUMBERS.findIndex((mark) => title.trim().startsWith(mark));
  if (circled >= 0) return circled + 1;
  const numeric = title.trim().match(/^(\d+)/);
  return numeric ? Number(numeric[1]) : null;
};

const getDefaultTrapKeyword = (title: string) => title
  .replace(/^[①②③④⑤⑥⑦⑧⑨\d.\s]+/, '')
  .trim();

const HighlightedChoice: React.FC<{text:string;keyword:string}> = ({text,keyword}) => {
  if (!keyword || !text.includes(keyword)) return <>{text}</>;
  const [before,...rest] = text.split(keyword);
  return <>{before}<span style={{color:ORANGE,fontWeight:900}}>{keyword}</span>{rest.join(keyword)}</>;
};

const TimelineWrong = () => {
  const items = current.timelineItems || [];
  return (
    <Stage section="사건 흐름">
      <div style={{fontSize:44,fontWeight:900,color:RED}}>{current.timelineTitle || '사건 흐름'}</div>
      <div style={{marginTop:30,width:'100%',display:'grid',gap:0,textAlign:'left'}}>
        {items.map((item,index) => (
          <div key={`${item.year}-${item.title}`} style={{position:'relative',display:'grid',gridTemplateColumns:'118px 34px minmax(0,1fr)',columnGap:12,minHeight:116}}>
            <div style={{paddingTop:4,fontSize:28,fontWeight:900,color:item.accent ? YELLOW : ORANGE,textAlign:'right'}}>{item.year}</div>
            <div style={{position:'relative',display:'flex',justifyContent:'center'}}>
              {index < items.length - 1 ? <div style={{position:'absolute',top:24,bottom:-6,width:4,background:'#555A60',borderRadius:99}} /> : null}
              <div style={{marginTop:9,width:20,height:20,borderRadius:'50%',background:item.accent ? YELLOW : ORANGE,boxShadow:item.accent ? '0 0 18px rgba(255,213,42,.35)' : 'none',zIndex:2}} />
            </div>
            <div style={{paddingBottom:24}}>
              <div style={{fontSize:30,lineHeight:1.28,fontWeight:900,color:item.accent ? YELLOW : WHITE,...KOREAN_WRAP}}>{item.title}</div>
              {item.detail ? <div style={{marginTop:8,fontSize:23,lineHeight:1.38,fontWeight:800,color:'#D8D8D3',...KOREAN_WRAP}}>{item.detail}</div> : null}
            </div>
          </div>
        ))}
      </div>
    </Stage>
  );
};

const Wrong = () => {
  if (current.explanationLayout === 'timeline' && current.timelineItems?.length) return <TimelineWrong />;
  const shortMode = Boolean(current.wrongTrapsShort?.length);
  const wrongQuestion = displayQuestion;
  const wrongQuestionLength = textLength(wrongQuestion);
  const wrongQuestionFontSize = wrongQuestionLength > 54 ? 27 : wrongQuestionLength > 40 ? 29 : 31;
  return (
    <Stage section="오답 함정">
      <div style={{fontSize:44,fontWeight:900,color:RED}}>오답 함정</div>
      <div style={{marginTop:16,fontSize:wrongQuestionFontSize,lineHeight:1.3,fontWeight:900,letterSpacing:-1.2,...KOREAN_WRAP}}><span style={{color:ORANGE}}>Q. </span>{wrongQuestion}</div>
      <div style={{marginTop:shortMode ? 24 : 26,display:'grid',gap:shortMode ? 12 : 13,width:'100%'}}>
        {displayWrongTraps.map(([title,description,explicitKeyword]) => {
          const choiceNumber = getTrapChoiceNumber(title);
          const choiceText = choiceNumber ? current.choices[choiceNumber - 1] : title;
          const keyword = explicitKeyword || getDefaultTrapKeyword(title);
          const descriptionLength = textLength(description);
          const longDescription = !shortMode && descriptionLength > 18;
          return (
            <div key={`${title}-${description}`} style={{border:'2px solid #555A60',background:'rgba(255,255,255,.015)',borderRadius:16,padding:shortMode ? '14px 18px' : longDescription ? '15px 19px 17px' : '16px 19px',display:'grid',gridTemplateColumns:shortMode ? '46px minmax(0,1fr) 230px' : longDescription ? '46px minmax(0,1fr)' : '46px minmax(0,1fr) 210px',columnGap:13,rowGap:9,alignItems:'center',fontSize:shortMode ? 24 : longDescription ? 25 : 24,lineHeight:1.35,fontWeight:800,textAlign:'left',...KOREAN_WRAP}}>
              <span style={{color:ORANGE,fontWeight:900}}>{choiceNumber || '•'}</span>
              <span><HighlightedChoice text={choiceText} keyword={keyword} /></span>
              {longDescription ? (
                <div style={{gridColumn:'2 / -1',borderTop:'1px solid #555A60',paddingTop:9,color:YELLOW,fontSize:23,lineHeight:1.38,fontWeight:900,textAlign:'left',...KOREAN_WRAP}}>{description}</div>
              ) : (
                <span style={{borderLeft:'1px solid #555A60',paddingLeft:15,color:YELLOW,fontSize:shortMode ? 22 : 23,fontWeight:900,textAlign:'left',...KOREAN_WRAP}}>{description}</span>
              )}
            </div>
          );
        })}
      </div>
    </Stage>
  );
};

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
    {current.mnemonicLead && current.mnemonicBodyParts?.length ? (
      <>
        <div style={{marginTop:44,fontSize:52,lineHeight:1.3,fontWeight:900,color:ORANGE,...KOREAN_WRAP}}>{current.mnemonicLead}</div>
        <div style={{marginTop:28,fontSize:38,lineHeight:1.58,fontWeight:900,...KOREAN_WRAP}}>{renderParts(current.mnemonicBodyParts)}</div>
      </>
    ) : (
      <div style={{marginTop:50,fontSize:46,lineHeight:1.58,fontWeight:900,...KOREAN_WRAP}}>{current.mnemonicParts?.length ? renderParts(current.mnemonicParts) : current.memoryTip}</div>
    )}
    {!current.mnemonicLead && current.mnemonicSublineParts?.length ? <div style={{marginTop:38,fontSize:29,lineHeight:1.62,color:'#E2E2DE',fontWeight:800,...KOREAN_WRAP}}>{renderParts(current.mnemonicSublineParts)}</div> : null}
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
    <Sequence from={10*FPS} durationInFrames={4*FPS}><Explanation /></Sequence>
    <Sequence from={14*FPS} durationInFrames={4*FPS}><Wrong /></Sequence>
    <Sequence from={18*FPS} durationInFrames={6*FPS}><MemoryImage /></Sequence>
    <Sequence from={24*FPS} durationInFrames={3*FPS}><Mnemonic /></Sequence>
    <Sequence from={27*FPS} durationInFrames={4*FPS}><Recap /></Sequence>
    <Sequence from={31*FPS} durationInFrames={3*FPS}><CTA /></Sequence>
  </AbsoluteFill>
);
