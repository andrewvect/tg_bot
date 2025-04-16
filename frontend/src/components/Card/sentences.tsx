import React from 'react';
import { List, ListItem, ListIcon, Text, Box } from '@chakra-ui/react';
import { CheckCircleIcon } from '@chakra-ui/icons';
import { WordResponse } from '../../client/types.gen';

interface SentencesProps {
    sentences: WordResponse['sentences'];
    alphabetSettings: number | null;
}

const Sentences: React.FC<SentencesProps> = ({ sentences, alphabetSettings }) => {
    if (!sentences) return null;

    const formatTextWithBold = (text: string) => {
        // Split by ** markers
        const parts = text.split(/\*\*/);

        return (
            <>
                {parts.map((part, index) => {
                    // Even indices are regular text, odd indices are bold text
                    return index % 2 === 0 ?
                        part :
                        <Text as="span" fontWeight="bold" key={index}>{part}</Text>;
                })}
            </>
        );
    };

    return (
        <Box>
        <Text fontSize="xs" mb={2}>
            Пример использования:
        </Text>
        <List spacing={3}>
            {sentences.map((sentence) => (
                <ListItem key={sentence.id}>
                    <ListIcon as={CheckCircleIcon} color="green.500" />
                    <Box>
                        <Text>{formatTextWithBold(sentence.native_text)}</Text>
                        <Box height="0.5vh"></Box>

                        {/* Show text based on alphabet settings */}
                        {(alphabetSettings === null) && (
                            <>
                                <Text>{formatTextWithBold(sentence.cyrilic_text)}</Text>
                                <Text>{formatTextWithBold(sentence.latin_text)}</Text>
                            </>
                        )}

                        {(alphabetSettings === 3) && (
                            <Text>{formatTextWithBold(sentence.latin_text)}</Text>
                        )}

                        {(alphabetSettings === 2) && (
                            <Text>{formatTextWithBold(sentence.cyrilic_text)}</Text>
                        )}
                    </Box>
                </ListItem>
            ))}
        </List>
        </Box>
    );
};

export default Sentences;
