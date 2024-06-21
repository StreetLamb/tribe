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
import { type SubmitHandler, useForm } from "react-hook-form"
import { useMutation, useQueryClient } from "react-query"

import {
  type ApiError,
  UploadsService,
  type Body_uploads_create_upload,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import FileUpload from "../Common/FileUpload"

interface AddUploadProps {
  isOpen: boolean
  onClose: () => void
}

const AddUpload = ({ isOpen, onClose }: AddUploadProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isSubmitting, isValid },
  } = useForm<Body_uploads_create_upload>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      name: "",
    },
  })

  const addUpload = async (data: Body_uploads_create_upload) => {
    await UploadsService.createUpload({ formData: data })
  }

  const mutation = useMutation(addUpload, {
    onSuccess: () => {
      showToast("Success!", "Upload created successfully.", "success")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      const errDetail = err.body?.detail
      showToast("Something went wrong.", `${errDetail}`, "error")
    },
    onSettled: () => {
      queryClient.invalidateQueries("uploads")
    },
  })

  const onSubmit: SubmitHandler<Body_uploads_create_upload> = (data) => {
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
          <ModalHeader>Add Upload</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isRequired isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="title"
                {...register("name", {
                  required: "Title is required.",
                })}
                placeholder="Title"
                type="text"
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>
            <FileUpload
              name="file"
              acceptedFileTypes="application/pdf"
              isRequired={true}
              placeholder="Your file"
              control={control}
            >
              Upload File
            </FileUpload>
          </ModalBody>
          <ModalFooter gap={3}>
            <Button
              variant="primary"
              type="submit"
              isLoading={isSubmitting || mutation.isLoading}
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

export default AddUpload
