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
            <Box width={"100vw"} height="100vh" bg={bg}>
                {children}
            </Box>
        </Center>
    );
}
