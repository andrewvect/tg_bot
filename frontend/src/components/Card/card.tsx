import { Card, CardBody, CardHeader, Text, Center, VStack } from "@chakra-ui/react"

interface CardComponentProps {
    header: string;
    children: React.ReactNode;
}

export function CardComponent({ header, children }: CardComponentProps) {
    return (
        <Card width="300px" backgroundColor="black">
            <CardBody gap="2">
                <Center>
                    <VStack>
                        <CardHeader>
                            <Text fontSize="7xl" fontWeight="bold" color="white">{header}</Text>
                        </CardHeader>
                        {children}
                    </VStack>
                </Center>
            </CardBody>
        </Card>
    )
}
