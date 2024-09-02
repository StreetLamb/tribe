import {
  Button,
  Checkbox,
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
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Textarea,
  Tooltip,
} from "@chakra-ui/react"
import useCustomToast from "../../hooks/useCustomToast"
import { useMutation, useQuery, useQueryClient } from "react-query"
import {
  type ApiError,
  MembersService,
  type TeamUpdate,
  type MemberOut,
  type MemberUpdate,
  SkillsService,
  UploadsService,
} from "../../client"
import { type SubmitHandler, useForm, Controller } from "react-hook-form"
import {
  Select as MultiSelect,
  chakraComponents,
  CreatableSelect,
  type OptionBase,
} from "chakra-react-select"
import { useState } from "react"

interface EditMemberProps {
  member: MemberOut
  teamId: number
  isOpen: boolean
  onClose: () => void
}

interface ModelOption extends OptionBase {
  label: string
  value: string
}

type MemberTypes = "root" | "leader" | "worker" | "freelancer" | "freelancer_root"

interface MemberConfigs {
  selection: MemberTypes[],
  enableTools: boolean,
  enableInterrupt: boolean,
  enableHumanTool: boolean
}

const customSelectOption = {
  Option: (props: any) => (
    <chakraComponents.Option {...props}>
      {props.children}: {props.data.description}
    </chakraComponents.Option>
  ),
}

// TODO: Place this somewhere else.
const AVAILABLE_MODELS = {
  openai: ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
  anthropic: [
    "claude-3-haiku-20240307",
    "claude-3-sonnet-20240229",
    "claude-3-opus-20240229",
  ],
  ollama: ["llama3.1"],
}

const ALLOWED_MEMBER_CONFIGS:  Record<MemberTypes, MemberConfigs> = {
  root: {
    selection: ["root"],
    enableTools: false,
    enableInterrupt: false,
    enableHumanTool: false,
  },
  leader: {
    selection: ["worker", "leader"],
    enableTools: false,
    enableInterrupt: false,
    enableHumanTool: false,
  },
  worker: {
    selection: ["worker", "leader"],
    enableTools: true,
    enableInterrupt: false,
    enableHumanTool: false,
  },
  freelancer: {
    selection: ["freelancer"],
    enableTools: true,
    enableInterrupt: true,
    enableHumanTool: true,
  },
  freelancer_root: {
    selection: ["freelancer_root"],
    enableTools: true,
    enableInterrupt: true,
    enableHumanTool: true,
  },
}

type ModelProvider = keyof typeof AVAILABLE_MODELS

export function EditMember({
  member,
  teamId,
  isOpen,
  onClose,
}: EditMemberProps) {
  const queryClient = useQueryClient()
  const showToast = useCustomToast()
  const [showTooltip, setShowTooltip] = useState(false)
  const {
    data: skills,
    isLoading: isLoadingSkills,
    isError: isErrorSkills,
    error: errorSkills,
  } = useQuery("skills", () => SkillsService.readSkills({}))
  const {
    data: uploads,
    isLoading: isLoadingUploads,
    isError: isErrorUploads,
    error: errorUploads,
  } = useQuery("uploads", () =>
    UploadsService.readUploads({ status: "Completed" }),
  )

  if (isErrorSkills || isErrorUploads) {
    const error = errorSkills || errorUploads
    const errDetail = (error as ApiError).body?.detail
    showToast("Something went wrong.", `${errDetail}`, "error")
  }

  const {
    register,
    handleSubmit,
    reset,
    control,
    watch,
    setValue,
    formState: { isSubmitting, errors, isDirty, isValid },
  } = useForm<MemberUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    values: {
      ...member,
      skills: member.skills.map((skill) => ({
        ...skill,
        label: skill.name,
        value: skill.id,
      })),
      uploads: member.uploads.map((upload) => ({
        ...upload,
        label: upload.name,
        value: upload.id,
      })),
    },
  })

  const updateMember = async (data: MemberUpdate) => {
    return await MembersService.updateMember({
      id: member.id,
      teamId: teamId,
      requestBody: data,
    })
  }

  const mutation = useMutation(updateMember, {
    onSuccess: (data) => {
      showToast("Success!", "Team updated successfully.", "success")
      reset(data) // reset isDirty after updating
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

  const memberConfig = ALLOWED_MEMBER_CONFIGS[ watch("type") as MemberTypes]

  const skillOptions = skills
  ? skills.data
      // Remove 'ask-human' tool if 'enableHumanTool' is false
      .filter((skill) => skill.name !== "ask-human" || memberConfig.enableHumanTool)
      .map((skill) => ({
        ...skill,
        label: skill.name,
        value: skill.id,
      }))
  : []

  const uploadOptions = uploads
    ? uploads.data.map((upload) => ({
        ...upload,
        label: upload.name,
        value: upload.id,
      }))
    : []

  const modelProvider = watch("provider") as ModelProvider
  const modelOptions: ModelOption[] = (AVAILABLE_MODELS[modelProvider] ?? []).map(
    (model) => ({
      label: model,
      value: model,
    }),
  )

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay>
        <ModalContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <ModalHeader>Update Team Member</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <FormControl
              isDisabled={
                member.type === "root" || member.type.startsWith("freelancer")
              }
            >
              <FormLabel htmlFor="type">Type</FormLabel>
              <Select id="type" {...register("type")}>
                {memberConfig.selection.map((member, index) => (<option key={index} value={member}>{member}</option>))}
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
            <Controller
              control={control}
              name="skills"
              render={({
                field: { onChange, onBlur, value, name, ref },
                fieldState: { error },
              }) => (
                <FormControl mt={4} isInvalid={!!error} id="skills">
                  <FormLabel>Skills</FormLabel>
                  <MultiSelect
                    isDisabled={!memberConfig.enableTools}
                    isLoading={isLoadingSkills}
                    isMulti
                    name={name}
                    ref={ref}
                    onChange={onChange}
                    onBlur={onBlur}
                    value={value}
                    options={skillOptions}
                    placeholder="Select skills"
                    closeMenuOnSelect={false}
                    components={customSelectOption}
                  />
                  <FormErrorMessage>{error?.message}</FormErrorMessage>
                </FormControl>
              )}
            />
            <Controller
              control={control}
              name="uploads"
              render={({
                field: { onChange, onBlur, value, name, ref },
                fieldState: { error },
              }) => (
                <FormControl mt={4} isInvalid={!!error} id="uploads">
                  <FormLabel>Knowledge Base</FormLabel>
                  <MultiSelect
                    isDisabled={!memberConfig.enableTools}
                    isLoading={isLoadingUploads}
                    isMulti
                    name={name}
                    ref={ref}
                    onChange={onChange}
                    onBlur={onBlur}
                    value={value}
                    options={uploadOptions}
                    placeholder="Select uploads"
                    closeMenuOnSelect={false}
                    components={customSelectOption}
                  />
                  <FormErrorMessage>{error?.message}</FormErrorMessage>
                </FormControl>
              )}
            />
            {memberConfig.enableInterrupt && (
              <FormControl mt={4}>
                <FormLabel htmlFor="interrupt">Human In The Loop</FormLabel>
                <Checkbox {...register("interrupt")}>
                  Require approval before executing actions
                </Checkbox>
              </FormControl>
            )}
            <FormControl mt={4} isRequired isInvalid={!!errors.provider}>
              <FormLabel htmlFor="provider">Provider</FormLabel>
              <Select
                id="provider"
                {...register("provider", {
                  required: true,
                  onChange: (event) =>
                    setValue(
                      "model",
                      AVAILABLE_MODELS[event.target.value as ModelProvider][0],
                    ),
                })}
              >
                {Object.keys(AVAILABLE_MODELS).map((provider, index) => (
                  <option key={index} value={provider}>
                    {provider}
                  </option>
                ))}
              </Select>
            </FormControl>
            <Controller
              control={control}
              name="model"
              render={({
                field: { onChange, onBlur, value, name, ref },
                fieldState: { error },
              }) => {
                return (
                  <FormControl mt={4} isRequired isInvalid={!!error}>
                    <FormLabel htmlFor="model">Model</FormLabel>
                    <CreatableSelect
                      id="model"
                      name={name}
                      ref={ref}
                      onChange={(newValue) => onChange(newValue?.value)}
                      onBlur={onBlur}
                      value={{ value: value, label: value }}
                      options={modelOptions}
                      useBasicStyles
                    />
                    <FormHelperText>
                      If a model is not listed, you can type it in.
                    </FormHelperText>
                  </FormControl>
                )
              }}
            />
            {(modelProvider === "openai" || modelProvider === "ollama") && (
              <FormControl mt={4} isInvalid={!!errors.base_url}>
                <FormLabel htmlFor="model">Proxy Provider</FormLabel>
                <Input
                  id="base_url"
                  {...register("base_url")}
                  placeholder="Base URL"
                />
                {modelProvider === "ollama" && (
                  <FormHelperText>
                    Default url: http://host.docker.internal:11434
                  </FormHelperText>
                )}
              </FormControl>
            )}
            <Controller
              control={control}
              name="temperature"
              rules={{ required: true }}
              render={({
                field: { onChange, onBlur, value, name, ref },
                fieldState: { error },
              }) => (
                <FormControl mt={4} isRequired isInvalid={!!error}>
                  <FormLabel htmlFor="temperature">Temperature</FormLabel>
                  <Slider
                    id="temperature"
                    name={name}
                    value={value ?? 0} // Use nullish coalescing to ensure value is never null
                    onChange={onChange}
                    onBlur={onBlur}
                    ref={ref}
                    min={0}
                    max={1}
                    step={0.1}
                    onMouseEnter={() => setShowTooltip(true)}
                    onMouseLeave={() => setShowTooltip(false)}
                  >
                    <SliderTrack>
                      <SliderFilledTrack />
                    </SliderTrack>
                    <Tooltip
                      hasArrow
                      placement="top"
                      isOpen={showTooltip}
                      label={watch("temperature")}
                    >
                      <SliderThumb />
                    </Tooltip>
                  </Slider>
                  <FormErrorMessage>{error?.message}</FormErrorMessage>
                </FormControl>
              )}
            />
          </ModalBody>
          <ModalFooter gap={3}>
            <Button
              variant="primary"
              type="submit"
              isLoading={isSubmitting || mutation.isLoading}
              isDisabled={!isDirty || !isValid}
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
