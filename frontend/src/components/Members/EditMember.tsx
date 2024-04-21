import {
  Button,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Select,
  Textarea,
} from "@chakra-ui/react"
import useCustomToast from "../../hooks/useCustomToast"
import { useMutation, useQueryClient } from "react-query"
import {
  type ApiError,
  MembersService,
  type TeamUpdate,
  type MemberOut,
  type MemberUpdate,
} from "../../client"
import { type SubmitHandler, useForm } from "react-hook-form"

interface EditMemberProps {
  member: MemberOut
  teamId: number
  isOpen: boolean
  onClose: () => void
}

export function EditMember({
  member,
  teamId,
  isOpen,
  onClose,
}: EditMemberProps) {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<MemberUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    values: member,
  })

  const updateMember = async (data: MemberUpdate) => {
    await MembersService.updateMember({
      id: member.id,
      teamId: teamId,
      requestBody: data,
    })
  }

  const mutation = useMutation(updateMember, {
    onSuccess: () => {
      showToast("Success!", "Team updated successfully.", "success")
      onClose()
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries(`teams/${teamId}/members`)
    },
  })

  const onSubmit: SubmitHandler<TeamUpdate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay>
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Update Team Member</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isDisabled={member.type === "root"}>
              <FormLabel htmlFor="type">Type</FormLabel>
              <Select id="type" {...register("type")}>
                <option value="member">Worker</option>
                <option value="leader">Leader</option>
                {member.type === "root" && (
                  <option value="root">Team Leader</option>
                )}
              </Select>
            </FormControl>
            <FormControl mt={4} isRequired isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="name"
                {...register("name", {
                  required: "Name is required.",
                  pattern: {
                    value: /^[a-zA-Z0-9_-]{1,64}$/,
                    message: "Name must follow pattern: ^[a-zA-Z0-9_-]{1,64}$",
                  },
                })}
                placeholder="Name"
                type="text"
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl mt={4} isRequired isInvalid={!!errors.role}>
              <FormLabel htmlFor="role">Role</FormLabel>
              <Textarea
                id="role"
                {...register("role", { required: "Role is required." })}
                placeholder="Role"
                className="nodrag nopan"
              />
              {errors.role && (
                <FormErrorMessage>{errors.role.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="backstory">Backstory</FormLabel>
              <Textarea
                id="backstory"
                {...register("backstory")}
                className="nodrag nopan"
              />
            </FormControl>
            {/* TODO: Add ability to select skills */}
            {/* <FormControl mt={4}>
              <FormLabel htmlFor="skills">Skills</FormLabel>
              <MultiSelect
                isMulti
                useBasicStyles
                id="skills"
                {...register("skills")}
                className="nodrag nopan"
                options={[
                  {
                    label: "I am red",
                    value: "i-am-red",
                  },
                  {
                    label: "I fallback to purple",
                    value: "i-am-purple",
                  },
                ]}
                // value={data.role}
              />
            </FormControl> */}
          </ModalBody>
          <ModalFooter gap={3}>
            <Button
              variant="primary"
              type="submit"
              isLoading={isSubmitting}
              isDisabled={!isDirty}
            >
              Save
            </Button>
            <Button onClick={onCancel}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </ModalOverlay>
    </Modal>
  )
}
