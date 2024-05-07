// theme.js
import { extendTheme, theme as baseTheme } from '@chakra-ui/react';

const config = {
  initialColorMode: 'dark',
  useSystemColorMode: false,
};

// Extend the base theme with your config
const theme = extendTheme({ config });

export default theme;
