import {
  Button,
  FormControl,
  FormErrorMessage,
  FormHelperText,
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
} from "@chakra-ui/react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useMutation, useQueryClient } from "react-query"

import { type ApiError, type TeamCreate, TeamsService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"

interface AddTeamProps {
  isOpen: boolean
  onClose: () => void
}

const AddTeam = ({ isOpen, onClose }: AddTeamProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isValid },
  } = useForm<TeamCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
      description: "",
    },
  })

  const addTeam = async (data: TeamCreate) => {
    await TeamsService.createTeam({ requestBody: data })
  }

  const mutation = useMutation(addTeam, {
    onSuccess: () => {
      showToast("Success!", "Team created successfully.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries("teams")
    },
  })

  const onSubmit: SubmitHandler<TeamCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "sm", md: "md" }}
        isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Add Team</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="title"
                {...register("name", {
                  required: "Title is required.",
                  pattern: {
                    value: /^[a-zA-Z0-9_-]{1,64}$/,
                    message: "Name must follow pattern: ^[a-zA-Z0-9_-]{1,64}$",
                  },
                })}
                placeholder="Title"
                type="text"
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>
            <FormControl mt={4}>
              <FormLabel htmlFor="description">Description</FormLabel>
              <Input
                id="description"
                {...register("description")}
                placeholder="Description"
                type="text"
              />
            </FormControl>
            <FormControl isRequired mt={4}>
              <FormLabel htmlFor="description">Workflow</FormLabel>
              <Select
                id="workflow"
                {...register("workflow", { required: true })}
              >
                <option value="hierarchical">Hierarchical</option>
                <option value="sequential">Sequential</option>
              </Select>
              <FormHelperText>
                You cannot change workflow after creation.
              </FormHelperText>
            </FormControl>
          </ModalBody>

          <ModalFooter gap={3}>
            <Button
              variant="primary"
              type="submit"
              isLoading={isSubmitting}
              isDisabled={!isValid}
            >
              Save
            </Button>
            <Button onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}

export default AddTeam
