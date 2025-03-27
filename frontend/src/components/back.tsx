import { Box, Center } from "@chakra-ui/react";
import React from "react";


export default function BackgroundBox({
    children,
    bg = "black"
}: {
    children: React.ReactNode;
    bg?: string;
}) {
    return (
        <Center>
            <Box w={["100%", "430px"]} minH={["100vh", "932px"]} bg={bg}>
                {children}
            </Box>
        </Center>
    );
}
