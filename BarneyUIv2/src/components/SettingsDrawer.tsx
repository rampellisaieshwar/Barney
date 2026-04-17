import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '../styles/theme';

const DrawerOverlay = styled(motion.div, {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0, 0, 0, 0.4)',
  backdropFilter: 'blur(10px)',
  zIndex: 1000,
});

const DrawerContent = styled(motion.div, {
  position: 'fixed',
  right: 0,
  top: 0,
  bottom: 0,
  width: '400px',
  background: '$glassBackground',
  backdropFilter: 'blur(60px)',
  borderLeft: '1px solid $glassBorder',
  zIndex: 1001,
  padding: '$10 $8',
  display: 'flex',
  flexDirection: 'column',
  gap: '$8',
  boxShadow: '-10px 0 40px rgba(0,0,0,0.5)',
  transformStyle: 'preserve-3d',
});

const DrawerHeader = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  gap: '$2',
  marginBottom: '$4',
  transform: 'translateZ(20px)',
});

const Title = styled('h2', {
  fontFamily: '$display',
  fontSize: '$xl',
  fontWeight: 700,
  color: '$textPrimary',
  letterSpacing: '-0.04em',
});

const Description = styled('p', {
  fontSize: '$sm',
  color: '$textSecondary',
  opacity: 0.8,
});

const SettingGroup = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  gap: '$4',
});

const GroupLabel = styled('label', {
  fontSize: '$xs',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.1em',
  color: '$amberWarm',
});

const SettingItem = styled('div', {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '$4',
  borderRadius: '$xl',
  background: 'rgba(255, 255, 255, 0.03)',
  border: '1px solid $glassBorder',
  transition: '$medium',

  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
    borderColor: '$amberWarm',
  },
});

const Control = styled('div', {
  display: 'flex',
  gap: '$2',
});

const Button = styled('button', {
  padding: '$2 $4',
  borderRadius: '$full',
  border: '1px solid $glassBorder',
  background: 'transparent',
  color: '$textPrimary',
  fontSize: '$xs',
  fontWeight: 600,
  cursor: 'pointer',
  transition: '$fast',

  '&:hover': {
    background: '$amberWarm',
    color: '$backgroundDeep',
  },

  variants: {
    active: {
      true: {
        background: '$amberWarm',
        color: '$backgroundDeep',
        borderColor: '$amberWarm',
      },
    },
  },
});

interface SettingsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsDrawer({ isOpen, onClose }: SettingsDrawerProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <DrawerOverlay
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
          <DrawerContent
            initial={{ x: '100%', rotateY: 20, translateZ: 100 }}
            animate={{ x: 0, rotateY: 0, translateZ: 0 }}
            exit={{ x: '100%', rotateY: 20, translateZ: 100 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          >
            <DrawerHeader>
              <Description>Engine Configuration</Description>
              <Title>Varanasi Settings</Title>
            </DrawerHeader>

            <SettingGroup>
              <GroupLabel>Atmosphere</GroupLabel>
              <SettingItem>
                <span>Cinematic Bloom</span>
                <Control>
                  <Button active>On</Button>
                  <Button>Off</Button>
                </Control>
              </SettingItem>
              <SettingItem>
                <span>Rendering Quality</span>
                <Control>
                  <Button>4K</Button>
                  <Button active>HD</Button>
                </Control>
              </SettingItem>
            </SettingGroup>

            <SettingGroup>
              <GroupLabel>Intelligence</GroupLabel>
              <SettingItem>
                <span>Reasoning Depth</span>
                <Control>
                  <Button>Fast</Button>
                  <Button active>Deep</Button>
                </Control>
              </SettingItem>
            </SettingGroup>

            <div style={{ marginTop: 'auto' }}>
              <Button style={{ width: '100%', padding: '$4' }} onClick={onClose}>
                Confirm Configuration
              </Button>
            </div>
          </DrawerContent>
        </>
      )}
    </AnimatePresence>
  );
}
