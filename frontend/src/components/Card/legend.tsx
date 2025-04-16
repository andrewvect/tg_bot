import { Button, Popover, PopoverTrigger, PopoverContent, PopoverArrow, PopoverCloseButton, PopoverBody, Circle, Box, Text } from "@chakra-ui/react"
import Sentences from './sentences';
import { WordResponse } from '../../client/types.gen'

interface LegendProps {
	sentences: WordResponse[],
	header: string,
	alphabetSettings: number | null,
}

export const Legend = ({ sentences, header, alphabetSettings }: LegendProps) => {

	return (
		<Box>
			<Circle size="6" position="absolute" top="15vh" right="15vw">
				<Popover>
					<PopoverTrigger>
						<Button size="2xl" fontSize="2xl" colorScheme="white">?</Button>
					</PopoverTrigger>
					<PopoverContent
						bg="black"
						maxW="90vw"
						maxH="80vh"
						overflow="hidden"
						mr="5vw"
					>
						<PopoverArrow bg="black" />
						<PopoverCloseButton color="white" />
						<PopoverBody
							color="white"
							overflowY="auto"
							maxH="60vh"
						>
							<Text mb={2}>{header}</Text>
							{sentences && sentences.length > 0 && (
								<>
									<Sentences sentences={sentences[0]?.sentences ?? []} alphabetSettings={alphabetSettings} />
								</>
							)}
						</PopoverBody>
					</PopoverContent>
				</Popover>
			</Circle>
		</Box>
	)
}
