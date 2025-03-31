import { Card, CardBody, CardHeader, Text, Center, VStack } from "@chakra-ui/react"

interface CardComponentProps {
    header: string;
    children: React.ReactNode;
}

export function CardComponent({ header, children }: CardComponentProps) {
    return (
        <Card width="300px" backgroundColor="black" padding="4">
            <CardBody gap="2">
                <Center>
                    <VStack>
                        <CardHeader>
                            <Text
                                fontSize="7xl"
                                fontWeight="bold"
                                color="white"
                                isTruncated
                                noOfLines={1}
                                wordBreak="break-word"
                                textAlign="center"
                            >
                                {header}
                            </Text>
                        </CardHeader>
                        <Text textAlign="center">
                            {children}
                        </Text>
                    </VStack>
                </Center>
            </CardBody>
        </Card>
    )
}
