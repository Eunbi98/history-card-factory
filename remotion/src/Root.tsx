import React from 'react';
import {Composition} from 'remotion';
import {HistoryCardVideo} from './HistoryCardVideo';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="HistoryCard"
    component={HistoryCardVideo}
    durationInFrames={32 * 30}
    fps={30}
    width={1080}
    height={1920}
  />
);
