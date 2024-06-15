import ReactJson from "@microlink/react-json-view"

export const skillPlaceholder = {
  url: "https://example.com",
  method: "GET",
  headers: {},
  type: "function",
  function: {
    name: "Enter skill name",
    description: "Enter skill description",
    parameters: {
      type: "object",
      properties: {
        param1: {
          type: "integer",
          description: "Describe this parameter",
        },
        param2: {
          type: "string",
          enum: ["option1"],
          description: "Select from the provided options",
        },
      },
      required: ["param1", "param2"],
    },
  },
}

interface SkillEditorProps {
  value: object
  onChange: (...event: any[]) => void
}

const SkillEditor = ({ value, onChange, ...props }: SkillEditorProps) => {
  return (
    <ReactJson
      {...props}
      style={{ padding: "1rem" }}
      name={"skill"}
      src={value as object}
      theme="monokai"
      iconStyle="circle"
      displayDataTypes={false}
      enableClipboard={false}
      collapsed={4}
      collapseStringsAfterLength={27}
      onEdit={(e) => onChange(e.updated_src)}
      onDelete={(e) => onChange(e.updated_src)}
      onAdd={(e) => onChange(e.updated_src)}
    />
  )
}

export default SkillEditor
