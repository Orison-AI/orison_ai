// App.jsx

// External
import React, { useState } from 'react';
import { 
  Button, useColorMode,
} from '@chakra-ui/react';

// Internal
import MainMenu from './pages/MainMenu';

const App = () => {
  const { colorMode, toggleColorMode } = useColorMode();
  const [isMenuOpen, setMenuOpen] = useState(false);

  const toggleMenu = () => {
    setMenuOpen(!isMenuOpen);
  };

  return (
    <div>
      <Button onClick={toggleMenu}>Toggle Menu</Button>
      <MainMenu isOpen={isMenuOpen} onClose={toggleMenu} />
      <Button onClick={toggleColorMode}>
        Color Mode: {colorMode === 'light' ? 'Light' : 'Dark'}
      </Button>
    </div>
  );
}

export default App;
