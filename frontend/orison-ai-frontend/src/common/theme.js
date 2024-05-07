// theme.js
import { extendTheme } from '@chakra-ui/react';

const config = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
};

const styles = {
  global: {
    // Styles for the `body`
    "html, body, #root": {
      height: "100%", // Ensures full viewport height
      width: "100%", // Ensures full viewport width
      margin: 0,
      padding: 0,
      overflow: "hidden" // Optional: Prevent scrolling
    }
  }
};

const theme = extendTheme({ config, styles });

export default theme;
