import { extendTheme } from "@chakra-ui/react"

const theme = extendTheme({
  colors: {
    ui: {
      main: "#000000", // black background
      secondary: "#EDF2F7",
      success: "#48BB78",
      danger: "#E53E3E",
      light: "#ffffff", // white text
      dark: "#1A202C",
      darkSlate: "#252D3D",
      dim: "#A0AEC0",
    },
  },
  components: {
    Button: {
      variants: {
        primary: {
          backgroundColor: "ui.main",
          color: "ui.light",
          fontWeight: "bold", // makes text bold
          fontSize: "2xl", // increases text size (you can also use values like "20px", etc.)
          _hover: {
            backgroundColor: "#000000", // keep black on hover
          },
          _disabled: {
            backgroundColor: "ui.main",
            color: "ui.light",
          },
        },
        danger: {
          backgroundColor: "ui.main",
          color: "ui.light",
          fontWeight: "bold",
          fontSize: "lg",
          _hover: {
            backgroundColor: "#000000",
          },
        },
      },
    },
    Tabs: {
      variants: {
        enclosed: {
          tab: {
            _selected: {
              color: "ui.main",
            },
          },
        },
      },
    },
  },
})

export default theme
