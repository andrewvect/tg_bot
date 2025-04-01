import { Card, CardBody, CardHeader, Text, Center, VStack } from "@chakra-ui/react";

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
                        <CardHeader width={"100%"}>
                            <Text
                                fontSize={["6xl", "7xl"]} // Reduce font size
                                fontWeight="bold"
                                color="white"
                                isTruncated={false} // Disable truncation
                                whiteSpace="normal" // Allow text to wrap to the next line
                                textAlign="center"
                                maxWidth="100%" // Constrain the text width
                            >
                                {header}
                            </Text>
                        </CardHeader>
                        <Text
                            p="6"
                            textAlign="center"
                            fontSize={["4xl", "5xl"]}
                            color="white"
                            height="80px" // Set a fixed height to prevent layout shifts
                            display="flex"
                            alignItems="center" // Center text vertically
                            justifyContent="center" // Center text horizontally
                        >
                            {children}
                        </Text>
                    </VStack>
                </Center>
            </CardBody>
        </Card>
    );
}
