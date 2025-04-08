import { Button, Popover, PopoverTrigger, PopoverContent, PopoverArrow, PopoverCloseButton, PopoverBody, Circle } from "@chakra-ui/react"

interface LegendProps {
	legend: string
}

export const Legend = ({ legend }: LegendProps) => {
	// If legend is null, do not show the element.
	if (legend === null) return null;
	return (
		<Circle size="6" position="absolute" top="-2" right="-2">
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
	)
}
