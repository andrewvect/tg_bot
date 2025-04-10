import { Button, Popover, PopoverTrigger, PopoverContent, PopoverArrow, PopoverCloseButton, PopoverBody, Circle, Box } from "@chakra-ui/react"

interface LegendProps {
	legend: string
}

export const Legend = ({ legend }: LegendProps) => {
	// If legend is null, do not show the element.
	if (legend === null) return null;
	return (
		<Box>
		<Circle size="6" position="absolute" top="15vh" right="15vw">
			<Popover>
				<PopoverTrigger>
					<Button size="2xl" fontSize="2xl" colorScheme="white">?</Button>
				</PopoverTrigger>
				<PopoverContent bg="black">
					<PopoverArrow bg="black" />
					<PopoverCloseButton color="white" />
					<PopoverBody color="white">{legend}</PopoverBody>
				</PopoverContent>
			</Popover>
		</Circle>
		</Box>
	)
}
