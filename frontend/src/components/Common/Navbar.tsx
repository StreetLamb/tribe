import { Button, Flex, Icon, useDisclosure } from "@chakra-ui/react"
import { FaPlus } from "react-icons/fa"

import AddUser from "../Admin/AddUser"
import AddTeam from "../Teams/AddTeam"
import AddSkill from "../Skills/AddSkill"

interface NavbarProps {
  type: string
}

const Navbar = ({ type }: NavbarProps) => {
  const addUserModal = useDisclosure()
  const addTeamModal = useDisclosure()
  const addSkillModal = useDisclosure()

  return (
    <>
      <Flex py={8} gap={4}>
        {/* TODO: Complete search functionality */}
        {/* <InputGroup w={{ base: '100%', md: 'auto' }}>
                    <InputLeftElement pointerEvents='none'>
                        <Icon as={FaSearch} color='gray.400' />
                    </InputLeftElement>
                    <Input type='text' placeholder='Search' fontSize={{ base: 'sm', md: 'inherit' }} borderRadius='8px' />
                </InputGroup> */}
        <Button
          variant="primary"
          gap={1}
          fontSize={{ base: "sm", md: "inherit" }}
          onClick={
            type === "User"
              ? addUserModal.onOpen
              : type === "Team"
                ? addTeamModal.onOpen
                : addSkillModal.onOpen
          }
        >
          <Icon as={FaPlus} /> Add {type}
        </Button>
        <AddUser isOpen={addUserModal.isOpen} onClose={addUserModal.onClose} />
        <AddTeam isOpen={addTeamModal.isOpen} onClose={addTeamModal.onClose} />
        <AddSkill
          isOpen={addSkillModal.isOpen}
          onClose={addSkillModal.onClose}
        />
      </Flex>
    </>
  )
}

export default Navbar
