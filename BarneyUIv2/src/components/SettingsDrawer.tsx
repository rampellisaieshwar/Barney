import { motion, AnimatePresence } from 'framer-motion';
import { styled } from '../styles/theme';

const DrawerOverlay = styled(motion.div, {
  position: 'fixed',
  inset: 0,
  background: 'rgba(0, 0, 0, 0.7)', // Slightly darker for better focus
  backdropFilter: 'blur(12px)',
  zIndex: 10000,
});

const DrawerContent = styled(motion.div, {
  position: 'fixed',
  left: '50%',
  top: '50%',
  width: '450px',
  maxHeight: '85vh',
  overflowY: 'auto',
  background: 'rgba(10, 9, 8, 0.4)',
  backdropFilter: 'blur(30px) saturate(150%)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  zIndex: 10001,
  padding: '$10 $8',
  borderRadius: '32px',
  display: 'flex',
  flexDirection: 'column',
  gap: '$8',
  boxShadow: '0 50px 100px rgba(0, 0, 0, 0.9)',
  transformStyle: 'preserve-3d',
  
  '&::-webkit-scrollbar': {
    width: '0px',
  },
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
            initial={{ opacity: 0, scale: 0.95, x: '-50%', y: '-48%' }}
            animate={{ opacity: 1, scale: 1, x: '-50%', y: '-50%' }}
            exit={{ opacity: 0, scale: 0.95, x: '-50%', y: '-48%' }}
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
