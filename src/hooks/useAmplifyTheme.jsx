import { useEffect, useState } from 'react';

const useAmplifyTheme = () => {
  const [amplifyTheme, setAmplifyTheme] = useState({});

  useEffect(() => {
    // Custom theme for Amplify UI components
    setAmplifyTheme({
      name: 'sportsbook-theme',
      tokens: {
        colors: {
          background: {
            primary: '#060C1F',
            secondary: '#141C33',
          },
          font: {
            interactive: '#FFFFFF',
            primary: '#FFFFFF',
            secondary: '#8A92AB',
          },
          brand: {
            primary: {
              10: '#09ff8d',
              20: '#09ff8d',
              40: '#09ff8d',
              60: '#09ff8d',
              80: '#09ff8d',
              90: '#09ff8d',
              100: '#09ff8d',
            },
          },
        },
        components: {
          button: {
            primary: {
              backgroundColor: '#F3486A',
              _hover: {
                backgroundColor: '#FF6600',
              },
            },
          },
          card: {
            backgroundColor: '#141C33',
          },
          heading: {
            color: '#FFFFFF',
          },
          text: {
            color: '#FFFFFF',
          },
        },
      },
    });
  }, []);

  return amplifyTheme;
};

export default useAmplifyTheme;
