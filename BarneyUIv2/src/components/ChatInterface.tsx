import { styled } from '../styles/theme';
import { motion, AnimatePresence } from 'framer-motion';
import { useState, useRef, useEffect } from 'react';
import type { Message, PlanStep } from '../types';
import { sendMessage, createMessage } from '../services/api';

const ChatWrapper = styled('div', {
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  maxWidth: '900px',
  margin: '0 auto',
  padding: '$4',
  position: 'relative',
  zIndex: 10,
});

const ChatHeader = styled('header', {
  display: 'flex',
  alignItems: 'center',
  gap: '$3',
  padding: '$4 0',
  marginBottom: '$4',
  borderBottom: '1px solid $glassBorder',
});

const LogoMark = styled('div', {
  width: '40px',
  height: '40px',
  borderRadius: '$lg',
  background: 'linear-gradient(135deg, $amberWarm, $copper)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontFamily: '$display',
  fontWeight: 700,
  fontSize: '$lg',
  color: '$backgroundDeep',
});

const HeaderText = styled('div', {
  '& h1': {
    fontFamily: '$display',
    fontSize: '$xl',
    fontWeight: 600,
    color: '$textPrimary',
    letterSpacing: '-0.02em',
  },
  '& p': {
    fontSize: '$sm',
    color: '$textMuted',
  },
});

const MessagesContainer = styled('div', {
  flex: 1,
  overflowY: 'auto',
  overflowX: 'hidden',
  padding: '$4 0',
  perspective: '1000px',
});

const MessageGroup = styled(motion.div, {
  display: 'flex',
  flexDirection: 'column',
  gap: '$4',
  marginBottom: '$6',
});

const MessageBubble = styled(motion.div, {
  maxWidth: '85%',
  padding: '$4 $5',
  borderRadius: '$xl',
  position: 'relative',
  transformOrigin: 'left center',

  variants: {
    role: {
      user: {
        background: 'linear-gradient(135deg, rgba(212, 165, 116, 0.2), rgba(184, 115, 51, 0.15))',
        border: '1px solid $glassBorder',
        marginLeft: 'auto',
        backdropFilter: 'blur(20px)',
      },
      assistant: {
        background: '$glassBackground',
        border: '1px solid $glassBorder',
        backdropFilter: 'blur(20px)',
        boxShadow: '$layer',
      },
    },
  },
});

const MessageContent = styled('p', {
  fontSize: '$md',
  lineHeight: 1.7,
  color: '$textPrimary',
  whiteSpace: 'pre-wrap',
});

const MessageMeta = styled('span', {
  fontSize: '$xs',
  color: '$textMuted',
  marginTop: '$2',
  display: 'block',
});

const StepsContainer = styled(motion.div, {
  marginTop: '$4',
  display: 'flex',
  flexDirection: 'column',
  gap: '$2',
});

const StepCard = styled(motion.div, {
  display: 'flex',
  alignItems: 'flex-start',
  gap: '$3',
  padding: '$3 $4',
  borderRadius: '$lg',
  background: 'rgba(26, 22, 18, 0.6)',
  border: '1px solid $glassBorder',
  backdropFilter: 'blur(10px)',
  transition: '$medium',

  variants: {
    status: {
      pending: {},
      running: {
        borderColor: '$running',
        boxShadow: '0 0 20px rgba(56, 189, 248, 0.1)',
      },
      completed: {
        borderColor: '$success',
        opacity: 0.7,
      },
      failed: {
        borderColor: '$error',
        opacity: 0.7,
      },
      blocked: {
        borderColor: '$warning',
      },
      rejected: {
        borderColor: '$error',
        opacity: 0.7,
      },
    },
  },
});

const StepIndicator = styled('div', {
  width: '24px',
  height: '24px',
  borderRadius: '$full',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,

  variants: {
    status: {
      pending: { background: '$textMuted' },
      running: { background: '$running', animation: 'pulse 1.5s ease-in-out infinite' },
      completed: { background: '$success' },
      failed: { background: '$error' },
      blocked: { background: '$warning' },
    },
  },

  '@keyframes pulse': {
    '0%, 100%': { opacity: 1, boxShadow: '0 0 0 0 rgba(56, 189, 248, 0.4)' },
    '50%': { opacity: 0.8, boxShadow: '0 0 0 8px rgba(56, 189, 248, 0)' },
  },
});

const StepContent = styled('div', {
  flex: 1,
  minWidth: 0,
  '& h4': {
    fontSize: '$sm',
    fontWeight: 500,
    color: '$textPrimary',
    marginBottom: '$1',
  },
  '& p': {
    fontSize: '$xs',
    color: '$textSecondary',
    lineHeight: 1.5,
  },
});

const StageTag = styled('span', {
  fontSize: '10px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  padding: '2px 6px',
  borderRadius: '$sm',
  background: '$glassBackground',
  color: '$amberWarm',
  border: '1px solid $glassBorder',
});

const InputArea = styled('div', {
  padding: '$4 0',
  borderTop: '1px solid $glassBorder',
});

const InputWrapper = styled('div', {
  display: 'flex',
  gap: '$3',
  alignItems: 'flex-end',
  padding: '$3',
  borderRadius: '$xl',
  background: '$glassBackground',
  border: '1px solid $glassBorder',
  backdropFilter: 'blur(20px)',
  transition: '$medium',

  '&:focus-within': {
    borderColor: '$amberWarm',
    boxShadow: '$glow',
  },
});

const Input = styled('textarea', {
  flex: 1,
  background: 'transparent',
  border: 'none',
  outline: 'none',
  color: '$textPrimary',
  fontFamily: '$body',
  fontSize: '$md',
  lineHeight: 1.5,
  resize: 'none',
  maxHeight: '150px',
  overflowY: 'auto',

  '&::placeholder': {
    color: '$textMuted',
  },
});

const SendButton = styled(motion.button', {
  width: '44px',
  height: '44px',
  borderRadius: '$lg',
  border: 'none',
  background: 'linear-gradient(135deg, $amberWarm, $copper)',
  color: '$backgroundDeep',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
  flexShrink: 0,

  '&:disabled': {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
});

const ThinkingIndicator = styled(motion.div, {
  display: 'flex',
  alignItems: 'center',
  gap: '$2',
  padding: '$3 $4',
  color: '$textMuted',
  fontSize: '$sm',

  '& span': {
    display: 'flex',
    gap: '4px',
  },

  '& span b': {
    width: '6px',
    height: '6px',
    borderRadius: '$full',
    background: '$running',
  },
});

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [steps, setSteps] = useState<PlanStep[]>([]);
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
        <LogoMark>B</LogoMark>
        <HeaderText>
          <h1>Barney</h1>
          <p>Autonomous Research Agent</p>
        </HeaderText>
      </ChatHeader>

      <MessagesContainer>
        <AnimatePresence mode="popLayout">
          {messages.map((msg) => (
            <MessageGroup
              key={msg.id}
              initial={{ opacity: 0, y: 20, rotateX: -10 }}
              animate={{ opacity: 1, y: 0, rotateX: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
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
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          >
            {steps.map((step, idx) => (
              <StepCard
                key={step.id}
                status={step.status}
                initial={{ opacity: 0, x: -20, rotateY: -5 }}
                animate={{ opacity: 1, x: 0, rotateY: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.05, ease: [0.16, 1, 0.3, 1] }}
              >
                <StepIndicator status={step.status}>
                  {step.status === 'completed' && (
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path d="M2 6L5 9L10 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
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
            <span>
              <b style={{ animationDelay: '0ms' }} />
              <b style={{ animationDelay: '150ms' }} />
              <b style={{ animationDelay: '300ms' }} />
            </span>
            Processing...
          </ThinkingIndicator>
        )}

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputArea>
        <InputWrapper>
          <Input
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="What would you like to research?"
            rows={1}
          />
          <SendButton
            onClick={handleSubmit}
            disabled={!input.trim() || isProcessing}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 10L17 3L10 17L11.5 10L3 10Z" fill="currentColor" />
            </svg>
          </SendButton>
        </InputWrapper>
      </InputArea>
    </ChatWrapper>
  );
}