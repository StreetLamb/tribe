import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import {
  Box,
  Flex,
  Text,
  useColorMode,
  useColorModeValue,
} from "@chakra-ui/react";
import CopyButton from "./CopyButton";
import { FiTerminal } from "react-icons/fi";
import { v4 } from "uuid";
import { useEffect } from "react";

const Markdown = ({ content }: { content: string }) => {
  const textColor = useColorModeValue("ui.dark", "ui.white");
  const secBgColor = useColorModeValue("ui.secondary", "ui.darkSlate");
  const { colorMode } = useColorMode();

  useEffect(() => {
  const loadMarkdownCSSStyle = async () => {
    if (colorMode === "dark") {
      await import("highlight.js/styles/github-dark.css");
    } else {
      await import("highlight.js/styles/github.css");
    }
  };
  loadMarkdownCSSStyle();
}, [colorMode]);

  return (
    <ReactMarkdown
      rehypePlugins={[rehypeHighlight]}
      components={{
        pre: ({ children }) => (
          <Box as="pre" overflow="auto">
            {children}
          </Box>
        ),
        code: ({ node, className, children, ...props }) => {
          const matchedLanguage = /language-(\w+)/.exec(className || "");
          if (matchedLanguage?.length) {
            const id = v4();
            return (
              <Box borderWidth="1px" borderRadius="md" overflow="hidden" my={2}>
                <Flex
                  align="center"
                  justify="space-between"
                  bg={secBgColor}
                  p={1}
                  borderBottomWidth="1px"
                >
                  <Flex align="center" gap={2}>
                    <FiTerminal size={18} />
                    <Text
                      fontSize="md"
                      color={textColor}
                      fontWeight={"bold"}
                      ml={2}
                    >
                      {matchedLanguage[1]}
                    </Text>
                  </Flex>
                  <CopyButton id={id} />
                </Flex>
                <Box
                  as="pre"
                  id={id}
                  p={2}
                  overflowX="auto"
                  whiteSpace="pre-wrap"
                >
                  <Box
                    as="code"
                    backgroundColor={secBgColor}
                    className={className}
                    {...props}
                  >
                    {children}
                  </Box>
                </Box>
              </Box>
            );
          } else {
            return (
              <Box
                as="code"
                {...props}
                bg={secBgColor}
                px={2}
                borderRadius="md"
              >
                {children}
              </Box>
            );
          }
        },
      }}
      className="prose prose-zinc max-w-2xl dark:prose-invert"
    >
      {content}
    </ReactMarkdown>
  );
};

export default Markdown;
