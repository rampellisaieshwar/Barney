import { styled } from '../styles/theme';
import { motion, AnimatePresence } from 'framer-motion';
import { useState } from 'react';

const SidebarContainer = styled(motion.aside, {
  position: 'fixed',
  left: '$4',
  top: '$6',
  bottom: '$6',
  background: 'rgba(10, 9, 8, 0.4)', // Precise requested glassmorphism
  backdropFilter: 'blur(25px) saturate(150%)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '24px',
  display: 'flex',
  flexDirection: 'column',
  zIndex: 1000,
  boxShadow: '0 20px 40px rgba(0, 0, 0, 0.4)',
  transformStyle: 'preserve-3d',
  overflow: 'hidden',
});

const HoverHandle = styled(motion.div, {
  position: 'fixed',
  left: 0,
  top: 0,
  bottom: 0,
  width: '24px',
  zIndex: 999,
});

const SidebarHeader = styled('div', {
  padding: '$8 $6',
  borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
  transform: 'translateZ(10px)',
});

const SidebarTitle = styled('h2', {
  fontFamily: '$display',
  fontSize: '1.2rem',
  fontWeight: 700,
  color: '$textPrimary',
  letterSpacing: '-0.04em',
  textTransform: 'uppercase',
});

const SidebarNav = styled('nav', {
  flex: 1,
  padding: '$6 $4',
  overflowY: 'auto',
  '&::-webkit-scrollbar': {
    width: '0px',
  },
});

const NavSection = styled('div', {
  marginBottom: '$8',
});

const NavSectionTitle = styled('h3', {
  fontSize: '10px',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.15em',
  color: '$textMuted',
  padding: '$2 $4',
  marginBottom: '$2',
});

const NavItem = styled(motion.button, {
  width: '100%',
  display: 'flex',
  alignItems: 'center',
  gap: '$4',
  padding: '$4 $5',
  borderRadius: '$xl',
  border: 'none',
  background: 'transparent',
  color: '$textSecondary',
  fontFamily: '$body',
  fontSize: '$sm',
  fontWeight: 500,
  textAlign: 'left',
  cursor: 'pointer',
  transition: '$medium',

  '&:hover': {
    background: 'rgba(255, 255, 255, 0.05)',
    color: '$textPrimary',
    transform: 'translateZ(5px)',
  },

  variants: {
    active: {
      true: {
        background: 'rgba(212, 165, 116, 0.08)',
        color: '$amberWarm',
        borderLeft: '3px solid $amberWarm',
      },
    },
  },
});

const HistoryItem = styled(motion.button, {
  width: '100%',
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
  padding: '$3 $5',
  borderRadius: '$lg',
  border: 'none',
  background: 'transparent',
  color: '$textMuted',
  fontFamily: '$body',
  fontSize: '$xs',
  textAlign: 'left',
  cursor: 'pointer',
  transition: '$fast',
  maxWidth: '100%',
  overflow: 'hidden',

  '&:hover': {
    color: '$textSecondary',
  },

  '& p': {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    opacity: 0.7,
  },
});

const AgentStatus = styled('div', {
  padding: '$6 0',
  margin: '0 $6',
  borderTop: '1px solid rgba(255, 255, 255, 0.05)',
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
});

const StatusDot = styled('div', {
  width: '10px',
  height: '10px',
  borderRadius: '$full',
  background: '#B87333',
  boxShadow: '0 0 12px #B87333',
  animation: 'pulseStatus 2s infinite',

  '@keyframes pulseStatus': {
    '0%, 100%': { opacity: 1, transform: 'scale(1)' },
    '50%': { opacity: 0.6, transform: 'scale(0.8)' },
  },
});

export function Sidebar() {
  const [activeNav, setActiveNav] = useState('chat');
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <>
      <HoverHandle onMouseEnter={() => setIsExpanded(true)} />
      <SidebarContainer
        initial={{ width: '12px', opacity: 0.2, x: -10 }}
        animate={{ 
          width: isExpanded ? '260px' : '12px',
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
              <SidebarHeader>
                <SidebarTitle>Varanasi</SidebarTitle>
              </SidebarHeader>

              <SidebarNav>
                <NavSection>
                  <NavSectionTitle>Command</NavSectionTitle>
                  <NavItem
                    active={activeNav === 'chat'}
                    onClick={() => setActiveNav('chat')}
                    whileHover={{ x: 6 }}
                    whileTap={{ scale: 0.96 }}
                  >
                    <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
                      <path d="M2 4h12v8H10l-4 4V4z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
                    </svg>
                    Cinema
                  </NavItem>
                  <NavItem
                    active={activeNav === 'agents'}
                    onClick={() => setActiveNav('agents')}
                    whileHover={{ x: 6 }}
                    whileTap={{ scale: 0.96 }}
                  >
                    <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
                      <circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.8" />
                      <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                    </svg>
                    Cognition
                  </NavItem>
                  <NavItem
                    active={activeNav === 'memory'}
                    onClick={() => setActiveNav('memory')}
                    whileHover={{ x: 6 }}
                    whileTap={{ scale: 0.96 }}
                  >
                    <svg width="18" height="18" viewBox="0 0 16 16" fill="none">
                      <path d="M8 2L2 5v6l6 3 6-3V5L8 2z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
                      <path d="M8 2v10M2 5l6 3M14 5l-6 3" stroke="currentColor" strokeWidth="1.8" />
                    </svg>
                    Vault
                  </NavItem>
                </NavSection>

                <NavSection>
                  <NavSectionTitle>Reels</NavSectionTitle>
                  <HistoryItem whileHover={{ x: 6 }}>
                    <p>Quantum Synthesis Phase II</p>
                  </HistoryItem>
                  <HistoryItem whileHover={{ x: 6 }}>
                    <p>Neural Pattern Audit</p>
                  </HistoryItem>
                </NavSection>
              </SidebarNav>

              <AgentStatus>
                <StatusDot />
                <span style={{ fontSize: '11px', fontWeight: 600, color: '#D4A574', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                  Engine Live
                </span>
              </AgentStatus>
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
      </SidebarContainer>
    </>
  );
}