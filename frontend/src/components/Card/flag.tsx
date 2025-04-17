import { Circle, Box } from "@chakra-ui/react"

interface FlagProps {
  emoji: string;
}

export const Flag = ({ emoji }: FlagProps) => {
    return (
        <Box>
        <Circle size="6" top="15vh" left="15vw" position="absolute">
            <span style={{
                fontSize: '30px',
                display: 'inline-block',
                whiteSpace: 'nowrap',
                lineHeight: 1
            }}>{emoji}</span>
        </Circle>
        </Box>
    )
}
