import { styled } from './styles/theme';
import { globalStyles } from './styles/theme';
import { MainCanvas } from './components/MainCanvas';
import { ChatInterface } from './components/ChatInterface';
import { Sidebar } from './components/Sidebar';
import { ThemeProvider } from './styles/theme';

const PerspectiveContainer = styled('div', {
  width: '100vw',
  height: '100vh',
  perspective: '2000px',
  overflow: 'hidden',
  background: '$backgroundDeep',
});

const AppContainer = styled('div', {
  width: '100%',
  height: '100%',
  display: 'flex',
  justifyContent: 'center',
  position: 'relative',
  transformStyle: 'preserve-3d',
});

const MainContent = styled('main', {
  width: '100%',
  maxWidth: '1200px',
  height: '100vh',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
  zIndex: 10,
  transformStyle: 'preserve-3d',
});

function App() {
  globalStyles();

  return (
    <ThemeProvider.Provider value={{}}>
      <PerspectiveContainer>
        <MainCanvas>
          <AppContainer>
            <Sidebar />
            <MainContent>
              <ChatInterface />
            </MainContent>
          </AppContainer>
        </MainCanvas>
      </PerspectiveContainer>
    </ThemeProvider.Provider>
  );
}

export default App;