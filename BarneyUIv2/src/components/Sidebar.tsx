import { styled } from '../styles/theme';
import { motion } from 'framer-motion';
import { useState } from 'react';

const SidebarContainer = styled(motion.aside, {
  position: 'fixed',
  left: 0,
  top: 0,
  bottom: 0,
  width: '280px',
  background: '$glassBackground',
  backdropFilter: 'blur(30px)',
  borderRight: '1px solid $glassBorder',
  display: 'flex',
  flexDirection: 'column',
  zIndex: 100,
  transition: '$slow',
});

const SidebarHeader = styled('div', {
  padding: '$6',
  borderBottom: '1px solid $glassBorder',
});

const SidebarTitle = styled('h2', {
  fontFamily: '$display',
  fontSize: '$md',
  fontWeight: 600,
  color: '$textPrimary',
  letterSpacing: '-0.01em',
});

const SidebarNav = styled('nav', {
  flex: 1,
  padding: '$4',
  overflowY: 'auto',
});

const NavSection = styled('div', {
  marginBottom: '$6',
});

const NavSectionTitle = styled('h3', {
  fontSize: '$xs',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
  color: '$textMuted',
  padding: '$2 $3',
});

const NavItem = styled(motion.button, {
  width: '100%',
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
  padding: '$3 $4',
  borderRadius: '$lg',
  border: 'none',
  background: 'transparent',
  color: '$textSecondary',
  fontFamily: '$body',
  fontSize: '$sm',
  textAlign: 'left',
  cursor: 'pointer',
  transition: '$fast',

  '&:hover': {
    background: '$glassHighlight',
    color: '$textPrimary',
  },

  variants: {
    active: {
      true: {
        background: 'rgba(212, 165, 116, 0.1)',
        color: '$amberWarm',
        borderLeft: '2px solid $amberWarm',
      },
    },
  },
});

const HistoryItem = styled(motion.button, {
  width: '100%',
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
  padding: '$3 $4',
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
    background: '$glassHighlight',
    color: '$textSecondary',
  },

  '& p': {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
});

const AgentStatus = styled('div', {
  padding: '$4 $6',
  borderTop: '1px solid $glassBorder',
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
});

const StatusDot = styled('div', {
  width: '8px',
  height: '8px',
  borderRadius: '$full',
  background: '$success',
  boxShadow: '0 0 8px $success',
});

export function Sidebar() {
  const [activeNav, setActiveNav] = useState('chat');

  return (
    <SidebarContainer
      initial={{ x: -280 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
    >
      <SidebarHeader>
        <SidebarTitle>Barney</SidebarTitle>
      </SidebarHeader>

      <SidebarNav>
        <NavSection>
          <NavSectionTitle>Navigate</NavSectionTitle>
          <NavItem
            active={activeNav === 'chat'}
            onClick={() => setActiveNav('chat')}
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M2 4h12v8H10l-4 4V4z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
            </svg>
            Chat
          </NavItem>
          <NavItem
            active={activeNav === 'agents'}
            onClick={() => setActiveNav('agents')}
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.5" />
              <path d="M2 14c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            Agents
          </NavItem>
          <NavItem
            active={activeNav === 'memory'}
            onClick={() => setActiveNav('memory')}
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2L2 5v6l6 3 6-3V5L8 2z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
              <path d="M8 2v10M2 5l6 3M14 5l-6 3" stroke="currentColor" strokeWidth="1.5" />
            </svg>
            Memory
          </NavItem>
          <NavItem
            active={activeNav === 'governance'}
            onClick={() => setActiveNav('governance')}
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 1l2 4h4l-3 3 1 5-4-2-4 2 1-5-3-3h4l2-4z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
            </svg>
            Governance
          </NavItem>
        </NavSection>

        <NavSection>
          <NavSectionTitle>History</NavSectionTitle>
          <HistoryItem
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <p>Research into quantum computing applications...</p>
          </HistoryItem>
          <HistoryItem
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <p>Compare machine learning frameworks...</p>
          </HistoryItem>
          <HistoryItem
            whileHover={{ x: 4 }}
            whileTap={{ scale: 0.98 }}
          >
            <p>Analyze blockchain consensus mechanisms...</p>
          </HistoryItem>
        </NavSection>
      </SidebarNav>

      <AgentStatus>
        <StatusDot />
        <span style={{ fontSize: '12px', color: '#a89f8f' }}>Agent Active</span>
      </AgentStatus>
    </SidebarContainer>
  );
}