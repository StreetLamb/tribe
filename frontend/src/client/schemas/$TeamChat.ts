/* generated using openapi-typescript-codegen -- do no edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export const $TeamChat = {
    properties: {
        messages: {
            type: 'array',
            contains: {
                type: 'ChatMessage',
            },
            isRequired: true,
        },
    },
} as const;
