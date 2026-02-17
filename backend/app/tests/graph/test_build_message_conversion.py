from app.core.graph.build import chat_message_to_human_message
from app.models import (
    ChatContentFileData,
    ChatContentFilePart,
    ChatContentImageData,
    ChatContentImagePart,
    ChatContentTextPart,
    ChatMessage,
    ChatMessageType,
)


def test_chat_message_to_human_message_with_string_content() -> None:
    message = ChatMessage(type=ChatMessageType.human, content="hello")

    result = chat_message_to_human_message(message)

    assert result.content == "hello"
    assert result.additional_kwargs == {}


def test_chat_message_to_human_message_with_multipart_content() -> None:
    message = ChatMessage(
        type=ChatMessageType.human,
        content=[
            ChatContentTextPart(type="text", text="Describe this"),
            ChatContentImagePart(
                type="image_url",
                image_url=ChatContentImageData(url="data:image/png;base64,AAA"),
            ),
            ChatContentFilePart(
                type="file",
                file=ChatContentFileData(
                    file_id="file-123",
                    filename="report.pdf",
                    file_data="data:application/pdf;base64,BBB",
                ),
            ),
        ],
    )

    result = chat_message_to_human_message(message)

    assert isinstance(result.content, list)
    assert result.content[0] == {"type": "text", "text": "Describe this"}
    assert result.content[1] == {
        "type": "image_url",
        "image_url": {"url": "data:image/png;base64,AAA"},
    }
    content_parts = result.content
    assert isinstance(content_parts, list)
    third_part = content_parts[2]
    assert isinstance(third_part, dict)
    assert third_part == {"type": "text", "text": "[Attached file: report.pdf]"}
    assert result.additional_kwargs["attachments"] == ["file-123"]
