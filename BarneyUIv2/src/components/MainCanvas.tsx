import React, { useRef, useEffect, useState } from 'react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import { styled } from '../styles/theme';

const CanvasWrapper = styled('div', {
  position: 'fixed',
  inset: 0,
  zIndex: 0,
  background: '$backgroundDeep',
  overflow: 'hidden',
  perspective: '2000px',
});

const StyledCanvas = styled(motion.canvas, {
  position: 'absolute',
  width: '110% !important',
  height: '110% !important',
  top: '-5%',
  left: '-5%',
  objectFit: 'cover',
  willChange: 'transform',
});

const DepthOverlay = styled('div', {
  position: 'absolute',
  inset: 0,
  background: `radial-gradient(circle at 50% 50%, transparent 20%, rgba(5, 4, 4, 0.4) 100%)`,
  pointerEvents: 'none',
});

const UIStage = styled('div', {
  position: 'relative',
  width: '100%',
  height: '100%',
  zIndex: 1,
  transformStyle: 'preserve-3d',
});

const Stage = motion(UIStage);

interface MainCanvasProps {
  children?: React.ReactNode;
  frameCount?: number;
  basePath?: string;
}

export function MainCanvas({ 
  children,
  frameCount = 60, 
  basePath = '/assets/BarneyUIv2/backgrounds/varanasi-sequence/frame_' 
}: MainCanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [images, setImages] = useState<HTMLImageElement[]>([]);
  const { scrollYProgress } = useScroll();

  // Mouse position for parallax tilt
  const mouseX = useSpring(0, { stiffness: 50, damping: 20 });
  const mouseY = useSpring(0, { stiffness: 50, damping: 20 });

  // Map scroll to frame index
  const frameIndex = useTransform(scrollYProgress, [0, 1], [0, frameCount - 1]);

  // Map mouse movement to subtle 3D tilt for the WHOLE UI
  const rotateX = useTransform(mouseY, [-0.5, 0.5], [4, -4]); 
  const rotateY = useTransform(mouseX, [-0.5, 0.5], [-6, 6]);

  // Map mouse movement for the background (more exaggerated for parallax)
  const bgRotateX = useTransform(mouseY, [-0.5, 0.5], [6, -6]);
  const bgRotateY = useTransform(mouseX, [-0.5, 0.5], [-8, 8]);
  const bgScale = useTransform(scrollYProgress, [0, 1], [1.05, 1.15]);

  useEffect(() => {
    const loadedImages: HTMLImageElement[] = [];
    let loadedCount = 0;

    for (let i = 0; i < frameCount; i++) {
        const img = new Image();
        img.src = `${basePath}${i.toString().padStart(4, '0')}.jpg`;
        img.onload = () => {
          loadedCount++;
          if (loadedCount === frameCount) setImages(loadedImages);
        };
        img.onerror = () => loadedCount++;
        loadedImages[i] = img;
    }

    const handleMouseMove = (e: MouseEvent) => {
      mouseX.set((e.clientX / window.innerWidth) - 0.5);
      mouseY.set((e.clientY / window.innerHeight) - 0.5);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [frameCount, basePath, mouseX, mouseY]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || images.length === 0) return;

    const context = canvas.getContext('2d');
    if (!context) return;

    const render = () => {
      const index = Math.min(Math.floor(frameIndex.get()), frameCount - 1);
      const image = images[index];
      if (image && image.complete) {
        canvas.width = window.innerWidth * window.devicePixelRatio;
        canvas.height = window.innerHeight * window.devicePixelRatio;
        
        const scale = Math.max(canvas.width / image.width, canvas.height / image.height);
        const x = (canvas.width / 2) - (image.width / 2) * scale;
        const y = (canvas.height / 2) - (image.height / 2) * scale;
        
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(image, x, y, image.width * scale, image.height * scale);
      }
      requestAnimationFrame(render);
    };

    const animFrame = requestAnimationFrame(render);
    return () => cancelAnimationFrame(animFrame);
  }, [images, frameIndex, frameCount]);

  return (
    <CanvasWrapper>
      <StyledCanvas
        ref={canvasRef}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{
          rotateX: bgRotateX,
          rotateY: bgRotateY,
          scale: bgScale,
          transformPerspective: 1000,
        }}
      />
      <DepthOverlay />
      <Stage
        style={{
          rotateX,
          rotateY,
          transformPerspective: 1000,
        }}
        transition={{ type: 'spring', stiffness: 50, damping: 20 }}
      >
        {children}
      </Stage>
    </CanvasWrapper>
  );
}