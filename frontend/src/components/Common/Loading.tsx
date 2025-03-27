
import { Spinner, AbsoluteCenter } from "@chakra-ui/react"
import BackgroundBox from "../back"
import { CardComponent } from "../Card/card"

export default function Loading() {
	return (
		<BackgroundBox>
			<AbsoluteCenter>
				<CardComponent header="Loading...">
					<Spinner size="xl" color="white" />
				</CardComponent>
			</AbsoluteCenter>
		</BackgroundBox>
	)
}
