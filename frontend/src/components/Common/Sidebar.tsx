import {
  Box,
  Container,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerOverlay,
  Flex,
  IconButton,
  Image,
  Text,
  useColorModeValue,
  useDisclosure,
} from "@chakra-ui/react"
import { FiLogOut, FiMenu } from "react-icons/fi"
import { useQueryClient } from "react-query"

import Logo from "../../assets/images/tribe-logo.png"
import type { UserOut } from "../../client"
import useAuth from "../../hooks/useAuth"
import SidebarItems from "./SidebarItems"

const Sidebar = () => {
  const queryClient = useQueryClient()
  const bgColor = useColorModeValue("ui.white", "ui.dark")
  const textColor = useColorModeValue("ui.dark", "ui.white")
  const secBgColor = useColorModeValue("ui.secondary", "ui.darkSlate")
  const currentUser = queryClient.getQueryData<UserOut>("currentUser")
  const { isOpen, onOpen, onClose } = useDisclosure()
  const { logout } = useAuth()

  const handleLogout = async () => {
    logout()
  }

  return (
    <>
      {/* Mobile */}
      <IconButton
        onClick={onOpen}
        display={{ base: "flex", md: "none" }}
        aria-label="Open Menu"
        position="absolute"
        fontSize="20px"
        m={4}
        icon={<FiMenu />}
      />
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent maxW="250px">
          <DrawerCloseButton />
          <DrawerBody py={8}>
            <Flex flexDir="column" justify="space-between">
              <Box>
                <Image src={Logo} alt="logo" px={6} pt={6} />
                <Container
                  centerContent
                  fontWeight={"bold"}
                  fontSize={"large"}
                  mb={6}
                  color={"#0b4639"}
                >
                  Tribe AI
                </Container>
                <SidebarItems onClose={onClose} />
                <Flex
                  as="button"
                  onClick={handleLogout}
                  p={2}
                  color="ui.danger"
                  fontWeight="bold"
                  alignItems="center"
                >
                  <FiLogOut />
                  <Text ml={2}>Log out</Text>
                </Flex>
              </Box>
              {currentUser?.email && (
                <Text color={textColor} noOfLines={2} fontSize="sm" p={2}>
                  Logged in as: {currentUser.email}
                </Text>
              )}
            </Flex>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Desktop */}
      <Box
        bg={bgColor}
        p={3}
        h="100vh"
        position="sticky"
        top="0"
        display={{ base: "none", md: "flex" }}
      >
        <Flex
          flexDir="column"
          justify="space-between"
          bg={secBgColor}
          p={4}
          borderRadius={12}
        >
          <Box>
            <Image src={Logo} alt="Logo" w="180px" maxW="4xs" px={6} pt={6} />
            <Container
              centerContent
              fontWeight={"bold"}
              fontSize={"large"}
              mb={6}
            >
              Tribe AI
            </Container>
            <SidebarItems />
          </Box>
          {currentUser?.email && (
            <Text
              color={textColor}
              noOfLines={2}
              fontSize="sm"
              p={2}
              maxW="180px"
            >
              Logged in as: {currentUser.email}
            </Text>
          )}
        </Flex>
      </Box>
    </>
  )
}

export default Sidebar
