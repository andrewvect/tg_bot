import { Button, Text, VStack } from "@chakra-ui/react";
import { useNavigate } from "@tanstack/react-router";
import BackgroundBox from "./back";
import { AbsoluteCenter } from "@chakra-ui/layout";
import { motion } from "framer-motion";

function AllWordsReviewed() {
    const navigate = useNavigate();

    return (
        <BackgroundBox>
            <AbsoluteCenter>
                <VStack spacing={4}>
                    <motion.div
                        animate={{ scale: [1, 1.1, 1] }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            repeatType: "reverse",
                        }}
                    >
                        <Text fontSize="5xl" color="white" textAlign="center">
                            🥳
                        </Text>

                    </motion.div>
                    <Text fontSize="2xl" color="white" textAlign="center">
                            Все слова повторены!
                        </Text>
                    <Button variant="primary" onClick={() => navigate({ to: '/new' })}>
                        Добавить новые слова
                    </Button>
                </VStack>
            </AbsoluteCenter>
        </BackgroundBox>
    );
}

export default AllWordsReviewed;
