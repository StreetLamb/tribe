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
        interrupt_decision: {
            type: 'any-of',
            contains: [{
                type: 'InterruptDecision',
            }, {
                type: 'null',
            }],
        },
    },
} as const;
