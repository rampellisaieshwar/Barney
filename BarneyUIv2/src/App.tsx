import { styled } from './styles/theme';
import { globalStyles } from './styles/theme';
import { MainCanvas } from './components/MainCanvas';
import { ChatInterface } from './components/ChatInterface';
import { Sidebar } from './components/Sidebar';
import { ThemeProvider } from './styles/theme';

const AppContainer = styled('div', {
  width: '100%',
  height: '100%',
  display: 'flex',
});

const MainContent = styled('main', {
  flex: 1,
  marginLeft: '280px',
  height: '100vh',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
  zIndex: 10,
});

function App() {
  globalStyles();

  return (
    <ThemeProvider.Provider value={{}}>
      <AppContainer>
        <Sidebar />
        <MainContent>
          <MainCanvas>
            <ChatInterface />
          </MainCanvas>
        </MainContent>
      </AppContainer>
    </ThemeProvider.Provider>
  );
}

export default App;