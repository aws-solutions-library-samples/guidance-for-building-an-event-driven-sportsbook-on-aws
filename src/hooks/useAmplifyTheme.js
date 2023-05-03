import { useTheme as useMuiTheme } from "@mui/material";

export const useAmplifyTheme = () => {
  const { palette } = useMuiTheme();

  return {
    name: "Auth Theme",
    tokens: {
      colors: {
        border: {
          error: {
            value: palette.error.main,
          },
        },
        brand: {
          primary: {
            80: { value: palette.primary.dark },
            90: { value: palette.primary.main },
            100: { value: palette.primary.dark },
          },
        },
      },
      components: {
        passwordfield: {
          button: {
            color: {
              value: palette.primary.main,
            },
            _active: {
              backgroundColor: palette.primary.light,
              color: palette.primary.dark,
            },
            _focus: {
              backgroundColor: palette.primary.light,
              color: palette.primary.dark,
            },
            _hover: {
              backgroundColor: palette.primary.light,
              color: palette.primary.dark,
            },
          },
        },
        button: {
          link: {
            _active: {
              backgroundColor: { value: "transparent" },
              borderColor: { value: "transparent" },
              color: { value: palette.primary.dark },
            },
            _focus: {
              backgroundColor: { value: "transparent" },
              borderColor: { value: "transparent" },
              boxShadow: { value: "none" },
              color: { value: palette.primary.dark },
            },
            _hover: {
              backgroundColor: { value: "transparent" },
              borderColor: { value: "transparent" },
              color: { value: palette.primary.light },
            },
          },
        },
      },
    },
  };
};

export default useAmplifyTheme;
