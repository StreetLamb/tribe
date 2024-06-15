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
} from "@chakra-ui/react"
import { type SubmitHandler, useForm, Controller } from "react-hook-form"

import { useMutation, useQueryClient } from "react-query"
import {
  type ApiError,
  type SkillOut,
  type SkillUpdate,
  SkillsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import SkillEditor, { skillPlaceholder } from "./SkillEditor"

interface EditSkillProps {
  skill: SkillOut
  isOpen: boolean
  onClose: () => void
}

const EditSkill = ({ skill, isOpen, onClose }: EditSkillProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    control,
    setValue,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<SkillUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: skill,
  })

  const updateSkill = async (data: SkillUpdate) => {
    await SkillsService.updateSkill({ id: skill.id, requestBody: data })
  }

  const mutation = useMutation(updateSkill, {
    onSuccess: () => {
      showToast("Success!", "Skill updated successfully.", "success")
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

  const onSubmit: SubmitHandler<SkillUpdate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
  }

  const prefillHandler = () => {
    setValue("tool_definition", skillPlaceholder)
  }

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        size={{ base: "sm", md: "md", lg: "lg" }}
        // size="full"
        // isCentered
      >
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Edit Skill</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="name"
                {...register("name", {
                  required: "Name is required",
                  pattern: {
                    value: /^[a-zA-Z0-9_-]{1,64}$/,
                    message: "Name must follow pattern: ^[a-zA-Z0-9_-]{1,64}$",
                  },
                })}
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
            <Controller
              control={control}
              name="tool_definition"
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <FormControl mt={4}>
                  <FormLabel htmlFor="tool_definition">
                    Skill Definition
                  </FormLabel>
                  <SkillEditor onChange={onChange} value={value as object} />
                  <FormErrorMessage>{error?.message}</FormErrorMessage>
                  <Button mt={2} onClick={prefillHandler}>
                    Pre-fill
                  </Button>
                </FormControl>
              )}
            />
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
      </Modal>
    </>
  )
}

export default EditSkill
