import { styled } from '../styles/theme';
import { motion, useScroll, useTransform, useSpring, MotionValue } from 'framer-motion';
import { useRef } from 'react';

const CanvasContainer = styled('div', {
  position: 'fixed',
  inset: 0,
  overflow: 'hidden',
  background: '$backgroundDeep',
  perspective: '1000px',
});

const ParallaxLayer = styled(motion.div, {
  position: 'absolute',
  width: '100%',
  height: '100%',
  willChange: 'transform',
});

const BackgroundLayer = styled(ParallaxLayer, {
  background: `
    radial-gradient(ellipse at 20% 80%, rgba(139, 21, 56, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(184, 115, 51, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 50%, rgba(26, 22, 18, 0.95) 0%, $backgroundDeep 100%)
  `,
});

const MidgroundLayer = styled(ParallaxLayer, {
  '&::before': {
    content: '',
    position: 'absolute',
    inset: 0,
    background: `
      radial-gradient(circle at 30% 70%, rgba(212, 165, 116, 0.08) 0%, transparent 40%),
      radial-gradient(circle at 70% 30%, rgba(232, 196, 154, 0.05) 0%, transparent 30%)
    `,
  },
});

const ForegroundLayer = styled(ParallaxLayer, {
  pointerEvents: 'none',
  '&::after': {
    content: '',
    position: 'absolute',
    inset: 0,
    background: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 400 400\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noiseFilter)\'/%3E%3C/svg%3E")',
    opacity: 0.03,
    mixBlendMode: 'overlay',
  },
});

const DepthLine = styled(motion.div, {
  position: 'absolute',
  left: 0,
  right: 0,
  height: '1px',
  background: 'linear-gradient(90deg, transparent, $glassBorder, transparent)',
  opacity: 0.3,
});

interface LayerConfig {
  speed: number;
  rotation?: { x: number; y: number };
  scale?: number;
}

function ParallaxDepthLayer({
  children,
  depth,
  mouseX,
  mouseY,
}: {
  children: React.ReactNode;
  depth: number;
  mouseX: MotionValue<number>;
  mouseY: MotionValue<number>;
}) {
  const config: LayerConfig = {
    speed: 0.02 * depth,
    rotation: { x: 0.02 * depth, y: 0.02 * depth },
  };

  const moveX = useTransform(mouseX, [0, 1], [-30 * depth, 30 * depth]);
  const moveY = useTransform(mouseY, [0, 1], [-20 * depth, 20 * depth]);
  const rotateX = useTransform(mouseY, [0, 1], [-config.rotation!.x * 100, config.rotation!.x * 100]);
  const rotateY = useTransform(mouseX, [0, 1], [-config.rotation!.y * 100, config.rotation!.y * 100]);

  return (
    <ParallaxLayer
      style={{
        x: moveX,
        y: moveY,
        rotateX,
        rotateY,
      }}
    >
      {children}
    </ParallaxLayer>
  );
}

export function MainCanvas({ children }: { children: React.ReactNode }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollY } = useScroll();

  const smoothScrollY = useSpring(scrollY, { stiffness: 100, damping: 30 });

  const mouseX = useTransform(smoothScrollY, [0, 1000], [0.5, 0.5]);
  const mouseY = useTransform(smoothScrollY, [0, 1000], [0.5, 0.5]);

  return (
    <CanvasContainer ref={containerRef}>
      <BackgroundLayer />
      <MidgroundLayer />
      <ForegroundLayer />

      <DepthLine
        style={{ top: '15%', scaleY: useTransform(smoothScrollY, [0, 500], [0, 2]) }}
      />
      <DepthLine
        style={{ top: '85%', scaleY: useTransform(smoothScrollY, [0, 500], [0, 1.5]) }}
      />

      <ParallaxDepthLayer depth={1} mouseX={mouseX} mouseY={mouseY}>
        {children}
      </ParallaxDepthLayer>
    </CanvasContainer>
  );
}