import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '../styles/theme';
import { useState } from 'react';

const SettingsContainer = styled(motion.aside, {
  position: 'fixed',
  right: '$4',
  top: '$6',
  bottom: '$6',
  width: '420px',
  background: 'rgba(10, 9, 8, 0.4)',
  backdropFilter: 'blur(30px) saturate(150%)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '24px',
  display: 'flex',
  flexDirection: 'column',
  zIndex: 1000,
  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
  transformStyle: 'preserve-3d',
  overflow: 'hidden',

  '&::-webkit-scrollbar': {
    width: '0px',
  },
});

const HoverHandle = styled(motion.div, {
  position: 'fixed',
  right: 0,
  top: 0,
  bottom: 0,
  width: '24px',
  zIndex: 999,
});

const DrawerHeader = styled('div', {
  padding: '$8 $8',
  borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  transform: 'translateZ(15px)',
});

const Title = styled('h2', {
  fontFamily: '$display',
  fontSize: '$lg',
  fontWeight: 700,
  color: '$textPrimary',
  letterSpacing: '-0.04em',
  textTransform: 'uppercase',
});

const Description = styled('p', {
  fontSize: '10px',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.15em',
  color: '$amberWarm',
  opacity: 0.8,
  marginBottom: '$1',
});

const SettingGroup = styled('div', {
  padding: '$6 $8',
  display: 'flex',
  flexDirection: 'column',
  gap: '$6',
  flex: 1,
  overflowY: 'auto',
  '&::-webkit-scrollbar': {
    width: '0px',
  },
});

const GroupLabel = styled('label', {
  fontSize: '11px',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.1em',
  color: '$textMuted',
  marginBottom: '$1',
});

const SettingItem = styled('div', {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '$4 $5',
  borderRadius: '$xl',
  background: 'rgba(255, 255, 255, 0.03)',
  border: '1px solid rgba(255, 255, 255, 0.05)',
  transition: '$medium',

  '&:hover': {
    background: 'rgba(255, 255, 255, 0.06)',
    borderColor: '$amberWarm',
    transform: 'translateZ(5px)',
  },
});

const Control = styled('div', {
  display: 'flex',
  gap: '$2',
});

const Button = styled('button', {
  padding: '$2 $4',
  borderRadius: '$full',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  background: 'transparent',
  color: '$textPrimary',
  fontSize: '$xs',
  fontWeight: 600,
  cursor: 'pointer',
  transition: '$fast',

  '&:hover': {
    background: '$amberWarm',
    color: '$backgroundDeep',
    borderColor: '$amberWarm',
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

export function SettingsDrawer() {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <>
      <HoverHandle onMouseEnter={() => setIsExpanded(true)} />
      <SettingsContainer
        initial={{ width: '12px', opacity: 0.2, x: 10 }}
        animate={{ 
          width: isExpanded ? '400px' : '12px',
          opacity: 1,
          x: 0
        }}
        onMouseLeave={() => setIsExpanded(false)}
        transition={{ type: 'spring', stiffness: 200, damping: 25 }}
      >
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}
            >
              <DrawerHeader>
                <Description>Engine Configuration</Description>
                <Title>Varanasi Settings</Title>
              </DrawerHeader>

              <SettingGroup>
                <div>
                  <GroupLabel>Atmosphere</GroupLabel>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '$3', marginTop: '$2' }}>
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
                  </div>
                </div>

                <div style={{ marginTop: '$4' }}>
                  <GroupLabel>Intelligence</GroupLabel>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '$3', marginTop: '$2' }}>
                    <SettingItem>
                      <span>Reasoning Depth</span>
                      <Control>
                        <Button>Fast</Button>
                        <Button active>Deep</Button>
                      </Control>
                    </SettingItem>
                  </div>
                </div>
              </SettingGroup>

              <div style={{ padding: '$8', marginTop: 'auto' }}>
                <Button 
                  style={{ width: '100%', padding: '$4' }} 
                  onClick={() => setIsExpanded(false)}
                >
                  Apply & Synchronize
                </Button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {!isExpanded && (
          <motion.div
            style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <div style={{ width: '2px', height: '100px', background: 'rgba(212, 165, 116, 0.3)', borderRadius: '2px' }} />
          </motion.div>
        )}
      </SettingsContainer>
    </>
  );
}
