import { styled } from '../styles/theme';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useRef, useEffect } from 'react';
import type { Message, PlanStep } from '../types';
import { sendMessage, createMessage } from '../services/api';
import { SettingsDrawer } from './SettingsDrawer';

const ChatWrapper = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  width: '100%',
  maxWidth: '860px',
  margin: '0 auto',
  padding: '$6',
  position: 'relative',
  zIndex: 10,
  transformStyle: 'preserve-3d',
});

const ChatHeader = styled('header', {
  display: 'flex',
  alignItems: 'center',
  gap: '$4',
  padding: '$6 0',
  marginBottom: '$4',
  borderBottom: '1px solid $glassBorder',
  transform: 'translateZ(20px)',
});

const LogoMark = styled('div', {
  width: '42px',
  height: '42px',
  borderRadius: '$lg',
  background: 'linear-gradient(135deg, $amberWarm, $amberFire)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontFamily: '$display',
  fontWeight: 700,
  fontSize: '$lg',
  color: '$backgroundDeep',
  boxShadow: '0 0 20px $copperGlow',
});

const HeaderText = styled('div', {
  '& h1': {
    fontFamily: '$display',
    fontSize: '$xl',
    fontWeight: 600,
    color: '$textPrimary',
    letterSpacing: '-0.03em',
  },
  '& p': {
    fontSize: '$sm',
    color: '$textSecondary',
    fontStyle: 'italic',
    opacity: 0.8,
  },
});

const MessagesContainer = styled('div', {
  flex: 1,
  overflowY: 'auto',
  overflowX: 'hidden',
  padding: '$8 0',
  transformStyle: 'preserve-3d',
  maskImage: 'linear-gradient(to bottom, transparent, black 5%, black 95%, transparent)',
  '&::-webkit-scrollbar': {
    width: '0px',
  },
});

const MessageGroup = styled(motion.div, {
  display: 'flex',
  flexDirection: 'column',
  gap: '$4',
  marginBottom: '$8',
  transformStyle: 'preserve-3d',
});

const MessageBubble = styled(motion.div, {
  maxWidth: '80%',
  padding: '$5 $6',
  borderRadius: '$xl',
  position: 'relative',
  backdropFilter: 'blur(40px)',
  transformStyle: 'preserve-3d',
  boxShadow: '$deep',

  variants: {
    role: {
      user: {
        background: 'linear-gradient(135deg, rgba(212, 165, 116, 0.15), rgba(184, 115, 51, 0.1))',
        border: '1px solid $glassBorder',
        borderRight: '2px solid $amberWarm',
        marginLeft: 'auto',
      },
      assistant: {
        background: '$glassBackground',
        border: '1px solid $glassBorder',
        borderLeft: '2px solid $copper',
      },
    },
  },
});

const MessageContent = styled('p', {
  fontSize: '1.05rem',
  lineHeight: 1.8,
  color: '$textPrimary',
  whiteSpace: 'pre-wrap',
  fontWeight: 400,
});

const MessageMeta = styled('span', {
  fontSize: '$xs',
  color: '$textMuted',
  marginTop: '$3',
  display: 'block',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
});

const StepsContainer = styled(motion.div, {
  marginTop: '$4',
  display: 'flex',
  flexDirection: 'column',
  gap: '$3',
  transformStyle: 'preserve-3d',
});

const StepCard = styled(motion.div, {
  display: 'flex',
  alignItems: 'flex-start',
  gap: '$4',
  padding: '$4 $5',
  borderRadius: '$lg',
  background: 'rgba(15, 13, 11, 0.5)',
  border: '1px solid $glassBorder',
  backdropFilter: 'blur(20px)',
  transition: '$slow',
  boxShadow: '0 4px 20px rgba(0,0,0,0.3)',

  variants: {
    status: {
      pending: {},
      running: {
        borderColor: '$running',
        boxShadow: '0 0 30px rgba(56, 189, 248, 0.15)',
        background: 'rgba(56, 189, 248, 0.05)',
      },
      completed: {
        borderColor: '$success',
        opacity: 0.8,
      },
      failed: {
        borderColor: '$error',
        opacity: 0.8,
      },
      blocked: {
        borderColor: '$warning',
      },
      rejected: {
        borderColor: '$error',
        opacity: 0.8,
      },
    },
  },
});

const StepIndicator = styled('div', {
  width: '20px',
  height: '20px',
  borderRadius: '$full',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
  marginTop: '$1',

  variants: {
    status: {
      pending: { background: '$textMuted', opacity: 0.5 },
      running: { background: '$running', boxShadow: '0 0 10px $running' },
      completed: { background: '$success' },
      failed: { background: '$error' },
      blocked: { background: '$warning' },
      rejected: { background: '$error' },
    },
  },
});

const StepContent = styled('div', {
  flex: 1,
  minWidth: 0,
  '& h4': {
    fontSize: '$sm',
    fontWeight: 600,
    color: '$textPrimary',
    marginBottom: '$1',
  },
  '& p': {
    fontSize: '$xs',
    color: '$textSecondary',
    lineHeight: 1.6,
  },
});

const StageTag = styled('span', {
  fontSize: '9px',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.1em',
  padding: '3px 8px',
  borderRadius: '$sm',
  background: 'rgba(212, 165, 116, 0.1)',
  color: '$amberWarm',
  border: '1px solid $glassBorder',
  alignSelf: 'flex-start',
});

const InputArea = styled('div', {
  padding: '$6 0',
  position: 'relative',
  zIndex: 20,
});

const InputWrapper = styled('div', {
  display: 'flex',
  gap: '$4',
  alignItems: 'flex-end',
  padding: '$4',
  borderRadius: '$2xl',
  background: '$glassBackground',
  border: '1px solid $glassBorder',
  backdropFilter: 'blur(50px)',
  transition: '$slow',
  boxShadow: '$deep',

  '&:focus-within': {
    borderColor: '$amberWarm',
    boxShadow: '$glow',
    transform: 'translateY(-2px) translateZ(10px)',
  },
});

const Input = styled('textarea', {
  flex: 1,
  background: 'transparent',
  border: 'none',
  outline: 'none',
  color: '$textPrimary',
  fontFamily: '$body',
  fontSize: '1.05rem',
  lineHeight: 1.6,
  resize: 'none',
  maxHeight: '200px',
  overflowY: 'auto',

  '&::placeholder': {
    color: '$textMuted',
  },
});

const SendButton = styled(motion.button, {
  width: '48px',
  height: '48px',
  borderRadius: '$xl',
  border: 'none',
  background: 'linear-gradient(135deg, $amberWarm, $copper)',
  color: '$backgroundDeep',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  flexShrink: 0,
  boxShadow: '0 4px 15px rgba(184, 115, 51, 0.3)',

  '&:disabled': {
    opacity: 0.3,
    filter: 'grayscale(1)',
    cursor: 'not-allowed',
  },
});

const ThinkingIndicator = styled(motion.div, {
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
  padding: '$4 $2',
  color: '$textSecondary',
  fontSize: '$sm',
  fontWeight: 500,
});

const SettingsButton = styled(motion.button, {
  marginLeft: 'auto',
  padding: '$2',
  borderRadius: '$full',
  border: '1px solid $glassBorder',
  background: 'transparent',
  color: '$textMuted',
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: '$fast',

  '&:hover': {
    color: '$amberWarm',
    borderColor: '$amberWarm',
    background: 'rgba(212, 165, 116, 0.05)',
  },
});

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [steps, setSteps] = useState<PlanStep[]>([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, steps]);

  const handleSubmit = async () => {
    if (!input.trim() || isProcessing) return;

    const userMessage = createMessage(input.trim(), 'user');
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);
    setSteps([]);

    try {
      await sendMessage([...messages, userMessage], (step, isNew) => {
        setSteps((prev) => {
          if (isNew) {
            return [...prev, step];
          }
          return prev.map((s) => (s.id === step.id ? step : s));
        });
      });
    } catch (error) {
      console.error('Task failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <ChatWrapper>
      <ChatHeader>
        <LogoMark>V</LogoMark>
        <HeaderText>
          <h1>Varanasi</h1>
          <p>Cinematic Intelligence Engine</p>
        </HeaderText>
        <SettingsButton
          onClick={() => setIsSettingsOpen(true)}
          whileHover={{ rotate: 90 }}
          whileTap={{ scale: 0.9 }}
        >
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 13C11.6569 13 13 11.6569 13 10C13 8.34315 11.6569 7 10 7C8.34315 7 7 8.34315 7 10C7 11.6569 8.34315 13 10 13Z" stroke="currentColor" strokeWidth="1.5" />
            <path d="M10 2V4M10 16V18M18 10H16M4 10H2M15.65 4.35L14.24 5.76M5.76 14.24L4.35 15.65M15.65 15.65L14.24 14.24M5.76 5.76L4.35 4.35" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </SettingsButton>
      </ChatHeader>

      <MessagesContainer>
        <AnimatePresence mode="popLayout">
          {messages.map((msg) => (
            <MessageGroup
              key={msg.id}
              initial={{ opacity: 0, y: 30, rotateX: 15, translateZ: -100 }}
              animate={{ opacity: 1, y: 0, rotateX: 0, translateZ: 0 }}
              exit={{ opacity: 0, scale: 0.9, rotateX: -10 }}
              transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            >
              <MessageBubble role={msg.role}>
                <MessageContent>{msg.content}</MessageContent>
                <MessageMeta>
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </MessageMeta>
              </MessageBubble>
            </MessageGroup>
          ))}
        </AnimatePresence>

        {steps.length > 0 && (
          <StepsContainer
            initial={{ opacity: 0, y: 40, rotateX: 10 }}
            animate={{ opacity: 1, y: 0, rotateX: 0 }}
            transition={{ duration: 0.6 }}
          >
            {steps.map((step, idx) => (
              <StepCard
                key={step.id}
                status={step.status}
                initial={{ opacity: 0, x: -30, rotateY: -10, translateZ: -50 }}
                animate={{ opacity: 1, x: 0, rotateY: 0, translateZ: 0 }}
                transition={{ duration: 0.5, delay: idx * 0.1, ease: [0.16, 1, 0.3, 1] }}
              >
                <StepIndicator status={step.status}>
                  {step.status === 'completed' && (
                    <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                      <path d="M2 6L5 9L10 3" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                    </svg>
                  )}
                </StepIndicator>
                <StepContent>
                  <h4>{step.title}</h4>
                  <p>{step.description}</p>
                </StepContent>
                <StageTag>{step.stage}</StageTag>
              </StepCard>
            ))}
          </StepsContainer>
        )}

        {isProcessing && (
          <ThinkingIndicator
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <motion.span
              animate={{ opacity: [0.4, 1, 0.4] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              Orchestrating Cinematic Sequence...
            </motion.span>
          </ThinkingIndicator>
        )}

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputArea>
        <InputWrapper
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4, duration: 0.8 }}
        >
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Command the Varanasi Engine..."
            rows={1}
          />
          <SendButton
            onClick={handleSubmit}
            disabled={!input.trim() || isProcessing}
            whileHover={{ scale: 1.05, boxShadow: '0 0 20px $amberWarm' }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="22" height="22" viewBox="0 0 20 20" fill="none">
              <path d="M3 10L17 3L10 17L11.5 10L3 10Z" fill="currentColor" />
            </svg>
          </SendButton>
        </InputWrapper>
      </InputArea>
      
      <SettingsDrawer isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </ChatWrapper>
  );
}