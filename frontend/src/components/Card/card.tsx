import { Card, CardBody, CardHeader, Text, Center, VStack } from "@chakra-ui/react";
import { React } from "react";

interface CardComponentProps {
    header: string;
    children: React.ReactNode;
}

export function CardComponent({ header, children }: CardComponentProps) {
    const headerLength = header.length;
    const childrenLength = children.toString().length;

    return (
        <Card backgroundColor="black">
            <CardBody gap={0} padding={0} width="100%">
                <Center>
                    <VStack width="100%" height="100%">
                        <CardHeader gap={0} padding={0} width="100%">
                            <Text
                                fontSize={`clamp(35px, calc(80vw / ${headerLength}), 70px)`}
                                fontWeight="bold"
                                color="white"
                                isTruncated={false}
                                whiteSpace="nowrap"
                                textOverflow="ellipsis"
                                overflow="hidden"
                                width="100%" // Take full width of parent
                                textAlign="center"
                                display="flex"
                                justifyContent="center" // Center content horizontally
                            >
                                {header}
                            </Text>
                        </CardHeader>
                        <Text
                            textAlign="center"
                            fontSize={`clamp(30px, calc(60vw / ${childrenLength}), 60px)`}// Adjusts font size based on header length
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
