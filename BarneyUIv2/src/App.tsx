import { styled, globalStyles, ThemeProvider } from './styles/theme';
import { MainCanvas } from './components/MainCanvas';
import { ChatInterface } from './components/ChatInterface';
import { Sidebar } from './components/Sidebar';
import { SettingsDrawer } from './components/SettingsDrawer';

const PerspectiveContainer = styled('div', {
  width: '100vw',
  height: '100vh',
  perspective: '2000px',
  overflow: 'hidden',
  background: '$backgroundDeep',
  position: 'fixed',
  inset: 0,
});

const AppContainer = styled('div', {
  width: '100vw',
  height: '100vh',
  display: 'flex',
  justifyContent: 'center',
  position: 'relative',
  transformStyle: 'preserve-3d',
});

const MainContent = styled('main', {
  width: '100%',
  maxWidth: '900px', // Adjusted to 900px as per cinematic requirements
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
            <SettingsDrawer />
          </AppContainer>
        </MainCanvas>
      </PerspectiveContainer>
    </ThemeProvider.Provider>
  );
}

export default App;