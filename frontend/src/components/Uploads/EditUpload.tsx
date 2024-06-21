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
  type Body_uploads_update_upload,
  type UploadOut,
  UploadsService,
} from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import FileUpload from "../Common/FileUpload"

interface EditUploadProps {
  upload: UploadOut
  isOpen: boolean
  onClose: () => void
}

const EditUpload = ({ upload, isOpen, onClose }: EditUploadProps) => {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { isSubmitting, errors, isDirty, isValid },
  } = useForm<Body_uploads_update_upload>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: upload,
  })

  const updateUpload = async (data: Body_uploads_update_upload) => {
    return await UploadsService.updateUpload({ id: upload.id, formData: data })
  }

  const mutation = useMutation(updateUpload, {
    onSuccess: (data) => {
      showToast("Success!", "Upload updated successfully.", "success")
      reset(data) // reset isDirty after updating
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

  const onSubmit: SubmitHandler<Body_uploads_update_upload> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
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
          <ModalHeader>Edit Upload</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl isInvalid={!!errors.name}>
              <FormLabel htmlFor="name">Name</FormLabel>
              <Input
                id="name"
                {...register("name", {
                  required: "Name is required",
                })}
                type="text"
              />
              {errors.name && (
                <FormErrorMessage>{errors.name.message}</FormErrorMessage>
              )}
            </FormControl>
            <FileUpload
              name="file"
              acceptedFileTypes="application/pdf"
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
              isLoading={isSubmitting}
              isDisabled={!isDirty || !isValid}
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

export default EditUpload
